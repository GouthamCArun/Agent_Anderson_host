from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
load_dotenv()
# LinkedIn credentials
USERNAME = os.getenv("LINKDIN_U")
PASSWORD = os.getenv("LINKDIN_P")

def send_linkedin_message(profile_url, message_content):
    """Logs into LinkedIn, navigates to the profile, waits for manual click on 'Message',
    then types the message and waits for manual 'Send'."""
    
    driver = webdriver.Chrome()
    
    try:
        # Open LinkedIn login page
        driver.get('https://www.linkedin.com/login')

        # Enter login credentials and submit
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(USERNAME)
        driver.find_element(By.NAME, 'session_password').send_keys(PASSWORD)
        driver.find_element(By.CLASS_NAME, 'btn__primary--large').click()

        # Directly navigate to the profile
        driver.get(profile_url)

        # Inform the user to manually click 'Message' button
        print("\nProfile loaded. Please manually click the 'Message' button.")
        
        # Wait until the message box appears (indicating user has clicked 'Message')
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Write a message…']"))
        )
        
        # Once the message box appears, type the message
        print("\nMessage box detected! Typing the message now...")
        message_box = driver.find_element(By.XPATH, "//div[@aria-label='Write a message…']")
        message_box.send_keys(message_content)

        # Inform user to manually click 'Send' button
        print("\nMessage typed. Please manually click the 'Send' button.")

        # Wait indefinitely for user to click 'Send'
        input("\nPress Enter here after clicking the 'Send' button...")

        print("Message sent successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()

# Example usage
# profile_url = "https://www.linkedin.com/in/goutham-c-arun-057b2722b/"
# message_content = "Hello, this is a test message!"
# send_linkedin_message(profile_url, message_content)
