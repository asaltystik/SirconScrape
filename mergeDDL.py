# This script will be responsible for merging the several sheets from an excel file into a single sheet.
# imports
import pandas as pd
import os
import time

# get the file
file = 'AETNA_DDL.xlsx'

# read the file
xl = pd.ExcelFile(file)

# get the sheet names
sheet_names = xl.sheet_names

# Create the merged dataframe
merged_df = pd.DataFrame(columns=['Drug Name', 'Condition', 'is_accepted'])

# loop through the sheets
for sheet_name in sheet_names:
    # read the sheet the first row is not the header, so wee need to include the header=None
    df = pd.read_excel(file, sheet_name=sheet_name, header=None)
    # loop through the rows
    for index, row in df.iterrows():
        # Check if the 1st column for that row contains the "Drug Name" in the string
        # if it does, split the string by "Drug Name " and grab the 2nd part
        if 'Drug Name' in str(row[0]):
            # Check if the column contains "Drug Name                 Condition"
            # if it does, skip over that row
            if 'Condition' in str(row[0]):
                continue
            # if the string only contains "Drug Name" then we can skip this row too
            if 'Drug Name' == str(row[0]):
                continue
            drug_name = row[0].split('Drug Name ')[1]
        else:
            drug_name = row[0]
        # check if the 2nd Column strarts with "Condition"
        # if it does, split the string by "Condition " and grab the 2nd part
        if str(row[1]).startswith('Condition '):
            condition = row[1].split('Condition ')[1]
        else:
            condition = row[1]
        # Grab the 3rd column for that row
        is_accepted = row[2]
        # Append the row to the merged dataframe
        merged_df = merged_df._append({'Drug Name': drug_name, 'Condition': condition, 'is_accepted': is_accepted}, ignore_index=True)

# Create a scrapped df
scrapped_df = pd.DataFrame(columns=['Drug Name', 'Condition', 'is_accepted'])

# Now we loop through the merged dataframe, if we encounty a row that has multiple values for conditions then we want to
# split that string based on ", " and create a new row for each condition
for index, row in merged_df.iterrows():
    # Check if the condition column contains ", "
    # if row['Declined'] is not nan, then we need to check if "X" is in the string
    if 'X' in str(row['is_accepted']):
        is_accepted = 'False'
    else:
        is_accepted = 'True'
    if ', ' in row['Condition']:
        # Split the string by ", "
        conditions = row['Condition'].split(', ')
        drug_name = row['Drug Name']
        print(conditions)
        # Loop through the conditions
        for condition in conditions:
            # Append the row to the merged dataframe
            print("Creating new row: " + str(drug_name) + " " + str(condition) + " " + str(is_accepted))
            scrapped_df = scrapped_df._append({'Drug Name': drug_name, 'Condition': condition, 'is_accepted': is_accepted}, ignore_index=True)
    else:
        scrapped_df = scrapped_df._append({'Drug Name': row['Drug Name'], 'Condition': row['Condition'], 'is_accepted': is_accepted}, ignore_index=True)

# Save the merged dataframe to a new excel file
scrapped_df.to_excel('AETNA_DDL_Scraped.xlsx', index=False)
