"""
LinkedIn Automated Connection Request Bot

This script automates the process of sending personalized connection requests
on LinkedIn based on search criteria defined in the configuration file.
"""

import os
import random
import subprocess
from pathlib import Path
from time import sleep

import yaml
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils import call_openrouter_llm

# Add project paths to sys.path
import sys
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "prompts"))

from connection_request_prompt import get_note_text_prompt


# Constants
DEBUG_PROFILE = r"C:\Users\shaur\selenium_chrome_profile"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def load_config():
    """Load connection configuration from YAML file."""
    load_dotenv()
    config_path = PROJECT_ROOT / "config" / "connection.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def start_chrome_debug_session():
    """Start Chrome with remote debugging enabled and return the WebDriver."""
    os.makedirs(DEBUG_PROFILE, exist_ok=True)
    
    process = subprocess.Popen([
        CHROME_PATH,
        "--remote-debugging-port=9222",
        f"--user-data-dir={DEBUG_PROFILE}",
        "--no-first-run",
        "--no-default-browser-check"
    ])
    
    sleep(2)
    
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        raise RuntimeError(f"Failed to connect to Chrome: {e}")
    
    return driver


def click_button(driver, text, css_selector):
    """Click a button containing the specified text."""
    for btn in driver.find_elements(By.CSS_SELECTOR, css_selector):
        if text in btn.text:
            btn.click()
            sleep(random.uniform(1, 2))
            return True
    return False


def add_filter_information(driver, config, field_type, css_selector):
    """Add filter information to a search field."""
    input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )
    input_element.click()
    
    location = config[field_type][field_type]
    input_element.send_keys(location)
    sleep(random.uniform(1, 2))
    
    print("Pressing down arrow key...")
    input_element.send_keys(Keys.ARROW_DOWN)
    sleep(random.uniform(0.5, 1))
    
    print("Pressing Enter key...")
    input_element.send_keys(Keys.RETURN)


def apply_search_filters(driver, config):
    """Apply search filters based on configuration."""
    click_button(driver, "People", "button.search-reusables__filter-pill-button")
    click_button(driver, "All filters", "button.search-reusables__filter-pill-button")
    click_button(driver, "2nd", "button.search-reusables__multiselect-pill-button")
    
    if config["filter_location"]["filter_bool"]:
        click_button(driver, "Add a location", 
                    "button.reusable-search-filters-advanced-filters__add-filter-button")
        add_filter_information(driver, config, "filter_location", 
                              "input.basic-input[placeholder='Add a location']")
    
    if config["filter_company"]["filter_bool"]:
        click_button(driver, "Add a company", 
                    "button.reusable-search-filters-advanced-filters__add-filter-button")
        add_filter_information(driver, config, "filter_company", 
                              "input.basic-input[placeholder='Add a company']")
    
    click_button(driver, "Show results", 
                "button.search-reusables__secondary-filters-show-results-button")
    
    # Wait for search results to load
    sleep(random.uniform(3, 5))


def collect_profile_urls(driver, config):
    """Collect profile URLs from search results pages."""
    profile_urls = []
    
    for page_num in range(config["no_of_search_pages"]):
        print(f"Collecting profiles from page {page_num + 1}...")
        
        # Wait for search results to be present
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    "div[data-view-name='search-entity-result-universal-template']"
                ))
            )
        except TimeoutException:
            print("Warning: No profile elements found on this page (timeout)")
        
        profile_elements = driver.find_elements(
            By.CSS_SELECTOR, 
            "div[data-view-name='search-entity-result-universal-template']"
        )
        print(f"Found {len(profile_elements)} profile elements on page {page_num + 1}")
        
        for profile_element in profile_elements:
            profile_link = profile_element.find_element(By.TAG_NAME, "a").get_attribute("href")
            profile_urls.append(profile_link)
        
        sleep(random.uniform(1, 2))
        click_button(driver, "Next", "button.artdeco-pagination__button--next")
    
    return profile_urls


