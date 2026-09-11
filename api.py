import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import json

load_dotenv()

LOGIN_URL = os.getenv("LOGIN_URL")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
FROM_DATE = "11-09-2026"
TO_DATE = "26-12-2026"


def get_time_table():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(LOGIN_URL)

    #LOGIN
    email_box =WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.ID, "email")))
    password_box = driver.find_element(by=By.ID, value="password")
    email_box.send_keys(EMAIL)
    password_box.send_keys(PASSWORD)
    sign_in_button = driver.find_element(By.XPATH, "/html/body/div/div/div[6]/main/div/div[2]/form/button")
    sign_in_button.click()

    #GO TO MY SCHEDULE
    my_schedule_link = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.XPATH, "/html/body/div/div/aside/nav/a[7]"))
    )
    my_schedule_link.click()

    #SET DATES
    from_date = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH,
                                        "//input[contains(@placeholder, 'From') or contains(@type, 'date')] | /html/body/div/div/div/main/div/div/div[3]/div/div[4]/div/input"))
    )
    from_date.send_keys(FROM_DATE)

    to_date = driver.find_element(By.XPATH, "/html/body/div/div/div/main/div/div/div[3]/div/div[5]/div/div/input")
    to_date.send_keys(TO_DATE)

    # TRIGGER JS CHANGE EVENT IF ENTER DOESN'T WORK
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", to_date)

    # WAIT FOR CARDS TO LOAD
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "div.rounded-xl.border.border-surface-200")) > 1
    )

    # GET SUBJECTS
    all_cards = driver.find_elements(By.CSS_SELECTOR, "div.rounded-xl.border.border-surface-200")
    timetable = [card for card in all_cards if "PROGRAM" not in card.text.upper()]
    parse_timetable(timetable)

    driver.close()

def parse_timetable(timetable_elements):
    """
    Robust timetable parser using multi-selector fallbacks, textContent retrieval,
    and fallback text parsing.
    """
    scraped_data = []
    try:
        # Context: Inside parse_timetable(timetable_elements), replacing lines 71-98

        for div in timetable_elements:
            day = div.find_element(
                By.CSS_SELECTOR, ".text-sm.font-semibold.text-surface-900"
            ).get_attribute("textContent").strip()

            timings_list = div.find_elements(
                By.CSS_SELECTOR, ".font-mono.text-surface-700"
            )
            subjects_list = div.find_elements(
                By.CSS_SELECTOR, ".block.text-sm.font-medium.truncate"
            )
            places_list = div.find_elements(
                By.CSS_SELECTOR, "span.text-surface-400"
            )

            for timing_elem, subject_elem, place_elem in zip(timings_list, subjects_list, places_list):
                place_raw = place_elem.get_attribute("textContent").strip()
                # Strips out parentheses around "LCR-01"
                place_clean = place_raw.replace("(", "").replace(")", "").strip()

                scraped_data.append({
                    "day": day,
                    "time": timing_elem.get_attribute("textContent").strip(),
                    "subject": subject_elem.get_attribute("textContent").strip(),
                    "place": place_clean
                })

        with open("timetable.json", "w") as f:
            json.dump(scraped_data, f, indent=2)
    except Exception as e:
        return e