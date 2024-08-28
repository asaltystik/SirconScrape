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

    # Function to log in to the sircon website
    def login(self):
        try:
            # Wait until the inputs are available
            account_id = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "accountId")))
            username = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "loginName")))
            password = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "password")))

            # Enter the login information
            account_id.send_keys("34017")
            username.send_keys("securecare65")
            password.send_keys("Secure33760#")
            # account_id.send_keys("87880")
            # username.send_keys("chrisbeckett217@gmail.com")
            # password.send_keys("aNNUITY123!")

            # Submit the form
            password.send_keys(Keys.RETURN)
        # If there is an error print the error
        except Exception as e:
            print(e)
        time.sleep(5)

    # Click the Network tab
    def click_network(self):
        try:
            # Define the coords for the network tab
            x = 50
            y = 180

            #  Set the actions to move to the network tab
            actions = ActionChains(self.driver)

            # Move to the network tab
            actions.move_by_offset(x, y).click().perform()
            time.sleep(.8)

            # Find the element with href="/network/entities
            network = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href='/network/entities']")))
            network.click()
            time.sleep(6)

        # If the element is not found print the error
        except Exception as e:
            print(e)

    # This function will click each agent in the table to get to the sub table
    def click_each_row(self, row_position=0):
        try:
            # Find the table class=table-container
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-container")))

            rows = table.find_elements(By.CSS_SELECTOR, "tr.table-row")
            print("Rows: ", len(rows))
            print("Row Names: ", [row.find_element(By.CSS_SELECTOR, "div.name-value").text for row in rows])

            # If there are no rows then leave the function
            if not rows:
                return

            # Set the index to the passed in row_position
            index = row_position
            row = rows[index]
            # Get the current agent name from the row
            current_agent = row.find_element(By.CSS_SELECTOR, "div.name-value")
            name = current_agent.text
            # Now we have the agent name, I want to make the first name lowercase
            # The last name will just be the First Character capitalized
            name = name.split()
            first_name = name[0].lower()
            last_name = name[1][0].upper()
            name = first_name + last_name  # Format the name to be first name lower last name upper
            print(name)
            # Click the agent to get to the sub table but open a new tab
            current_agent.click()
            print("Parse Sub Table")
            self.parse_sub_table(name)
            print("Sub Table Parsed for agent: " + name)
            time.sleep(4)

            # Go back 2 pages to get back to the main page
            self.driver.execute_script("window.history.go(-2)")
            time.sleep(20)
            # Reload the page
            self.driver.refresh()
            time.sleep(20)
            # Recursively call the function to click the next agent.
            # We do this because the page reloads and the elements are no longer available
            self.click_each_row(index + 1)
        # If there is an error print the error
        except Exception as e:
            print(e)

    # This is the function that will be parsing the sub tables
    def parse_sub_table(self, agent_name):
        try:
            time.sleep(15)
            print("Navigating to licenses")
            navigation = True
            try:
                while navigation:
                    # Lets hit tab 13 times to get to the licenses tab
                    for i in range(4):
                        webdriver.ActionChains(self.driver).send_keys(Keys.TAB).perform()
                        time.sleep(2)
                        # print(i)
                    webdriver.ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                    time.sleep(8)

                    # now we must hit tab 6 more times to get to the all licenses tab
                    for i in range(6):
                        webdriver.ActionChains(self.driver).send_keys(Keys.TAB).perform()
                        time.sleep(2)
                        # print(i)
                    webdriver.ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                    time.sleep(8)
                    # Wait 7 seconds between each set of actions to allow the pages to load+
                    navigation = False  # we should be done navigating so lets set this to false
            except Exception as e:
                # reload the page if there is an error and try again
                self.driver.refresh()
                time.sleep(5)
                print(e)
                navigation = True

            # Scroll to down the page using the page down key
            for i in range(8):
                webdriver.ActionChains(self.driver).send_keys(Keys.PAGE_DOWN).perform()
                time.sleep(.5)
            time.sleep(1)
            # we want to hit the selection box with class="ng-pristine ng-valid ng-touched"
            # this will allow us to select all licenses
            # print('Attempting to select all licenses')
            # element = WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, "input.ng-pristine.ng-valid.ng-touched")))
            # element.click()
            # print('clicked drop down')
            # element.send_keys(Keys.DOWN)
            # element.send_keys(Keys.ENTER)
            # time.sleep(2)

            # click the element with class="ng-pristine ng-valid ng-touched"
            # element = WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, "input.ng-pristine.ng-valid.ng-touched")))
            # element.click()
            # time.sleep(5)

            # We are now on the all licenses page Now we need to parse the table.
            # The table is in a div with class=table-container
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.table-container")))
            rows = table.find_elements(By.CSS_SELECTOR, "tbody.suif-expandable-row-group")

            # Dictionary to parse out unwanted text
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
                "SUBLICENSEE ": "",
                "SUBLICENSEE": "",
                "Producer ": "",
                "Producer": "",
                "(NonResident) ": "",
                "(NonResident)": "",
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

                # For whatever reason these dont get found in the replace_dict so lets just hard code them into this
                row_text = row_text.replace("Active Actions Menu", "")
                row_text = row_text.replace("Active Expiring Soon", "")
                row_text = row_text.replace("Active", "")

                # Replace the state names with the abbreviations
                for key in state_abbr_dict:
                    row_text = row_text.replace(key, state_abbr_dict[key])
                print("Text scrubbed adding to dataframe")

                # Split the text by spaces - prep for adding to the dataframe
                split_text = row_text.split(" ")

                # creating a temp dataframe since df.append does not seem to work in this implementation
                row_df = pd.DataFrame([{
                    "Agent": agent_name,  # Add the agent name
                    "State": split_text[0] if len(split_text) > 1 else "",  # Add the state
                    "License Number": split_text[1] if len(split_text) > 2 else "",  # Add the license number
                    "Expiration Date": split_text[2] if len(split_text) > 3 else ""  # Add the expiration date
                }])

                # Add the temp dataframe to the main dataframe
                df = pd.concat([df, row_df], ignore_index=True)

                # Print the agent name and the row text
                print(agent_name + " - " + row_text)
                time.sleep(1)
            print(df)
            # Save the dataframe to a csv file to be sent to the server
            df.to_csv(agent_name + "-licenses.csv", index=False)
            time.sleep(10)
        # If there is an error print the error
        except Exception as e:
            print(e)

    # Function to close the browser
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
        df.to_csv("all-licenses1.csv", index=False)


# Gonna clean this up later but for now this bit of code will be the __main__ function in all but name lol
scraper = SirconScrape()  # Create the scraper object
scraper.open_browser()  # open the browser
scraper.login()  # login to the site
scraper.click_network()  # Click the network tab
scraper.click_each_row(0)  # click each row in the table and parse the sub table
scraper.close_browser()  # close the browser free some memory, Greedy ass cpu
scraper.condensecsv()
