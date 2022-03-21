import os
import sys
import subprocess
from io import StringIO
import pandas as pd
import argparse

from config import *
import moneyforward as mf


# Parse arguments
parser = argparse.ArgumentParser(description='Retrieves expense information of PayPay card')
parser.add_argument('-m', '--month', required=True, help="Month, in YYYYMM format")
parser.add_argument('-d', '--delete-old-file', action='store_true', help="Delete old file after importing to MoneyForward")
args = parser.parse_args()

month = args.month
asset_name = "PayPayカード" # MoneyForwardでの登録名

import pathlib
import pprint

def load_data():

    data_dir = pathlib.Path('/data')
    file_list = data_dir.glob('paypay_{}*.tsv'.format(month))

    file_list_str = [str(p.resolve()) for p in file_list]
    file_list_str = sorted(file_list_str, reverse=True)

    if len(file_list_str) == 1:
        data = file_list_str[0]
        print("Loading {}".format(data))
        df = pd.read_csv(data, sep="\t")
    else:
        new_file = file_list_str[0]
        old_file = file_list_str[1]
        print("Comparing '{}' and '{}' ...".format(new_file, old_file))

        data = get_diff(old_file=old_file, new_file=new_file)
        columns = ["store_name", "date", "expense"]
        df = pd.read_csv(data, sep="\t", header=None, names=columns)

    return df


def get_diff(old_file, new_file):
    shell_command = """
    diff {new} {old} | grep "^< " | sed "s/< //"
    """.format(new=new_file, old=old_file)

    diff_lines = subprocess.check_output(shell_command, shell=True, text=True)
    line_count = subprocess.check_output('wc -l', shell=True, input=diff_lines, text=True)
    line_count = line_count.rstrip()

    if (line_count) == "0":
        print("No diff found.")
        delete_old_file()
        sys.exit()

    diff_lines = StringIO(diff_lines)
    return diff_lines

def import_to_moneyforward(df):
    try:
        driver = mf.start_driver()
        mf.login(driver=driver, username=mf_username, password=mf_password)
        mf.add_expense(driver=driver, asset_name=asset_name, df=df)
        mf.logout(driver=driver)
        delete_old_file()
    finally:
        driver.quit()


def delete_old_file():

    if args.delete_old_file == True:

        data_dir = pathlib.Path('/data')
        file_list = data_dir.glob('paypay_{}_*.tsv'.format(month))

        file_list_str = [str(p.resolve()) for p in file_list]
        file_list_str = sorted(file_list_str, reverse=True)

        # Delete only when there is more than one file
        if len(file_list_str) > 2:
            old_files = file_list_str[2:]
            for old_file in old_files:
                print("Deleting {}".format(old_file))
                os.remove(old_file)

if __name__ == "__main__":
    df = load_data()
    # print(df)
    import_to_moneyforward(df)
