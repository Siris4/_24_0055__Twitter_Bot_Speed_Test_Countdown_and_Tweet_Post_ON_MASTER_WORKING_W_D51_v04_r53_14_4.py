
import sys
import time
import re
import threading  # for separate countdown timer:
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

element_for_Total_Play_speed = '''
<a class="no-link-chev btnBanner" href="/personaliza?150#internet" promo-name="150 megas 2p" promo-id="1" target="_blank">
    <img class="d-none d-md-block w-100" src="/assetsv2/img/home/sliders/Banner1.png">
    <img class="d-block d-md-none" src="/assetsv2/img/home/sliders/Banner1_mobile.png">
</a>'''

# the regular expression pattern to extract out the number of Mbps (megas):
# pattern = r'promo-name="(\d+ megas)'  # this one is a string
pattern = r'promo-name="(\d+)'  # this is an integer

# search for the pattern in the string
match = re.search(pattern, element_for_Total_Play_speed)

# check if a match was found
if match:
    extracted_text = match.group(1)
    # print(extracted_text)
else:
    extracted_text = "No internet speed found."

# constants:
PROMISED_SPEEDS_DOWN = extracted_text
PROMISED_SPEEDS_UP = 10

# print(
#     f"\nThis is the first print statement and shows the integer of the extracted text, which is then converted to PROMISED_DOWNLOAD_SPEEDS: {int(PROMISED_DOWNLOAD_SPEEDS)}")

TWITTER_EMAIL = "YOUR_EMAIL"
TWITTER_PASSWORD = "YOUR_PASSWORD"

URL_FOR_SPEEDTEST = "https://www.speedtest.net/"


# ChromeDriverManager is handled by the webdriver_manager.chrome


