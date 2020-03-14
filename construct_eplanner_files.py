import pandas as pd
from read_sheet import retrieve_eclipsers
import os

from astroplan import Observer, FixedTarget, is_observable
from astroplan import (AltitudeConstraint, AirmassConstraint,
                       AtNightConstraint)
from astropy.time import Time
import astropy.units as u
from astropy.coordinates import SkyCoord, Angle


data = retrieve_eclipsers()
site = Observer(latitude="18.59056",longitude="98.48656", elevation=2457.0*u.m, name='TNT')
time_range = Time([Time.now(), Time.now()+1])

constraints = [AltitudeConstraint(10*u.deg, 80*u.deg),
               AirmassConstraint(5), AtNightConstraint.twilight_civil()]

# NAME
# <RA hh:mm:ss.ss> <DEC dd:mm:ss.s>
# <HMJD/BMJD T0 err P err
#
# NAME...
# ENTRY = "{}\n{} {}\n{} linear {} {} {} {}\n\n"
targets_list = ""
targets_prg = ""
for name, row in data.iterrows():
    row['RA'], row['Dec'] = row['RA'].replace(" ", ":"), row['Dec'].replace(" ", ":")

    target = FixedTarget(
        coord=SkyCoord(
            ra=Angle(row['RA'], unit='hourangle'),
            dec=Angle(row['Dec'], unit='degree')
        ),
        name=name
    )

    ever_observable = is_observable(constraints, site, target, time_range=time_range)

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

    # Output data formats
    line = "{}\n{} {}\n{} linear {} {} {} {}\n\n".format(
        name,
        row['RA'], row['Dec'],
        calendar,
        T0, T0_err, P, P_err
    )
    prgline = "{}\n0.7 1.3 3 8\n\n".format(name)

    # If they're observable, add to the list
    if ever_observable[0]:
        targets_list += line
        targets_prg += prgline


with open(os.path.join('OUTPUT', 'targets.lis'), 'w') as f:
    f.write(targets_list)
with open(os.path.join('OUTPUT', 'targets.prg'), 'w') as f:
    f.write(targets_prg)
