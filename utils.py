"""Python imports"""
import os
import logging
from time import sleep
from datetime import datetime
import diff_match_patch as dmp_module
from jinja2 import Environment, FileSystemLoader
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions



# SET SELENIUM LOGGING LEVELS TO WARNING
logging.getLogger('selenium').setLevel(logging.WARNING)


# FOR RUNNING IN CHROME
def open_chrome_window():
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def get_changes(old_text: str, new_text: str) -> list[tuple[tuple, tuple]]:
    # DIFF MODULE OBJECT
    dmp = dmp_module.diff_match_patch()

    # GETTING DIFFERENCE BETWEEN THE SEQUENCES
    diff = dmp.diff_main(old_text, new_text)
    dmp.diff_cleanupSemantic(diff)

    # REMOVE UNCHANGED TEXT FROM CONTENT
    def filter_unchanged(content: tuple):
        if content[0] != 0:
            return content

    diff = map(filter_unchanged, diff)
    diff = [change for change in diff if change is not None]

    # GET REMOVALS AND ADDITIONS FROM CONTENTS
    removals = [change for change in diff if change[0] == -1]
    additions = [change for change in diff if change[0] == 1]

    # ZIP REMOVALS AND ADDITIONS AS PAIRS OF CHANGES
    changes = list(zip(removals, additions))

    return changes or None


def start_tracking(driver, original_text, stop_event) -> None:
    print('-> Tracking changes...')
    while not stop_event.is_set():
        # CHECK PERIODICALLY
        sleep(5)

        # CURRENT HTML AND BODY TEXT
        current_html = driver.page_source
        current_text = driver.find_element(By.TAG_NAME, "body").text.strip()

        # COMPARE ORIGINAL AND CURRENT
        changes = get_changes(original_text, current_text)

        # RECORD CHANGES TO FILE IF CHANGES EXIST
        if changes is not None:
            print('-> Changes detected, processing files...')
            # CREATE FILENAME FROM CURRENT TIMESTAMP
            timestamp = datetime.now().strftime("%Y_%m_%d [%H_%M_%S]")

            # CREATE CHANGES DIRECTORY
            os.makedirs('./Changes', exist_ok=True)
            filename = os.path.abspath(f"./Changes/{timestamp}.html")

            # Load the Jinja2 template environment; directory with HTML templates
            env = Environment(loader=FileSystemLoader('Changes'))

            # Report template
            template = env.get_template('template.html')

            print("-> Saving changes to file...")
            with open(filename, mode='w') as file:
                # Render template with variables and write changes to file
                file.write(template.render(
                    timestamp=timestamp,
                    changes=changes
                ))

            # SAVE NEW HTML FILE
            print("-> Saving new HTML file...")
            with open('new.html', 'w') as file:
                file.write(current_html)

            print('Done!')
            return

        driver.refresh()
        continue


if __name__ == "__main__":
    pass
