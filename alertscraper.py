import sys
import time
from datetime import datetime
import argparse
from pyotp import *
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, \
    ElementNotInteractableException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

modules_link = "https://app.cybersecuritysaasplatform.com/live/sc/home?type=alert"


def navigate_to_alerts():
    if testing:  # test an individual query
        # link to page for individual alert
        # driver.get("https://app.cybersecuritysaasplatform.com/live/#/?sc=k5vEkRC1yVHX1ue") #singlesectionalbnlegacy
        # driver.get("https://app.cybersecuritysaasplatform.com/live/#/?sc=k41neeWSCQ1Lstl")# singlesectionalbnlegacyextrasection
        # driver.get("https://app.cybersecuritysaasplatform.com/live/#/?sc=k6Ib8ed6Dmfe1SS")  # singlesectionalsebmodulesextrasection
        # driver.get("https://app.cybersecuritysaasplatform.com/live/#/?sc=k6Poie5rSxCEVZX") #multisectionalsebmodules
        # driver.get("https://app.cybersecuritysaasplatform.com/live/#/?sc=kqVeIkxq2A4zNl5") #singlesectionalsebmodules
        driver.get("https://app.cybersecuritysaasplatform.com/live/#/?sc=k2urognSwjORvVw") #testgettingorganization
        # driver.get("https://app.cybersecuritysaasplatform.com/live/#/?sc=k4cNJR9uWVTgLpN") #testgettingorganization2

        get_organization(0)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//a[@data-testid="dashboard-button-module:overview"]'))
        )
        print("MODULES PLATFORM - setting link to: " + modules_link)
        args.link = modules_link
    except TimeoutException:
        print("LEGACY PLATFORM - using link provided by user: " + args.link)

    driver.get(args.link)

    if args.multiorg:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "selectedOrgBtn"))
            )
            driver.find_element(By.ID, "selectedOrgBtn").click()
            time.sleep(2)
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "rf-checkbox__label"))
                )
                driver.find_element(By.XPATH, '//label[text()="All organizations"]').click()
                time.sleep(2)
            except TimeoutException:
                pass
        except TimeoutException:
            pass

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "matches"))
        )
        matches = str(driver.find_element(By.CLASS_NAME, "matches").get_attribute("innerHTML")).replace("(", ""). \
            replace(")", "")
    finally:
        pass

    for i in range(0, int(matches)):
        alert_dict[i] = {}
        for k in key_dict:
            alert_dict[i][k] = "NULL"

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rf-leftmenu__expandcollapse"))
        )
        if driver.find_elements(By.CLASS_NAME, "rf-leftmenu__expandcollapse"):
            driver.find_element(By.CLASS_NAME, "rf-leftmenu__expandcollapse").click()
    except ElementNotInteractableException:
        pass
    except TimeoutException:
        pass

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "moreButton"))
        )
        driver.find_element(By.CLASS_NAME, "moreButton").click()
        time.sleep(5)

        scroll_pause_time = 5
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    except TimeoutException:
        pass

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".rf-doclist-item-type-alert"))
        )
        alert_elems = driver.find_elements(By.CSS_SELECTOR, ".rf-doclist-item-type-alert")

        if int(matches) != int(len(alert_elems)):
            print("ERROR: Different number of matches (" + str(matches) +
                  ") to alert elements (" + str(len(alert_elems)) + ")")
            sys.exit()

        for i in range(0, len(alert_elems)):
            alert_elem = alert_elems[i]
            document_title = alert_elem.find_element(By.CLASS_NAME, "document-title").get_attribute("innerHTML"). \
                replace("&amp;", "&")
            document_info = alert_elem.find_element(By.CLASS_NAME, "document-info").get_attribute("innerHTML"). \
                replace("<span>", "&").replace("</span>", "")

            link = None
            while link is None:
                try:
                    link = alert_elem.find_elements(By.TAG_NAME, "a")[1]
                    ActionChains(driver).move_to_element(link).perform()
                    link = link.get_attribute("href")
                except StaleElementReferenceException:
                    link = alert_elem.find_elements(By.TAG_NAME, "a")[1]
                    ActionChains(driver).move_to_element(link).perform()
                    link = link.get_attribute("href")

            alert_dict[i]["name"] = document_title
            alert_dict[i]["link"] = link

            if "Deactivated" in document_info:
                alert_dict[i]["deactivated"] = "True"

            if "Threat View Alerting Rule" in document_info:
                alert_dict[i]["type"] = "Threat View Alerting Rule"
                alert_dict[i]["threat_urgency"] = document_info.split("·")[1]
            elif "New Events" in document_info:
                alert_dict[i]["type"] = "New Events"
            elif "New References" in document_info:
                alert_dict[i]["type"] = "New References"
            else:
                print("WARNING: UNKNOWN TYPE")
    finally:
        pass

    for i in range(0, len(alert_dict)):
        alert_dict[i]["num"] = str(i + 1)
        try:
            get_data_from_alerts(alert_dict[i]["link"], i)
        except IndexError as ex:
            print("***ERROR***: IndexError at " + str(i + 1))
            print(ex)
            alert_dict[i]["name"] = "***ERROR***: " + alert_dict[i]["name"]
        print("Processed " + str(i + 1) + " of " + str(len(alert_dict))
              + " - " + alert_dict[i]["name"]
              + " - " + alert_dict[i]["link"]
              + "\n----")


