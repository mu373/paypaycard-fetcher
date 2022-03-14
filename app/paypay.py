import os
import time
import re
import pandas as pd
import datetime
from config import *

# Import Selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1')
driver = webdriver.Remote(
        command_executor=os.environ['SELENIUM_ENDPOINT'],
        options = options
)

print("Starting driver")

def get_current_time():
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    return now.strftime('%Y%m%d%H%M%S')

def login(driver):
    driver.get("https://login.yahoo.co.jp/config/login")
    driver.find_element(By.ID, "username").send_keys(paypay_username)
    driver.find_element(By.ID, "btnNext").click()
    time.sleep(1)
    driver.find_element(By.ID, "passwd").send_keys(paypay_password)
    driver.find_element(By.ID, "btnSubmit").click()
    print("logging in...")
    time.sleep(1)

def format_date(date_list):
    # convert date to YYYY-MM-DD
    date_formatted = "{y}/{m}/{d}".format(
        y=date_list[0],
        m=date_list[1].zfill(2),
        d=date_list[2].zfill(2)
    )
    return(date_formatted)

def get_monthly_detail(target_month, driver):
    # showSt: state (0=未確定、2=確定）
    monthly_detail_url = "https://www.paypay-card.co.jp/member/statement/monthly?targetYm={}".format(target_month)
    driver.get(monthly_detail_url)
    time.sleep(10)
    print("page title: {}".format(driver.title))

    usage_ul = driver.find_element(By.CLASS_NAME, "index_ListSettlement_NIWTA")
    usage_li = usage_ul.find_elements(By.CLASS_NAME, "index_ListSettlement__list_10XmM")
    result_list = []

    for usage_li_item in usage_li:

        store_name = usage_li_item.find_element(By.CLASS_NAME, "index_ListSettlement__labelMain_20cjQ").text

        usage_date = usage_li_item.find_element(By.CLASS_NAME, "index_ListSettlement__date_1jxtk").text
        usage_date_list = re.findall('(.*)年(.*)月(.*)日', usage_date)[0]
        usage_date_formatted = format_date(usage_date_list)

        price = usage_li_item.find_element(By.CLASS_NAME, "index_ListSettlement__summary_eJl4_").text
        price = re.sub("\n|円|,", "", price)

        result = [store_name, usage_date_formatted, price]
        print(result)

        result_list.append(result)

    return(result_list)


try:
    login(driver)

    target_month = "202203"
    result_list = get_monthly_detail(target_month, driver)

    column_name = ['store_name', 'date', 'expense']
    df = pd.DataFrame(result_list, columns=column_name)

    current_time = get_current_time()

    filename="../data/paypay_{}_{}.tsv".format(target_month, current_time)
    df.to_csv(filename, sep='\t', index=False)
finally:
    driver.quit()