class InternetSpeedTwitterBot:
    def __init__(self, PROMISED_SPEEDS_DOWN, PROMISED_SPEEDS_UP):
        # driver = init_driver()  #try this 1st
        self.driver = self.init_driver()
        self.PROMISED_SPEEDS_DOWN = PROMISED_SPEEDS_DOWN
        self.PROMISED_SPEEDS_UP = PROMISED_SPEEDS_UP

        self.open_website(URL_FOR_SPEEDTEST)
        self.tweet_at_provider()

    def init_driver(self):
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        self.log_message("Webdriver initialized.")
        return driver

    # my function to log messages:
    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{timestamp} - {message}")

    def print_test_for_megas_speed(self, PROMISED_SPEEDS_DOWN, PROMISED_SPEEDS_UP):
        self.log_message(
            f"The Promised Download speed which is stated on Comcast's Website is: {PROMISED_SPEEDS_DOWN} (Mbps)")
        self.log_message(
            f"The Promised Upload speed which is stated on Comcast's Website is: {PROMISED_SPEEDS_UP} (Mbps)")

    def open_website(self, url):
        self.driver.get(URL_FOR_SPEEDTEST)
        self.log_message(f"Successfully opened the website: {URL_FOR_SPEEDTEST}")

        self.print_test_for_megas_speed(self.PROMISED_SPEEDS_DOWN, self.PROMISED_SPEEDS_UP)

        time.sleep(2)

        self.press_go_button_and_get_internet_speed()

    def press_go_button_and_get_internet_speed(self):
        global ACTUAL_DOWNLOAD_SPEED, ACTUAL_UPLOAD_SPEED
        ACTUAL_DOWNLOAD_SPEED = ""
        ACTUAL_UPLOAD_SPEED = ""

        XPATH_for_speed_url = '//*[@id="container"]/div/div[3]/div/div/div/div[2]/div[3]/div[1]/a/span[4]'
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, XPATH_for_speed_url))
        )
        self.speed_button = self.driver.find_element(By.XPATH, XPATH_for_speed_url)
        self.speed_button.click()  # clicks on the Go button to generate the speeds
        print("The Go button was pushed to start the Internet Speed Test.")
        print(f"\nSpeed check starting. Please wait... :) ")

        # Start of countdown timer
        for remaining in range(54, 0, -1):
            sys.stdout.write(f"\rCountdown: {remaining} seconds remaining")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\n")  # Move to the next line after the countdown completes
        # trying to close a potential popup or ad after the speed test
        xpath_for_ad_close_button = '//*[@id="container"]/div/div[3]/div/div/div/div[2]/div[3]/div[3]/div/div[3]/div/div/div[1]/div/div/div[2]/div[2]/a'
        backup_xpath_for_ad_close_button = '//*[@id="container"]/div/div[3]/div/div/div/div[2]/div[3]/div[3]/div/div[8]/div/a/svg/use'
        final_backup_xpath = '/html/body/div[3]/div/div[3]/div/div/div/div[2]/div[3]/div[3]/div/div[8]/div/a/svg/use'

        for xpath in [xpath_for_ad_close_button, backup_xpath_for_ad_close_button, final_backup_xpath]:
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                ad_close_button = self.driver.find_element(By.XPATH, xpath)
                ad_close_button_text = ad_close_button.text
                match = re.search(r'\b\d{9,13}\b', ad_close_button_text)
                if match:
                    result_id_number = match.group()
                    print(f"\nYour extracted Result ID number: {result_id_number}")
                self.driver.execute_script("arguments[0].click();", ad_close_button)
                print(f"\nClicked on the ad close button using XPath: {xpath}")
                break  # Exit the loop if click is successful
            except NoSuchElementException:
                print(f"Ad close button not found using XPath: {xpath}")
            except ElementClickInterceptedException:
                print(f"Element click intercepted using XPath: {xpath}")

        # Extracting actual download and upload speeds
        download_speed_xpath = '/html/body/div[3]/div/div[3]/div/div/div/div[2]/div[3]/div[3]/div/div[2]/div[1]/div[2]/div[1]/div[1]/div/div[2]/span'
        upload_speed_xpath = '/html/body/div[3]/div/div[3]/div/div/div/div[2]/div[3]/div[3]/div/div[2]/div[1]/div[2]/div[1]/div[2]/div/div[2]/span'

        try:
            download_speed_element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, download_speed_xpath))
            )
            ACTUAL_DOWNLOAD_SPEED = download_speed_element.text
            upload_speed_element = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, upload_speed_xpath))
            )
            ACTUAL_UPLOAD_SPEED = upload_speed_element.text

            print(f"\nYour download speed is currently: {ACTUAL_DOWNLOAD_SPEED} Mbps")
            print(f"\nYour upload speed is currently: {ACTUAL_UPLOAD_SPEED} Mbps")
        except NoSuchElementException:
            print("Could not find the speed result elements.")
        except TimeoutException:
            print("Timed out waiting for the speed result elements.")

    def tweet_at_provider(self):
        pass


# creating an instance of internetspeedtwitterbot:
TwitterBot = InternetSpeedTwitterBot(PROMISED_SPEEDS_DOWN, PROMISED_SPEEDS_UP)

# we can now call the methods on the instance that was created just above
# TwitterBot.open_website(URL_FOR_SPEEDTEST)

TwitterBot.tweet_at_provider()

#this is the end of the Internet Speed detection:

#---------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------#

# Start of the Twitter login and Tweet Post:

twitter_url = "https://twitter.com/"
search_keyword_within_twitter = "Comcast"


def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{timestamp} - {message}")

def init_driver():
    chrome_options = Options()
    chrome_options.page_load_strategy = 'eager'
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    log_message("Webdriver initialized.")
    return driver

