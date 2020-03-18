import pandas as pd
from read_sheet import retrieve_eclipsers
import os

from astroplan import Observer, FixedTarget, is_observable
from astroplan import (AltitudeConstraint, AirmassConstraint,
                       AtNightConstraint)
from astropy.time import Time
import astropy.units as u
from astropy.coordinates import SkyCoord, Angle
import argparse


def construct_plan(data, site, start_time, end_time, constraints=None, max_priority=3):
    if constraints is None:
        constraints = [AltitudeConstraint(10*u.deg, 80*u.deg),
                    AirmassConstraint(5), AtNightConstraint.twilight_civil()]

    data = data.sort_values(by=["Add. Data Priority", "RA"], ascending=[1,1])

    time_range = Time([start_time, end_time])

    # targets.lis format:
    # NAME
    # <RA hh:mm:ss.ss> <DEC dd:mm:ss.s>
    # <HMJD/BMJD T0 err P err
    #
    # NAME...
    # ENTRY = "{}\n{} {}\n{} linear {} {} {} {}\n\n"
    targets_list = ""
    targets_prg = ""
    targets_notes = ""
    for name, row in data.iterrows():
        row['RA'], row['Dec'] = row['RA'].replace(" ", ":"), row['Dec'].replace(" ", ":")

        target = FixedTarget(
            coord=SkyCoord(
                ra=Angle(row['RA'], unit='hourangle'),
                dec=Angle(row['Dec'], unit='degree')
            ),
            name=name
        )

        # Does the target rise above the horizon?
        ever_observable = is_observable(constraints, site, target, time_range=time_range)

        # Parse the ephemeris data
        try:
            T0, T0_err = row['T(0) +/- (d)'].replace(" ", "").split("(")
            calendar, T0 = T0.split("=")
            T0_err = T0_err.replace(")", "")

            N = len(T0.split(".")[1]) - len(T0_err)
            T0_err = "0.{}{}".format(
                ("0" * N), T0_err
            )

            P, P_err = row['P +/- (d)'].split("(")
            P_err = P_err.replace(")", "")

            M = len(P.split(".")[1]) - len(P_err)
            P_err = "0.{}{}".format(
                ("0" * M), P_err
            )
        except ValueError:
            print("Failed to extract row! {}".format(name))
            continue

        # Get the priority of this system
        try:
            priority = int(row['Add. Data Priority'])
        except ValueError:
            continue

        # Logic about if we want to use this target
        writeme = ever_observable[0] and (priority <= max_priority)

        # If true, add to the list
        if writeme:
            # Output data formats
            line = "{}\n{} {}\n{} linear {} {} {} {}\n\n".format(
                name,
                row['RA'], row['Dec'],
                calendar,
                T0, T0_err, P, P_err
            )
            prgline = "{}\n0.7 1.3 3 8\n\n".format(name)
            notesline = '{}: "{}"\n\n\n'.format(name, row['Target Notes'])

            targets_list += line
            targets_prg += prgline
            targets_notes += notesline

    # Write out files
    with open(os.path.join('OUTPUT', 'targets.lis'), 'w') as f:
        f.write(targets_list)
    with open(os.path.join('OUTPUT', 'targets.prg'), 'w') as f:
        f.write(targets_prg)
    with open(os.path.join('OUTPUT', 'targets.txt'), 'w') as f:
        f.write(targets_notes)


if __name__ in "__main__":
    desc = 'Fetches this google sheet (https://docs.google.com/spreadsheets/d/1JoJLFKagPb1VS-ey_VkaBCfZV9vQFAYIM68APxYUrVU) and gets a list of observable CVs'
    parser = argparse.ArgumentParser("CV eplanner schedule builder", description=desc)

    parser.add_argument(
        'site', help='Observing site. "tnt", or parsable by astropy'
    )
    parser.add_argument(
        '--priority',
        help='Maximum priority to include. Default=1',
        default=1,
        type=int,
    )

    args = parser.parse_args()
    site = args.site

    data = retrieve_eclipsers()

    if site.lower() == 'tnt':
        site = Observer(latitude="18.59056",longitude="98.48656", elevation=2457.0*u.m, name='TNT')
    else:
        site = Observer.at_site(site)

    start, stop = Time.now(), Time.now()+1

    construct_plan(data, site, start, stop, max_priority=args.priority)

