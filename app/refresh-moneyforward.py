from config import *
import moneyforward as mf

import requests
import time

if __name__ == "__main__":

    try:
        driver = mf.start_driver()
        mf.login(driver=driver, username=mf_username, password=mf_password)
        mf.refresh_all(driver=driver)
    finally:
        mf.logout(driver=driver)
        driver.quit()

