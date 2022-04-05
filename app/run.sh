#!/usr/bin/env bash

# fetch_date_month=$(python calculate-month.py)
fetch_date_month="latest"
echo "Running for $fetch_date_month"

# Get expense data of PayPay card
python get-paypay-card-data.py --month $fetch_date_month

# Add diffs to MoneyForward
python compare.py --month $fetch_date_month --delete-old-file --slack --add-category
