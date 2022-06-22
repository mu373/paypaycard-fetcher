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
        ["ペイペイ スーパー", "2022/03/25", "1000"],
        ["ペイペイ 書店", "2022/03/25", "3000"],
        ["ペイペイ コーヒー", "2022/03/25", "500"]
    ]
    columns = ["store_name", "date", "expense"]
    expense_sample_df = pd.DataFrame(expense_sample_data, columns=columns)

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
    driver.find_element(By.LINK_TEXT, "ログアウト").click()
    time.sleep(2)

def isNaN(obj):
    return obj != obj

def refresh_all(driver):
    print("Refreshing accounts...")

    mf_accounts_url = "https://moneyforward.com/accounts"
    driver.get(mf_accounts_url)
    time.sleep(5)

    driver.find_element(By.CLASS_NAME, "aggregation-queue-all").click()

def refresh_account(driver, account_name):
    print("Refreshing {}...".format(account_name))

    mf_accounts_url = "https://moneyforward.com/accounts"
    driver.get(mf_accounts_url)
    time.sleep(5)

    account_row = driver.find_element(By.CSS_SELECTOR, "#account-table").find_element(By.XPATH, "//tr[td[a[text()='{}']]]".format(account_name))
    account_row.find_element(By.XPATH, ".//form[input[@value='更新']]").click()


def add_expense(driver, asset_name, df):

    print("Adding expenses...")

    mf_accounts_url = "https://moneyforward.com/accounts"
    driver.get(mf_accounts_url)
    time.sleep(5)

    driver.find_element(By.LINK_TEXT, asset_name).click()

    for index, row in df.iterrows():

        usage_amount = row['expense']
        usage_date = row['date']
        if 'category_large_name' in row.keys():
            usage_category_large_name = row['category_large_name']
            usage_category_large_id = row['category_large_id']
            usage_category_middle_name = row['category_middle_name']
            usage_category_middle_id = row['category_middle_id']
        else:
            usage_category_large_id = float('NaN')
            usage_category_middle_id = float('NaN')
            usage_category_large_name = '未分類'
            usage_category_middle_name = '未分類'
        usage_name = truncate_string(row['store_name'], 52) # MoneyForwardの「内容」は52文字まで

        print("入力 {}件目 {}, {}, ¥{}, {}({}), {}({})".format(
            index+1, usage_date, usage_name, usage_amount,
            usage_category_large_name, usage_category_large_id,
            usage_category_middle_name, usage_category_middle_id
            )
        )

        new_button = driver.find_element(By.CLASS_NAME, "cf-new-btn")
        driver.execute_script("arguments[0].click();", new_button)
        time.sleep(5)
        
        # Find form
        form = driver.find_element(By.ID, "form-user-asset-act")
        
        # Expense date
        e = form.find_element(By.NAME, "user_asset_act[updated_at]")
        e.clear()
        e.send_keys(usage_date)

        # Expense category (large)
        if not isNaN(usage_category_large_id):
            e = form.find_element(By.NAME, "user_asset_act[large_category_id]")
            driver.execute_script("arguments[0].type='text';",e) # Value cannot be written when type='hidden'
            e.send_keys(str(usage_category_large_id))

        # Expense category (middle)
        if not isNaN(usage_category_middle_id):
            e = form.find_element(By.NAME, "user_asset_act[middle_category_id]")
            driver.execute_script("arguments[0].type='text';",e)  # Value cannot be written when type='hidden'
            e.send_keys(str(usage_category_middle_id))

        # Expense amount
        e = form.find_element(By.NAME, "user_asset_act[amount]")
        e.send_keys(str(usage_amount))

        # Expense content
        e = form.find_element(By.NAME, "user_asset_act[content]")
        e.send_keys(usage_name)

        # Submit form
        e.submit()
        time.sleep(5)


def get_categories(driver, asset_name):

    print("Getting categories...")

    mf_accounts_url = "https://moneyforward.com/accounts"
    driver.get(mf_accounts_url)
    time.sleep(5)

    driver.find_element(By.LINK_TEXT, asset_name).click()

    # Click 手入力 button
    driver.find_element(By.CLASS_NAME, "cf-new-btn").click()
    time.sleep(2)

    # Find form
    form = driver.find_element(By.ID, "form-user-asset-act")

    # Show category list
    form.find_element(By.CLASS_NAME, "btn_l_ctg").click()
    time.sleep(1)

    categories_ul = driver.find_element(By.CSS_SELECTOR, ".dropdown-menu.main_menu")
    categories_large_li = categories_ul.find_elements(By.CLASS_NAME, "dropdown-submenu")

    categories = []

    for category_large_li_item in categories_large_li:

        # 大分類
        category_large_a = category_large_li_item.find_element(By.CLASS_NAME, "l_c_name")
        category_large_name = category_large_a.get_attribute('text')
        category_large_id = category_large_a.get_attribute('id')

        category_middle_ul = category_large_li_item.find_element(By.CLASS_NAME, "sub_menu")
        category_middle_a = category_middle_ul.find_elements(By.CLASS_NAME, "m_c_name")
        for category_middle_a_item in category_middle_a:

            # 中分類
            category_middle_name = category_middle_a_item.get_attribute('text')
            category_middle_id = category_middle_a_item.get_attribute('id')

            category = [category_large_name, category_large_id, category_middle_name, category_middle_id]
            categories.append(category)

    category_columns = ["category_large_name", "category_large_id", "category_middle_name", "category_middle_id"]
    df_categories = pd.DataFrame(categories, columns=category_columns)
    df_categories['category_concat_name'] = df_categories['category_large_name'].str.cat(df_categories['category_middle_name'], sep="/")

    return (df_categories)

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