def get_priority(i):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rf-report-alert-edit__priority-check"))
        )
        if driver.find_element(By.CLASS_NAME, "rf-report-alert-edit__priority-check"). \
                find_element(By.CLASS_NAME, "rf-checkbox__checkbox").get_attribute("checked") == "true":
            alert_dict[i]["priority"] = "True"
    except TimeoutException:
        print("no priority found for element: " + str(i + 1))


def get_intel_goal(i):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rf-use-case-form-info__item"))
        )
        alert_dict[i]["intel_goal"] = driver.find_element(By.CLASS_NAME, "rf-use-case-form-info__item").text
    except TimeoutException:
        print("no intel goal found for element: " + str(i + 1))


def get_metadata(i):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Created by')]"))
        )
        created_elem = driver.find_element(By.XPATH, "//*[contains(text(), 'Created by')]")
        alert_dict[i]["created_by"] = created_elem.find_element(By.CLASS_NAME, "rf-nickname").text
        alert_dict[i]["created_date"] = created_elem.find_element(By.TAG_NAME, "time").text

        modified_elem = driver.find_element(By.XPATH, "//*[contains(text(), 'Modified by')]")
        alert_dict[i]["modified_by"] = modified_elem.find_element(By.CLASS_NAME, "rf-nickname").text
        alert_dict[i]["modified_date"] = modified_elem.find_element(By.TAG_NAME, "time").text
    except TimeoutException:
        print("no metadata found for element: " + str(i + 1))


def get_alerted_users(i):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rf-alert-recipients-list_button__label"))
        )
        driver.find_element(By.CLASS_NAME, "rf-alert-recipients-list_button__label").click()

        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "rf-alert-recipients__list"))
            )
            alert_dict[i]["users_alerted"] = driver.find_element(By.CLASS_NAME, "rf-alert-recipients__list"). \
                text.replace("\n", "; ")
            driver.find_element(By.XPATH, '//button[text()="Cancel"]').click()
        except TimeoutException:
            print("no alerted_users found for element: " + str(i + 1))
    except TimeoutException:
        print("no alerted_users found for element: " + str(i + 1))
    except ElementClickInterceptedException:
        print("***ERROR*** no alerted_users found for element: " + str(i + 1))
        alert_dict[i]["users_alerted"] = "***ERROR***"


def get_organization(i):
    try:
        WebDriverWait(driver, 2.5).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Organization')]/following-sibling::span"))
        )
        org_elem = driver.find_element(By.XPATH, "//span[contains(text(), 'Organization')]/following-sibling::span")
        alert_dict[i]["organization"] = org_elem.text
    except TimeoutException:
        print("no organization found for element (only present in multi-org legacy): " + str(i + 1))


