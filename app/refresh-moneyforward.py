from config import *
import moneyforward as mf

import requests
import time

if __name__ == "__main__":

    try:
        driver = mf.start_driver()
        mf.login(driver=driver, username=mf_username, password=mf_password)
        mf.refresh_all(driver=driver)
        mf.refresh_account(driver=driver, account_name="モバイルSuica (My JR-EAST ID)")
        time.sleep(5)
    finally:
        mf.logout(driver=driver)
        driver.quit()

