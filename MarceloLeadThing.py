# This Will be a quick python script to scrape securecare65.radiusbob.com for any leads that have a Email address and assigned to the provided user.
# this script will grab the name, and email address of the lead and save it to a csv file.
# import the necessary libraries like selenium, chrome web driver, and pandas
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

# Set up the class for the lead scraper

class LeadScraper:
    def __init__(self, username, password, user):
        self.username = username
        self.password = password
        self.user = user
        self.driver = webdriver.Chrome()
        self.driver.get('https://securecare65.radiusbob.com')
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()
        time.sleep(5)

    def login(self):
        # could we click on the image with alt="Sign in With Google"
        google_login = self.driver.find_element(By.XPATH, '//a[@href="/auth/google_oauth2"]')
        google_login.click()
        # Find the input field with type="email" and id="identifierId"
        time.sleep(2)
        email_input = self.driver.find_element(By.XPATH, '//input[@type="email"]')
        email_input.send_keys(self.username)
        email_input.send_keys(Keys.RETURN)
        time.sleep(5)
        # Find the input field with type="password" and name="password"
        password_input = self.driver.find_element(By.XPATH, '//input[@name="Passwd"]')
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)

    def scrape_leads(self):
        # navigate to the leads page https://securecare65.radiusbob.com/saas/records?record_type_id=259
        self.driver.get('https://securecare65.radiusbob.com/saas/records?record_type_id=259')
        time.sleep(10)
        # To find the dropdown, we need to hit tab 61 times
        for i in range(61):
            ActionChains(self.driver).send_keys(Keys.TAB).perform()
            time.sleep(.5)
        # hit space to open the dropdown
        ActionChains(self.driver).send_keys(Keys.SPACE).perform()
        time.sleep(3)
        # Lets use action chains to type in the users name and hit enter
        ActionChains(self.driver).send_keys(self.user).perform()
        time.sleep(2)
        ActionChains(self.driver).send_keys(Keys.RETURN).perform()
        time.sleep(5)
        # Now we need to find the leads table and load it into a pandas dataframe
        # Click on the leads per page dropdown and select 1000
        # it has the id=btnGroupDrop1
        dropdown = self.driver.find_element(By.ID, 'btnGroupDrop1')
        dropdown.click()
        time.sleep(2)
        # Click on the 1000 option
        # <a class="dropdown-item pagesize" href="#" rel="1000">1000</a>
        option = self.driver.find_element(By.XPATH, '//a[@rel="1000"]')
        option.click()
        time.sleep(20)
        # Grab the leads table
        # <table class="table table-hover align-middle has-bulk-select-footer">
        leads_table = self.driver.find_element(By.XPATH, '//table[@class="table table-hover align-middle has-bulk-select-footer"]')
        # Load the rows into a pandas dataframe
        leads_df = pd.read_html(leads_table.get_attribute('outerHTML'))[0]
        # Print the entire width of the dataframe
        pd.set_option('display.max_columns', None)
        print(leads_df.head())
        # Save the dataframe to a csv file only keep the columns up to Agent
        leads_df = leads_df.iloc[:, :4]
        # only keep the rows that have an email address, regex to find "E: *".
        # Also, trim the text to only include the email address in that column
        leads_df = leads_df[leads_df['Contact Information'].str.contains('E: ', na=False)]
        leads_df['Contact Information'] = leads_df['Contact Information'].str.extract(r'E: (.*)')
        leads_df.to_csv('leads.csv', index=False)
        time.sleep(60)
        # CLick the <a class="page-link" rel="next" href="/saas/records?assigned_user_id=20367&amp;page=2&amp;pagesize=1000&amp;searchoption=name">»</a>
        next_page = self.driver.find_element(By.XPATH, '//a[@rel="next"]')
        next_page.click()
        time.sleep(20)
        leads_table = self.driver.find_element(By.XPATH, '//table[@class="table table-hover align-middle has-bulk-select-footer"]')
        # Load the rows into a pandas dataframe
        leads_df = pd.read_html(leads_table.get_attribute('outerHTML'))[0]
        # Print the entire width of the dataframe
        pd.set_option('display.max_columns', None)
        print(leads_df.head())
        # Save the dataframe to a csv file only keep the columns up to Agent
        leads_df = leads_df.iloc[:, :4]
        # only keep the rows that have an email address, regex to find "E: *".
        # Also, trim the text to only include the email address in that column
        leads_df = leads_df[leads_df['Contact Information'].str.contains('E: ', na=False)]
        leads_df['Contact Information'] = leads_df['Contact Information'].str.extract(r'E: (.*)')
        leads_df.to_csv('leads1.csv', index=False)








# Initialize the class with the username, password, and user
#username = 'marcelo@securecare65.com'
#p#as#swo#rd = '###Halamadrid1###'
# user = 'Marcelo Polar'
lead_scraper = LeadScraper(username, password, user)
lead_scraper.login()
lead_scraper.scrape_leads()