def get_logic(i):
    text_elem = ""
    try:  # regular logic style
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-value='logic']"))
        )
        time.sleep(2)
        try:
            driver.find_element(By.XPATH, "//div[@data-value='logic']").click()
            text_elem = driver.find_elements(By.CLASS_NAME, "rf-rfq")[1].find_elements(By.TAG_NAME, "div")[0]. \
                text.replace("\n", "").replace("OR", " OR ").replace("AND", " AND ").replace("NOT", " NOT "). \
                replace("  ", " ")
        except ElementNotInteractableException:
            print("***ERROR*** in logic for element: " + str(i + 1))
            text_elem = "***ERROR***"

    except TimeoutException:
        try:  # AQB report logic style + multisectional
            if testing:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "kobra-patternform"))
                )
            else:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "kobra-patternform"))
                )

            sections = driver.find_elements(By.CLASS_NAME, "kobra-patternform")

            if len(sections) > 1:
                print("***MULTISECTIONAL***")
                is_multi = True
            else:
                is_multi = False

            els = driver.find_elements(By.TAG_NAME, "h4")
            els.reverse()
            for el in els:
                el.click()
            els.reverse()

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "kobra-patternform-item"))
            )

            all_labels = driver.find_elements(By.CLASS_NAME, "kobra-patternform-label-wrap")
            all_items = driver.find_elements(By.CLASS_NAME, "kobra-patternform-item")
            if len(all_labels) != len(all_items):
                print("Labels and items NOT the same length!")
                raise RuntimeError

            # TODO: this cannot currently handle multisectional mixed lengths e.g. legacy and legacy cyber, very rare?
            # TODO: replace with dict of event types and their lengths
            legacy_s_length = 21
            modules_s_length = 22
            legacy_cyber_s_length = 31
            modules_cyber_s_length = 32
            # legacy
            if len(all_labels) % legacy_s_length == 0:
                s_length = legacy_s_length
                s2_start = 7
                s3_start = 13
            # modules
            elif len(all_labels) % modules_s_length == 0:
                s_length = modules_s_length
                s2_start = 7
                s3_start = 14
            # legacy with cyber attack event type
            elif len(all_labels) % legacy_cyber_s_length == 0:
                s_length = legacy_cyber_s_length
                s2_start = 8
                s3_start = 18
            # modules with cyber attack event type
            elif len(all_labels) % modules_cyber_s_length == 0:
                s_length = modules_cyber_s_length
                s2_start = 12
                s3_start = 19
            else:
                print("Labels and items NOT equal to expected section length")
                raise RuntimeError

            for j in range(0, len(sections)):

                offset = j * s_length
                labels = all_labels[0 + offset:s_length + offset]
                items = all_items[0 + offset:s_length + offset]

                text_elems = ["" for x in range(0, len(labels))]
                for k in range(0, len(labels)):
                    if labels[k].text.strip() == "" or \
                            items[k].text.strip() == "" or \
                            len(items[k].find_elements(By.CLASS_NAME, "kobra-patternform-placeholder")) != 0:
                        continue
                    label = labels[k].text
                    item = items[k].text
                    text_elems[k] = label + ": " + \
                                    item.replace("\n", " ").replace("OR", "OR ").replace("AND", "AND ") \
                                        .replace("NOT", "NOT ").replace("Address", "address").replace("Add", "") \
                                        .replace("|", "").replace("  ", " ")
                sections_text = ""
                for k in range(0, len(text_elems)):
                    if k == 0 and "".join(text_elems[0:s2_start]) != "":
                        sections_text += "EVENTS: "
                    if k == s2_start and "".join(text_elems[s2_start:s3_start]) != "":
                        sections_text += "SOURCES: "
                    if k == s3_start and "".join(text_elems[s3_start:s_length]) != "":
                        sections_text += "EXCLUDE: "
                    if text_elems[k] != "":
                        sections_text += text_elems[k] + " --- "
                if is_multi:
                    sections_text = "MULTIQUERY" + str(j + 1) + ": " + sections_text
                if sections_text != "":
                    text_elem += sections_text + " +++ "

        except TimeoutException:
            print("no logic found for element:" + str(i + 1))
        except RuntimeError:
            print("***ERROR*** in logic for element: " + str(i + 1))
            text_elem = "***ERROR***"
        except ElementClickInterceptedException:
            print("***ERROR*** in logic for element: " + str(i + 1))
            text_elem = "***ERROR***"


    if text_elem != "":
        if testing:
            print(text_elem)
            sys.exit()
        alert_dict[i]["logic"] = text_elem


def get_alert_frequency(i, is_threat_type=False):
    if is_threat_type:
        class_type = "rf-alert-block"
    else:
        class_type = "interval-block"

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_type))
        )
        alert_dict[i]["alert_frequency"] = driver.find_element(By.CLASS_NAME, class_type). \
            text.replace("\n", " ")
    except TimeoutException:
        print("no alert_frequency found for element: " + str(i + 1))


