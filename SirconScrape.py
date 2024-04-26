from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import psycopg2
import pandas as pd
import time
import os


# This class will be used to scrape the sircon website on a yearly basis to get the licenses for the agents
class SirconScrape:
    def __init__(self):
        self.driver = webdriver.Chrome()

    # Function to open the browser and navigate to the sircon website
    def open_browser(self):
        self.driver.get("https://www.sircon.com/login.jsp?accountType=business")
        time.sleep(5)

    # Function to login to the sircon website
    def login(self):
        try:
            # Wait until the inputs are available
            account_id = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "accountId")))
            username = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "loginName")))
            password = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "password")))

            # Enter the login information
            account_id.send_keys("34017")
            username.send_keys("securecare65")
            password.send_keys("Secure1037*")

            # Submit the form
            password.send_keys(Keys.RETURN)
        except Exception as e:
            print(e)
        time.sleep(5)

    # Click the Network tab
    def click_network(self):
        try:
            # Define the coords for the network tab
            x = 50
            y = 180

            actions = ActionChains(self.driver)

            # Move to the network tab
            actions.move_by_offset(x, y).click().perform()
            time.sleep(.5)

            # Find the element with href="/network/entities
            network = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/network/entities']")))
            network.click()

            time.sleep(5)
        except Exception as e:
            print(e)

    def click_each_row(self, row_position=0):
        try:
            # Find the table class=table-container
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-container")))

            rows = table.find_elements(By.CSS_SELECTOR, "tr.table-row")

            if not rows:
                return

            index = row_position
            row = rows[index]
            current_agent = row.find_element(By.CSS_SELECTOR, "div.name-value")
            name = current_agent.text
            # Now we have the agent name, I want to make the first name lowercase
            # The last name will just be the First Character capitalized
            name = name.split()
            first_name = name[0].lower()
            last_name = name[1][0].upper()
            name = first_name + last_name
            print(name)
            # Click the agent to get to the sub table but open a new tab
            current_agent.click()
            self.parse_sub_table(name)
            time.sleep(1)

            # Go back 2 pages
            self.driver.execute_script("window.history.go(-2)")
            time.sleep(2)
            # Reload the page
            self.driver.refresh()
            time.sleep(3)
            self.click_each_row(index + 1)
        except Exception as e:
            print(e)

    # This is the function that will be parsing the sub tables
    def parse_sub_table(self, agent_name):
        try:
            time.sleep(10)
            print("Navigating to licenses")

            # Lets hit tab 13 times to get to the licenses tab
            for i in range(4):
                webdriver.ActionChains(self.driver).send_keys(Keys.TAB).perform()
                time.sleep(1)
                # print(i)
            webdriver.ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            time.sleep(7)

            for i in range(6):
                webdriver.ActionChains(self.driver).send_keys(Keys.TAB).perform()
                time.sleep(1)
                # print(i)
            webdriver.ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            time.sleep(7)

            # We are now on the all licenses page Now we need to parse the table.
            # The table is in a div with class=table-container
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-container")))
            rows = table.find_elements(By.CSS_SELECTOR, "tbody.suif-expandable-row-group")

            replace_dict = {
                "Insurance Producer ": "",
                "License ": "",
                "Producer - Individual ": "",
                "INTERMEDIARY (AGENT) INDIVIDUAL ": "",
                "(Resident License) ": "",
                "Agent-Nonresident ": "",
                "Agent-Resident ": "",
                "General Lines Agncy/Agnt ": "",
                "NON RES PRODUCER INDIV ": "",
                "NON RESIDENT PRODUCER ": "",
                "NON RES PRODUCER/PRODUCER FIRM ": "",
                "Life/Accident & Health Agent ": "",
                "Agent ": "",
                "MAJOR LINES ": "",
                "Actions Menu ": "",
                "Expiring Soon ": "",
                "Active License ": "",
            }

            # dictionary to replace the state names with abbreviations
            state_abbr_dict = {
                "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
                "California": "CA", "Colorado": "CO", "Connecticut": "CT",
                "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL",
                "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
                "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
                "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
                "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
                "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
                "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
                "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
                "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
                "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
                "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
                "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
                "West Virginia": "WV", "Virginia": "VA", "Washington": "WA",
                "Wisconsin": "WI", "Wyoming": "WY"
            }

            # Create a pandas dataframe to store the data
            df = pd.DataFrame(columns=["Agent", "State", "License Number", "Expiration Date"])

            # Skip the first row because it is the header
            for row in rows:
                # print(row.text)
                # Remove the \n from the text
                row_text = row.text.replace("\n", " ")

                # Replace the text with the values in the replace_dict
                print("scrubbing text")
                for key in replace_dict:
                    row_text = row_text.replace(key, replace_dict[key])
                    time.sleep(.1)

                row_text = row_text.replace("Active Actions Menu", "")
                row_text = row_text.replace("Active Expiring Soon", "")
                row_text = row_text.replace("Active", "")

                for key in state_abbr_dict:
                    row_text = row_text.replace(key, state_abbr_dict[key])
                print("Text scrubbed adding to dataframe")

                split_text = row_text.split(" ")

                row_df = pd.DataFrame([{
                    "Agent": agent_name,
                    "State": split_text[0] if len(split_text) > 1 else "",
                    "License Number": split_text[1] if len(split_text) > 2 else "",
                    "Expiration Date": split_text[2] if len(split_text) > 3 else ""
                }])

                df = pd.concat([df, row_df], ignore_index=True)

                print(agent_name + " - " + row_text)
                time.sleep(1)
            print(df)
            df.to_csv(agent_name + "-licenses.csv", index=False)
            time.sleep(10)
        except Exception as e:
            print(e)

    def close_browser(self):
        self.driver.quit()

    # This function will condense the csv files into one csv file
    def condensecsv(self):
        # Get the list of csv files found in the dir
        files = [f for f in os.listdir() if f.endswith('.csv')]
        # Create a pandas dataframe to store the data
        df = pd.DataFrame(columns=["Agent", "State", "License Number", "Expiration Date"])
        # Loop through the files and append the data to the dataframe
        for file in files:
            data = pd.read_csv(file)
            df = pd.concat([df, data], ignore_index=True)
        # Save the dataframe to a csv file
        df.to_csv("all-licenses.csv", index=False)







scraper = SirconScrape()
scraper.open_browser()
scraper.login()
scraper.click_network()
scraper.click_each_row(0)
scraper.close_browser()
