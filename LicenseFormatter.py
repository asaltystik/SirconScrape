# we want to open a csv file and read the data in it
import pandas as pd
import os
import datetime

# open the csv file
path = os.path.join(os.getcwd(), 'License.csv')

# read the csv file while only keep the 1st, 3rd, 5th, 6th, columns
data = pd.read_csv(path, usecols=[0, 2, 4, 5])
# Label the columns
data.columns = ['Name', 'State', 'License Number', 'Expiration Date']

# reformat the expiration date from year-month-day to mm/dd/yyyy
data['Expiration Date'] = pd.to_datetime(data['Expiration Date']).dt.strftime('%m/%d/%Y')

# Get todays date in mm/dd/yyyy format
today = datetime.datetime.now().strftime('%m/%d/%Y')

data = data[data['Expiration Date'] > today]

print(data)

# Dictionary of Names to Agent Names
agent_ids = {
    'SECURE CARE 65, LLC': 'admin',
    'AARON MODUGNO': 'aaronM',
    'AUSTEN LEE': 'austenL',
    'CHASE TARWACKI': 'chaseT',
    'CAROL THORN': 'carolT',
    'EVAN GAGE': 'evanG',
    'HEATHER SHOWALTER': 'heatherS',
    'JOSEPH WRIGHT': 'josephW',
    'JOSEPHINE WALKER': 'josephineW',
    'KELLY LUCE': 'kellyL',
    'KRISTIN DECAILLY': 'kristinD',
    'LANDON GAGE': 'landonG',
    'LAURA BUTLER': 'lauraB',
    'LISA STULTS': 'lisaS',
    'LISA YEAZELL': 'lisaY',
    'MARCELO POLAR': 'marceloP',
    'MARK LEE': 'markL',
    'MYRON HAGINS': 'myronH',
    'RHONDA LHOMMEDIEU': 'rhondaL',
    'SAMUEL DORRANCE': 'samuelD',
    'SAMUEL FARLEY': 'samuelF',
    'SKYLA DAVIS': 'skylaD',
    'STEVEN WILLIAMSON': 'stevenW',
    'TYLER KEOGH': 'tylerK',
}
stateABV = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}

# lets replace the names with the agent names
data['Name'] = data['Name'].replace(agent_ids)
data['State'] = data['State'].replace(stateABV)

print(data)
# save the data to a new csv file
data.to_csv('CleanedLicense.csv', index=False)