def login_twitter(driver, email, password):
    start_time = time.time()
    driver.get(twitter_url)
    log_message("Twitter page loaded.")

    wait = WebDriverWait(driver, 10)
    try:
        sign_in_button_xpath = "//a[@href='/login']"
        sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, sign_in_button_xpath)))
        sign_in_button.click()
        log_message("Sign-in button clicked.")

        selectors = [
            (By.XPATH, "//input[@name='session[username_or_email]']"),
            (By.CSS_SELECTOR, "input[autocomplete='username']"),
            (By.CSS_SELECTOR, "#react-root > div > div > div > main > div > div > div > div.css-175oi2r.r-1ny4l3l.r-6koalj.r-16y2uox > div.css-175oi2r.r-16y2uox.r-1jgb5lz.r-13qz1uu > div > div.css-175oi2r.r-1f1sjgu.r-mk0yit.r-13qz1uu > label > div > div.css-175oi2r.r-18u37iz.r-16y2uox.r-1wbh5a2.r-1wzrnnt.r-1udh08x.r-xd6kpl.r-1pn2ns4.r-ttdzmv > div > input"),
            (By.XPATH, "//*[@id='react-root']/div/div/div/main/div/div/div/div[2]/div[2]/div/div[5]/label/div/div[2]/div/input"),
            (By.XPATH, "/html/body/div/div/div/div/main/div/div/div/div[2]/div[2]/div/div[5]/label/div/div[2]/div/input"),
            (By.XPATH, "//input[@autocapitalize='sentences']")
        ]

        email_field = None
        for by, value in selectors:
            try:
                email_field = wait.until(EC.presence_of_element_located((by, value)))
                if email_field:
                    log_message("Email field found.")
                    break
            except TimeoutException:
                log_message(f"Email field not found using {by}='{value}'")

        if not email_field:
            raise Exception("Email field not found after trying all selectors.")

        email_field.send_keys(email)
        log_message("Email entered.")
        email_field.send_keys(Keys.RETURN)
        log_message("Email submitted.")

        password_selectors = [
            (By.NAME, 'password'),
            (By.CSS_SELECTOR, 'input[type="password"][autocomplete="current-password"]'),
            (By.CSS_SELECTOR, '.r-30o5oe'),
            (By.XPATH, "//input[@autocomplete='current-password']"),
            (By.XPATH, "//input[@type='password']")
        ]

        password_field = None
        for by, value in password_selectors:
            try:
                password_field = wait.until(EC.presence_of_element_located((by, value)))
                if password_field:
                    log_message("Password field found.")
                    break
            except TimeoutException:
                log_message(f"Password field not found with {by}='{value}'")

        if not password_field:
            raise Exception("Password field not found after trying all selectors.")

        password_field.send_keys(password)
        log_message("Password entered.")
        password_field.send_keys(Keys.RETURN)
        log_message("Login submitted.")

        end_time = time.time()
        total_time = end_time - start_time
        log_message(f"Login completed in {total_time:.2f} seconds.")

    except Exception as e:
        log_message(f"An error occurred during login: {str(e)}")

def navigate_to_twitter_explore(driver):
    wait = WebDriverWait(driver, 10)
    explore_button = None
    explore_selectors = [
        (By.CSS_SELECTOR, "#react-root > div > div > div.css-175oi2r.r-1f2l425.r-13qz1uu.r-417010.r-18u37iz > header > div > div > div > div:nth-child(1) > div.css-175oi2r.r-15zivkp.r-1bymd8e.r-13qz1uu.r-1awozwy > nav > a:nth-child(2) > div > div > svg"),
        (By.CSS_SELECTOR, "#react-root > div > div > div.css-175oi2r.r-1f2l425.r-13qz1uu.r-417010.r-18u37iz > header > div > div > div > div:nth-child(1) > div.css-175oi2r.r-15zivkp.r-1bymd8e.r-13qz1uu.r-1awozwy > nav > a:nth-child(2) > div > div"),
        (By.CSS_SELECTOR, "#react-root > div > div > div.css-175oi2r.r-1f2l425.r-13qz1uu.r-417010.r-18u37iz > header > div > div > div > div:nth-child(1) > div.css-175oi2r.r-15zivkp.r-1bymd8e.r-13qz1uu.r-1awozwy > nav > a:nth-child(2)"),
        (By.XPATH, "//a[@href='/explore']"),
        (By.XPATH, "//*[contains(@aria-label, 'Explore')]")
    ]

    for selector in explore_selectors:
        try:
            explore_button = wait.until(EC.element_to_be_clickable(selector))
            if explore_button:
                log_message("Explore button found.")
                explore_button.click()
                log_message("Navigated to Explore.")
                break
        except TimeoutException:
            log_message(f"Explore button not found using {selector[0]}='{selector[1]}'")

    if not explore_button:
        raise Exception("Explore button not found after trying all selectors.")