def get_annotation(i):
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "report-annotation"))
        )
        alert_dict[i]["annotation"] = driver.find_element(By.CLASS_NAME, "report-annotation").text.replace("\n", " ")
        if alert_dict[i]["annotation"].strip() == "Add annotation":
            alert_dict[i]["annotation"] = "NULL"
    except TimeoutException:
        print("no annotation found for element: " + str(i + 1))


def get_description(i, is_threat_type=False):
    if is_threat_type:
        position = 0
    else:
        position = 1

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rf-use-case-form-row__value-wrap"))
        )
        alert_dict[i]["description"] = driver. \
            find_elements(By.CLASS_NAME, "rf-use-case-form-row__value-wrap")[position].text
    except TimeoutException:
        print("no description found for element: " + str(i + 1))


def get_data_from_alerts(link, i):
    driver.get(link)
    time.sleep(2)

    get_priority(i)
    get_intel_goal(i)
    get_metadata(i)
    get_annotation(i)
    get_alerted_users(i)

    # speeds things up to separate it out, will remove eventually when legacy becomes obsolete
    if args.multiorg:
        get_organization(i)

    if alert_dict[i]["type"] == "New Events":
        get_new_event_alert_type_data(i)
    elif alert_dict[i]["type"] == "New References":
        get_new_reference_alert_type_data(i)
    elif alert_dict[i]["type"] == "Threat View Alerting Rule":
        get_threat_view_event_type_data(i)


def get_new_event_alert_type_data(i):
    get_new_alert_type_data(i)


def get_new_reference_alert_type_data(i):
    get_new_alert_type_data(i)


def get_new_alert_type_data(i):
    get_alert_frequency(i)
    get_description(i)
    get_logic(i)


def get_threat_view_event_type_data(i):
    get_alert_frequency(i, True)
    get_description(i, True)


def login_to_site(username, password, secret):
    driver.get('https://app.cybersecuritysaasplatform.com/')

    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "loginButton").click()

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "code"))
        )
        secret = secret.replace(" ", "")
        if secret.isdigit():
            driver.find_element(By.ID, "code").send_keys(secret)
        else:
            driver.find_element(By.ID, "code").send_keys(TOTP(secret).now())
        driver.find_element(By.ID, "submit").click()
    except TimeoutException:
        print("no totp")


def write_dict_to_file():
    with open(args.outfile, 'w') as f:
        for key in key_dict:
            f.write(key + "\t ")
        f.write("\n")
        for i in range(0, len(alert_dict)):
            for key in key_dict:
                f.write(alert_dict[i][key] + "\t")
            f.write("\n")
    print("Successfully output to " + args.outfile)


def _parse_args():
    parser = argparse.ArgumentParser(description='perform an Alert Review')
    parser.add_argument(
        '--username',
        type=str,
        help='cybersecuritysaasplatform username as string',
        required=True)
    parser.add_argument(
        '--password',
        type=str,
        help='cybersecuritysaasplatform password as string',
        required=True)
    parser.add_argument(
        '--secret',
        type=str,
        help='cybersecuritysaasplatform TOTP secret as string')
    parser.add_argument(
        '--link',
        type=str,
        help='cybersecuritysaasplatform link to Edit Alerting Rules page')
    parser.add_argument(
        '--multiorg',
        help='Captures the organization each alert is assigned to, for multiorg clients',
        default=False,
        action='store_true')
    parser.add_argument(
        '--outfile',
        type=str,
        help='Name of the output txt file',
        default='alert_review_output.txt'
    )

    return parser.parse_args()


if __name__ == '__main__':
    start_time = datetime.now()
    print("START TIME: " + str(start_time))

    testing = False

    args = _parse_args()

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    alert_dict = {}
    key_dict = ["num", "name", "type", "link", "intel_goal", "alert_frequency", "users_alerted", "logic",
                "threat_urgency", "deactivated", "priority", "description", "annotation",
                "created_by", "created_date", "modified_by", "modified_date"]
    if args.multiorg:
        key_dict.insert(13, "organization")

    login_to_site(args.username, args.password, args.secret)
    navigate_to_alerts()
    write_dict_to_file()

    driver.quit()
    end_time = datetime.now()
    print("END TIME: " + str(end_time))
    print("PROCESS TIME: " + str((end_time - start_time)))
