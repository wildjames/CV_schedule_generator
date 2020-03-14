import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# This is the ID of the eclipsingCVs spreadsheet
sheet_url = 'https://docs.google.com/spreadsheets/d/1JoJLFKagPb1VS-ey_VkaBCfZV9vQFAYIM68APxYUrVU/edit#gid=0'

# I have literally no idea what these are. Endpoints, I guess, but why two of them?
SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# Set up a connection to google
google_cred = ServiceAccountCredentials.from_json_keyfile_name(
    'eclipsingcvs-af8392796a31.json', SCOPE
)
conn = gspread.authorize(google_cred)

# Grab the spreadsheet, and the relevant sheet
database = conn.open_by_url(sheet_url)
sheet = database.sheet1.get_all_values()

# Retrieve the column headers
headers = sheet.pop(0)

df = pd.DataFrame(sheet, columns=headers)

print(df.head())
df.to_csv("eclipsingCVs.csv")