def search_twitter(driver, query):
    wait = WebDriverWait(driver, 10)
    search_xpath = "//input[@aria-label='Search query']"
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, search_xpath)))
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    log_message(f"Searched for {query}.")


def prepare_tweet(driver, message):
    wait = WebDriverWait(driver, 20)
    try:
        # Open the tweet dialog by clicking the "Post" button
        post_button_selectors = [
            "//a[@aria-label='Post']",
            "//span[contains(text(),'Post')]/..",
            "//div[contains(@role, 'button') and contains(text(), 'Post')]",
            "#layers div[role='button'][data-testid='tweetButton']",
            "//div[contains(@class, 'css-1qaijid') and contains(text(), 'Post')]",
            "//span[@class='css-1qaijid r-bcqeeo r-qvutc0 r-poiln3'][contains(text(),'Post')]"
        ]

        post_button = None
        for selector in post_button_selectors:
            try:
                if selector.startswith(("//", "/html")):
                    post_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    post_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                if post_button:
                    post_button.click()
                    log_message("Initial Post button clicked to open the tweet dialog.")
                    break
            except TimeoutException:
                log_message(f"Initial Post button not found using selector: {selector}")

        if not post_button:
            raise Exception("Failed to find and click the initial Post button.")

        # Wait for the tweet box to be ready and type the message
        tweet_box_selectors = [
            "//div[@aria-label='Tweet text']",
            "//div[@data-block='true']",
            "//textarea[@aria-label='Tweet text']",
            "div[data-testid='tweetTextarea_0']",
            "div[role='textbox']"
        ]

        tweet_box = None
        for selector in tweet_box_selectors:
            try:
                if selector.startswith(("//", "/html")):
                    tweet_box = wait.until(EC.visibility_of_element_located((By.XPATH, selector)))
                else:
                    tweet_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                if tweet_box:
                    tweet_box.send_keys(message)
                    log_message("Message typed in the tweet box.")
                    break
            except TimeoutException:
                log_message(f"Tweet box not found using selector: {selector}")

        if not tweet_box:
            raise Exception("Tweet box not found after trying all selectors.")

        # Wait for the tweet to be ready to send, then find and click the final "Post" button
        time.sleep(2)  # Adjust sleep time as needed for the page to be ready
        final_post_button_selectors = [
            "div[data-testid='tweetButton']",
            "//div[contains(@role, 'button') and contains(text(), 'Tweet')]",
            "//span[contains(text(),'Tweet')]/..",
            "//div[contains(@role, 'button') and @data-testid='tweetButton']"
        ]

        final_post_button = None
        for selector in final_post_button_selectors:
            try:
                if selector.startswith(("//", "/html")):
                    final_post_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    final_post_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                if final_post_button:
                    final_post_button.click()
                    log_message("Final Post button clicked to submit the tweet.")
                    break
            except TimeoutException:
                log_message(f"Final Post button not found using selector: {selector}")

        if not final_post_button:
            raise Exception("Failed to find and click the final Post button.")

    except Exception as e:
        log_message(f"An error occurred while preparing and posting the tweet: {str(e)}")


def main():
    driver = init_driver()
    login_twitter(driver, TWITTER_EMAIL, TWITTER_PASSWORD)
    navigate_to_twitter_explore(driver)
    search_twitter(driver, search_keyword_within_twitter)
    prepare_tweet(driver, f"Thank you for these speeds: {ACTUAL_DOWNLOAD_SPEED} Mbps Download and {ACTUAL_UPLOAD_SPEED} Mbps Upload")
    log_message("Browser will remain open until manually closed.")
    input("Press Enter to close the browser...")
    driver.quit()

if __name__ == "__main__":
    main()
