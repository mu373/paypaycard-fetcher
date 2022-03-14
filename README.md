# paypaycard-fetcher

Get monthly statement of PayPay card, and import them to MoneyForward ME

## Usage

Running from command line

```sh
docker-compose up -d

# Get monthly statement of PayPay card
# Data will be saved as TSV in `/data` directory
docker-compose exec app python get-paypay-card-data.py --month 202202

# Import diffs to MoneyForward
docker-compose exec app python compare.py --month 202202 --delete-old-file

# Or, run two commands at once
# Month will automatically be decided based on current date (see code for details)
docker-compose exec app python run.py

docker-compose down
```

Scheduling with `cron`

```crontab
# Schedule to run at 06:02 and 18:02 everyday
2 6,18 * * * docker-compose -f ~/paypaycard-fetcher/docker-compose.yml run python python run.py
```

## Data sample
- See [data/paypay_sample.tsv](https://github.com/mu373/paypaycard-fetcher/blob/master/data/paypay_sample.tsv)
- File format: tab-separated values (TSV)
- Columns: `store_name`, `date`, `expense`

## Preparation
- Add `PayPay card` as a new asset in MoneyForward ME
    - [口座一覧](https://moneyforward.com/accounts/service_list) > 金融機関追加 > その他保有資産
        - 金融機関カテゴリ：`カード`
        - 金融機関名：`PayPayカード`
    - 「手入力で負債を追加」
        - 負債の種類：`クレジットカード利用残高`
        - 負債の名称や説明：`利用残高`
        - 現在の借入金額：`0`

## License
[MIT License](https://github.com/mu373/paypaycard-fetcher/blob/master/LICENSE)