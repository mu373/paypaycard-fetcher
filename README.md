# paypaycard-fetcher

## Usage

```sh
docker-compose up -d

# Get statement for PayPay card
# Data will be saved as TSV in `/data` directory
docker-compose exec app python get-paypay-card-data.py --month 202202

# Import diffs to MoneyForward
docker-compose exec app python compare.py --month 202202 --delete-old-file

# Or, run two commands at once
# Month will automatically be decided based on current date (see code for details)
docker-compose exec app python run.py

docker-compose down
```

```crontab
# Schedule to run at 06:02 and 18:02 everyday
2 6,18 * * * docker-compose -f ~/docker/paypyacard-fetcher/docker-compose.yml run python python run.py
```