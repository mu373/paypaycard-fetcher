import subprocess
from subprocess import PIPE
from datetime import datetime, timedelta

fetch_date_dt = datetime.today() - timedelta(days=2)
fetch_date_month = fetch_date_dt.strftime('%Y%m')

print("Running for {}".format(fetch_date_month))

shell_command_paypay = """
python /app/get-paypay-card-data.py --month {}
""".format(fetch_date_month)

result_paypay = subprocess.run(shell_command_paypay, shell=True, stdout=PIPE, text=True)
print(result_paypay.stdout)

shell_command_paypay = """
python /app/compare.py --month {} --delete-old-file
""".format(fetch_date_month)

result_paypay = subprocess.run(shell_command_paypay, shell=True, stdout=PIPE, text=True)
print(result_paypay.stdout)