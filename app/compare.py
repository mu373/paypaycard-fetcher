from cmath import nan
import os
import sys
import subprocess
from io import StringIO
import pandas as pd
import argparse

from config import *
import moneyforward as mf

import requests
import time

# Parse arguments
parser = argparse.ArgumentParser(description='Retrieves expense information of PayPay card')
parser.add_argument('-m', '--month', required=True, help="Month, in YYYYMM format")
parser.add_argument('-d', '--delete-old-file', action='store_true', help="Delete old files for month after importing to MoneyForward (2 latest files will be keeped)")
parser.add_argument('-s', '--slack', action='store_true', help="Enable notification to Slack (optional)")
parser.add_argument('-c', '--add-category', action='store_true', help="Add category to expense record based on store name, using pre-defined CSV (/app/category.csv)")
args = parser.parse_args()

month = args.month
asset_name = "PayPayカード" # MoneyForwardでの登録名

category_preset_path = '/app/category.csv'

import pathlib

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

def get_user_category_preset(path):
    df = pd.read_csv(path)
    df['category_concat_name'] = df['category_large_name'].str.cat(df['category_middle_name'], sep="/")
    return df

def join_category_id(driver, df):

    if args.add_category == True:

        # If category.csv exists, join category ID to expense record
        if os.path.isfile(category_preset_path):

            # Driver should already be logged in to MoneyForward
            print("Category preset ({}) found...".format(category_preset_path))
            # Get categories from MoneyForward
            df_category_mf = mf.get_categories(driver=driver, asset_name=asset_name)[['category_concat_name', 'category_large_id', 'category_middle_id']]
            # Get user-defined category preset
            df_category_preset = get_user_category_preset(category_preset_path)

            # Join category ID to category preset
            df_category_preset = pd.merge(df_category_preset, df_category_mf, on='category_concat_name', how='inner')

            # Join category ID to expense records
            df = pd.merge(df, df_category_preset, on='store_name', how='left')
        else:
            print("Category preset ({}) is not found!".format(category_preset_path))
            print("Proceeding without preset.")

    return df

def import_to_moneyforward(driver, df):

    # Driver should already be logged in to MoneyForward

    # Add expense records to MoneyForward
    mf.add_expense(driver=driver, asset_name=asset_name, df=df)

    delete_old_file()

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

def isNaN(obj):
    return obj != obj

def get_category_name(category_name):
    # Returns '未分類' if category_name is NaN
    if isNaN(category_name):
        category_name = "未分類"
    return category_name

def post_to_slack(df):

    if args.slack == True:

        slack_post_data = ""
        for index, row in df.iterrows():
            store_name = row["store_name"]
            date = row["date"]
            expense = int(row["expense"])

            # If category preset is given, use values from dataframe
            if 'category_large_name' in row.keys():
                category_large_name = row['category_large_name']
                category_middle_name = row['category_middle_name']
            # If not, categories will internally be processed as NaN, which will be recorded as '未分類' in MoneyForward
            else:
                category_large_name = float('NaN')
                category_middle_name = float('NaN')

            slack_post_data = slack_post_data + "{date}  {store_name}  (¥{expense:,})  {category_large}/{category_middle}\n".format(
                date=date, store_name=store_name, expense=expense,
                category_large=get_category_name(category_large_name),
                category_middle=get_category_name(category_middle_name)
            )

        payload = {
            "text" : "MoneyForwardに支出が追加されました",
            "attachments": [
                {
                    "color": "#36a64f",
                    "blocks": [
                        {
                            "type": "section",
                            "text": { 
                                "type": "mrkdwn",
                                "text": "*カード*\n{}".format(asset_name)
                            }
                        },
                        {
                            "type": "section",
                            "text": { 
                                "type": "mrkdwn",
                                "text": "*ご利用内容*\n{}".format(slack_post_data)
                            }
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": "<!date^{unixtime}".format(unixtime=int(time.time())) + "^{time}|Posted timestamp>",
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        requests.post(SLACK_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    df = load_data()
    # df = mf.make_sample_df()

    try:
        driver = mf.start_driver()
        mf.login(driver=driver, username=mf_username, password=mf_password)
        df = join_category_id(driver=driver, df=df)
        import_to_moneyforward(driver=driver, df=df)
    finally:
        mf.logout(driver=driver)
        driver.quit()

    post_to_slack(df)
