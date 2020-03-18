# CV Scheduler


I want to do the following:
  - Take the sheet of EclipsingCVs
  - Take an observing site (i.e., TNT, La Palma, La Silla)
  - For each star in the list:
    - Extract RA, Dec, P, T0 from the row
    - Calculate if that star is visible that night from that place
    - If it is, put it to one side
  - Construct a `targets.lis`, `targets.prg` file
  - Construct a companion CSV file, `targets.txt` containing:
    - Name
    - RA, Dec
    - g' magnitude
    - New data priority
    - Notes

Sheets has an API, but in order to access it you need to enable it on your google account.
Go [here](https://gspread.readthedocs.io/en/latest/oauth2.html) and get your
signed credentials file. Add it to this directory.

Also, pip install the required thing:

```
pip3 install --upgrade gspread oauth2client PyOpenSSL
```

This library is somehow way nicer than the one google provides.


