# paypaycard-fetcher

Get monthly statement of PayPay card, and import them to MoneyForward ME

## Features
- Download monthly statement of PayPay card
- Import expense data to MoneyForward ME (only diffs would be imported from second time)
- Automatically classify expenses into categories (optional; user-defined category list required)
- Notify to Slack (optional; Webhook URL required)

## Usage

Running from command line

```sh
docker-compose up -d

# Get monthly statement of PayPay card
# Data will be saved as TSV in `/data` directory
docker-compose exec app python get-paypay-card-data.py --month 202202

# Import diffs to MoneyForward
# -h, --help: Show help
# -m MONTH, --month MONTH: Month, in YYYYMM format
# -d, --delete-old-file: Delete old files for month after importing to MoneyForward (2 latest files will be keeped) (optional)
# -s, --slack: Enable notification to Slack (optional)
# -c, --add-category: Add category to expense record based on store name, using pre-defined CSV (/app/category.csv) (optional)
docker-compose exec app python compare.py --month 202202 --delete-old-file --slack --add-category

# Or, run two commands at once
# Month will automatically be decided based on current date (see code for details)
docker-compose exec app bash run.sh

docker-compose down
```

Scheduling with `cron` of host machine

```crontab
# Schedule to run at 06:02 and 18:02 everyday
2 6,18 * * * docker-compose -f ~/paypaycard-fetcher/docker-compose.yml exec -T app bash run.sh
```

## Data sample
- See [data/paypay_sample.tsv](https://github.com/mu373/paypaycard-fetcher/blob/master/data/paypay_sample.tsv)
- File format: tab-separated values (TSV)
- Columns: `store_name`, `date`, `expense`

## Preparation
- Create `app/config.py`
    - Credentials for Yahoo! Japan and MoneyForward
    - Slack incoming webhook URL (optional, only if you want to notify to Slack)
- Create `app/category.csv` (optional)
    - Only if you want to have expense records to be classified into pre-defined categories
- Add `PayPay card` as a new asset in MoneyForward ME
    - [口座一覧](https://moneyforward.com/accounts/service_list) > 金融機関追加 > その他保有資産
        - 金融機関カテゴリ：`カード`
        - 金融機関名：`PayPayカード`
    - 「手入力で負債を追加」
        - 負債の種類：`クレジットカード利用残高`
        - 負債の名称や説明：`利用残高`
        - 現在の借入金額：`0`

## Debugging
- VNC can be used for debugging.
- As defined in `docker-compose.yml`, port 7900 of the container is mapped to port 7901 of the host machine for [noVNC](https://github.com/novnc/noVNC), a browser-based VNC client.
- Simply access http://localhost:7901/ to see the actual rendering from Selenium drivers in realtime.
- You can see details of VNC debugging at [SeleniumHQ/docker-selenium](https://github.com/SeleniumHQ/docker-selenium#using-your-browser-no-vnc-client-is-needed).

## Note
- The software will not work if 2FA is enabled for Yahoo! Japan ID and MoneyForward ID.
- IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## License
[MIT License](https://github.com/mu373/paypaycard-fetcher/blob/master/LICENSE)
