from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# 今月使用分は翌月分として集計される
# 月末締めだがバッファとして2日前の日付を使用
fetch_date_dt = datetime.today() + relativedelta(months=1) - timedelta(days=2)
fetch_date_month = fetch_date_dt.strftime('%Y%m')

print(fetch_date_month)