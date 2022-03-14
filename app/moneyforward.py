import os
import time
import pandas as pd
from config import *

# Import Selenium
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By

def make_sample_df():
    expense_sample_data = [
            ['ペイペイ1', '2022/01/01', '300'],
            ['ペイペイ2', '2022/01/02', '400'],
            ['ペイペイ3', '2022/01/03', '500'],
    ]
    expense_sample_df = pd.DataFrame(expense_sample_data)
    expense_sample_df = expense_sample_df.set_axis(['store_name', 'date', 'expense'], axis=1)
    return expense_sample_df

def truncate_string(string, length, ellipsis='...'):
    return string[:length-1]

def start_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-popup-blocking")
    driver = webdriver.Remote(
            command_executor=os.environ['SELENIUM_ENDPOINT'],
            options = options
    )
    return driver

def login(driver, username, password):

    # Login to MoneyForward ID
    print("Opening login page")
    mf_id_login_url = "https://id.moneyforward.com/sign_in/email"
    driver.get(mf_id_login_url)
    time.sleep(4)

    # Enter E-mail
    title = driver.find_element(By.CLASS_NAME, "title").text
    print(title)

    e = driver.find_element(By.NAME, "mfid_user[email]")
    e.clear()
    e.send_keys(username)
    e.submit()

    # Enter Password
    time.sleep(4)
    title = driver.find_element(By.CLASS_NAME, "title").text
    print(title)
    e = driver.find_element(By.NAME, "mfid_user[password]")
    e.send_keys(password)
    print("Logging in ...")
    e.submit()
    time.sleep(5)

    # Login to MoneyForward ME
    mf_me_login_url = "https://moneyforward.com/sign_in/"
    e = driver.get(mf_me_login_url)
    
    # Click "このアカウントを使用する"
    time.sleep(5)
    title = driver.find_element(By.CLASS_NAME, "title").text
    print(title)
    e = driver.find_element(By.CLASS_NAME, "submitBtn")
    e.submit()
    time.sleep(5)

def logout(driver):
    mf_logout_url = "https://moneyforward.com/sign_out"
    driver.get(mf_logout_url)
    time.sleep(2)

def add_expense(driver, asset_name, df):

    print("口座一覧")
    mf_accounts_url = "https://moneyforward.com/accounts"
    driver.get(mf_accounts_url)
    time.sleep(5)

    driver.find_element(By.LINK_TEXT, asset_name).click()
    print("PayPayカード")


    for index, row in df.iterrows():

        usage_amount = row['expense']
        usage_date = row['date']
        usage_name = truncate_string(row['store_name'], 52) # MoneyForwardの「内容」は52文字まで

        print("入力 {}件目 ({}, {}, {})".format(index+1, usage_date, usage_name, usage_amount))

        driver.find_element(By.CLASS_NAME, "cf-new-btn").click()
        time.sleep(5)
        
        # Find form
        form = driver.find_element(By.ID, "form-user-asset-act")
        
        # Expense date
        e = form.find_element(By.NAME, "user_asset_act[updated_at]")
        e.clear()
        e.send_keys(usage_date)

        # Expense amount
        e = form.find_element(By.NAME, "user_asset_act[amount]")
        e.send_keys(str(usage_amount))

        # Expense content
        e = form.find_element(By.NAME, "user_asset_act[content]")
        e.send_keys(usage_name)

        # Submit form
        e.submit()
        time.sleep(5)


def main():
    try:
        df = make_sample_df()
        asset_name = "PayPayカード"

        driver = start_driver()
        login(driver=driver, username=mf_username, password=mf_password)
        add_expense(driver=driver, asset_name=asset_name, df=df)
        logout(driver=driver)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
