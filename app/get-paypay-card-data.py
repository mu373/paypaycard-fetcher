import os
import sys
import time
import re
import pandas as pd
import datetime
import argparse
import urllib.parse

from config import *


# Parse arguments
parser = argparse.ArgumentParser(description='Retrieves expense information of PayPay card')
parser.add_argument('-m', '--month', required=True, help="Month (in YYYYMM format) or 'latest'")
args = parser.parse_args()

# Import Selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def start_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1')
    driver = webdriver.Remote(
            command_executor=os.environ['SELENIUM_ENDPOINT'],
            options = options
    )
    print("Starting driver...")
    return driver


def get_current_time():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    return now.strftime('%Y%m%d%H%M%S')

def login(driver, send_keys_only=False):
    if send_keys_only == False:
        driver.get("https://login.yahoo.co.jp/config/login")
    driver.find_element(By.ID, "login_handle").send_keys(paypay_username)
    driver.find_element(By.XPATH, "//button[text()='次へ']").click()
    time.sleep(1)
    driver.find_element(By.ID, "password").send_keys(paypay_password)
    driver.find_element(By.XPATH, "//button[text()='ログイン']").click()
    print("Logging in...")
    time.sleep(1)

def format_date(date_list):
    # convert date to YYYY-MM-DD
    date_formatted = "{y}/{m}/{d}".format(
        y=date_list[0],
        m=date_list[1].zfill(2),
        d=date_list[2].zfill(2)
    )
    return(date_formatted)

def open_member_top(driver):
    member_top_url = "https://www.paypay-card.co.jp/member/"
    driver.get(member_top_url)
    time.sleep(5)
    print("page title: {}".format(driver.title))

def open_latest_month(driver):

    # Member top
    open_member_top(driver)
    
    # Monthly top
    monthly_statement_top_url = "https://www.paypay-card.co.jp/member/statement/top"
    driver.get(monthly_statement_top_url)
    time.sleep(5)
    
    # Find and open latest month page
    # month_ul = driver.find_element(By.CLASS_NAME, "index_ListSettlement_NIWTA")
    month_ul = driver.find_element(By.CLASS_NAME, "_ListSettlement_1kf6q_8")
    latest_month_element = month_ul.find_elements(By.CLASS_NAME, "_ListSettlement__list_1kf6q_8")[0]
    latest_month_element.click()
    time.sleep(10)


def get_monthly_detail(driver, month):

    global target_month

    # Open PayPay card member page
    # Monthly statements cannot be loaded properly without visiting this page
    is_logged_in_successful = False
    open_member_top(driver)

    # If login screen is shown again, enter credentials
    while is_logged_in_successful == False:

        if "ログイン" in driver.title:
            login(driver, send_keys_only=True)
            open_member_top(driver)
        else:
            is_logged_in_successful = True
    
    # If argument for month is equal to 'latest', find and open latest month page
    if month == 'latest':

        open_latest_month(driver)

        # Get target_month (YYYYMM) from URL parameter
        monthly_detail_url = driver.current_url
        queries = urllib.parse.urlparse(monthly_detail_url).query
        queries_dict = urllib.parse.parse_qs(queries)
        target_month = queries_dict['targetYm'][0]
    else:
        target_month = month
        monthly_detail_url = "https://www.paypay-card.co.jp/member/statement/monthly?targetYm={}".format(month)
        driver.get(monthly_detail_url)
        time.sleep(10)

    print("page title: {}".format(driver.title))

    try:
        # usage_ul = driver.find_element(By.CLASS_NAME, "index_ListSettlement_NIWTA")
        usage_ul = driver.find_element(By.CLASS_NAME, "_ListSettlement_1kf6q_8")
    except NoSuchElementException:
        sys.exit("No statement was found for the month.")
    
    usage_li = usage_ul.find_elements(By.CLASS_NAME, "_ListSettlement__list_1kf6q_8")
    result_list = []

    for usage_li_item in usage_li:

        store_name = usage_li_item.find_element(By.CLASS_NAME, "_ListSettlement__labelMain_1kf6q_43").text

        usage_date = usage_li_item.find_element(By.CLASS_NAME, "_ListSettlement__date_1kf6q_53").text
        usage_date_list = re.findall('(.*)年(.*)月(.*)日', usage_date)[0]
        usage_date_formatted = format_date(usage_date_list)

        price = usage_li_item.find_element(By.CLASS_NAME, "_ListSettlement__summary_1kf6q_61").text
        price = re.sub("\n|円|,", "", price)

        result = [store_name, usage_date_formatted, price]
        print(result)

        result_list.append(result)

    return(result_list)

def main():
    try:
        driver = start_driver()
        login(driver=driver)

        result_list = get_monthly_detail(driver=driver, month=args.month)

        column_name = ['store_name', 'date', 'expense']
        df = pd.DataFrame(result_list, columns=column_name)

        current_time = get_current_time()

        # target_month (YYYYMM) will be declared as global variable inside get_monthly_detail()
        print("target_month: {}".format(target_month))

        filename="../data/paypay_{}_{}.tsv".format(target_month, current_time)
        df.to_csv(filename, sep='\t', index=False)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