def extract_profile_info(driver):
    """Extract profile name and tagline from the current page."""
    page_title = driver.title
    if " | LinkedIn" in page_title:
        profile_name = page_title.split(" | LinkedIn")[0].strip()
        tagline_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.text-body-medium.break-words"))
        )
        profile_tagline = tagline_element.text.strip()
        profile_info = "\n".join([profile_name, profile_tagline])
        return profile_name, profile_info
    return "", ""


def send_connection_request(driver, profile_name, profile_info):
    """Attempt to send a connection request with a personalized note."""
    try:
        connect_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, f'button[aria-label="Invite {profile_name} to connect"]')
            )
        )
        connect_btn[1].click()
        sleep(random.uniform(1, 3))
        
        add_a_note_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Add a note"]'))
        )
        add_a_note_btn.click()
        
        note_txt_messages = get_note_text_prompt(profile_info)
        note_txt = call_openrouter_llm(note_txt_messages)
        
        text_area = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "textarea[placeholder='Ex: We know each other from…']")
            )
        )
        text_area.send_keys(note_txt)
        sleep(random.uniform(3, 5))
        
        send_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Send invitation"]'))
        )
        send_btn.click()
        sleep(random.uniform(5, 10))
        return True
    
    except Exception:
        return False


def send_connection_request_via_more_actions(driver, profile_name, profile_info):
    """Attempt to send a connection request via the 'More actions' menu."""
    try:
        more_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'button[aria-label="More actions"]'))
        )
        more_btn[1].click()
        sleep(random.uniform(1, 3))
        
        connect_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, f'div[aria-label="Invite {profile_name} to connect"]')
            )
        )
        connect_btn[1].click()
        sleep(random.uniform(1, 3))
        
        add_a_note_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Add a note"]'))
        )
        add_a_note_btn.click()
        
        note_txt_messages = get_note_text_prompt(profile_info)
        note_txt = call_openrouter_llm(note_txt_messages)
        
        text_area = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "textarea[placeholder='Ex: We know each other from…']")
            )
        )
        text_area.send_keys(note_txt)
        sleep(random.uniform(3, 5))
        
        send_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Send invitation"]'))
        )
        send_btn.click()
        sleep(random.uniform(5, 10))
        return True
    
    except Exception:
        return False


def run_connection_bot():
    """Main function to run the LinkedIn connection bot."""
    config = load_config()
    driver = start_chrome_debug_session()
    wait = WebDriverWait(driver, 10)
    
    # Navigate to LinkedIn
    driver.get("https://www.linkedin.com/")
    sleep(random.uniform(3, 5))
    
    # Perform search
    try:
        search_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.search-global-typeahead__input"))
        )
        search_input.click()
        search_input.send_keys(config["search_term"], Keys.RETURN)
    except TimeoutException:
        raise RuntimeError("Search bar not found")
    
    sleep(random.uniform(3, 5))
    
    # Apply filters
    apply_search_filters(driver, config)
    
    # Collect profile URLs
    profile_urls = collect_profile_urls(driver, config)
    print(f"Collected {len(profile_urls)} profile URLs")
    
    # Send connection requests
    sleep(random.uniform(1, 2))
    cn_rq_cnt = 0
    
    while cn_rq_cnt < len(profile_urls) and cn_rq_cnt < config["no_of_target_connections"]:
        target_url = profile_urls[cn_rq_cnt]
        driver.get(target_url)
        sleep(random.uniform(3, 5))
        
        profile_name, profile_info = extract_profile_info(driver)
        
        if profile_name:
            success = send_connection_request(driver, profile_name, profile_info)
            if not success:
                send_connection_request_via_more_actions(driver, profile_name, profile_info)
        
        cn_rq_cnt += 1
        print(f"Processed {cn_rq_cnt}/{min(len(profile_urls), config['no_of_target_connections'])} connections")
    
    print(f"Completed! Sent {cn_rq_cnt} connection requests.")
    return profile_urls


if __name__ == "__main__":
    run_connection_bot()
