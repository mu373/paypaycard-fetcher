import subprocess
from subprocess import PIPE
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# 今月使用分は翌月分として集計される
# 月末締めだがバッファとして2日前の日付を使用
fetch_date_dt = datetime.today() + relativedelta(months=1) - timedelta(days=2)
fetch_date_month = fetch_date_dt.strftime('%Y%m')

print("Running for {}".format(fetch_date_month))

shell_command_paypay = """
python /app/get-paypay-card-data.py --month {}
""".format(fetch_date_month)

result_paypay = subprocess.run(shell_command_paypay, shell=True, stdout=PIPE, text=True)
print(result_paypay.stdout)

shell_command_compare = """
python /app/compare.py --month {} --delete-old-file --slack --add-category
""".format(fetch_date_month)

result_compare = subprocess.run(shell_command_compare, shell=True, stdout=PIPE, text=True)
print(result_compare.stdout)
