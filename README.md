Here's a **README.md** file for your **Steam Price Tracker** project. It provides an overview, setup instructions, and usage details.

---

## 🕹️ Steam Price Tracker

This project is a **Steam Top Sellers Price Tracker** that scrapes the top 50 best-selling games from Steam, checks their current prices, and posts updates to a **Discord channel** using GitHub Actions.

This project is a minimalist CI/CD pipeline, you can use any API in this case we are using the steam API to get the top 30 best-selling games, checks their current prices, tracks discounts and posts updates to Discord channel using GitHub Actions.
### 📌 Features

- Scrapes the **top 30 best-selling games** on Steam.
- Fetches and tracks **game price changes**.
- Posts **daily price updates** to a Discord channel.
- Automates everything using **GitHub Actions**.

---

## 🚀 How It Works

1. **Scraper (Python)**
    
    - Extracts the top 50 games from [Steam’s Top Sellers](https://store.steampowered.com/search/?filter=topsellers).
    - Retrieves price data via Steam’s API.
    - Saves the data to `notification.json`.
2. **GitHub Actions**
    
    - Runs the scraper **daily** at 12:00 UTC or 17:00ET.
    - After the scrapper script finish and generates the `notification.json`, this triggers the discord action to post the message to a channel.

---

##  Setup & Usage

###  1. Clone the Repository

```sh
git clone https://github.com/yourusername/steam-price-tracker.git
cd steam-price-tracker
```

###  2.Set Up Python Environment

```sh
pip install -r requirements.txt
```

### 3. Run the Scraper Manually

```sh
python tracker.py
```

This generates `notification.json` with the latest price updates.

### 4️. Configure GitHub Secrets

In your **GitHub repository settings**, add a secret named:

- **`DISCORD_WEBHOOK`** → Your Discord Webhook URL.

### 5️. Enable GitHub Actions

- The workflow runs **automatically** every day at 13:00 UTC.
- You can trigger it manually from the **GitHub Actions** tab.
## Requirements to use GitHub Actions

### 1. Create a Personal access token

![[Pasted image 20250211205932.png]]

### 2. Get the webhook URL from Discord

![[Pasted image 20250211210244.png]]

### 3. Setup secrets for the token and the webhook
![[Pasted image 20250211210146.png]]

---

## 📌 GitHub Actions Workflow
### Action for the python script:

```yaml
name: Steam Price Tracker

on:
  schedule:
    - cron: '0 12 * * *'  # runs at 5PM ET 12AM UTC https://crontab.guru/
  workflow_dispatch:  # Allows manual trigger

jobs:
  track-prices:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: pip install -r requirements.txt

      - name: Run Steam Price Tracker
        run: python tracker.py 

      - name: Commit and Push Price Updates
        run: |
          git config --global user.name "encs16"
          git config --global user.email "encs16@users.noreply.github.com"
          git add steam_prices.json notification.json
          git commit -m "Update Steam prices" || echo "No changes to commit"
          git push https://x-access-token:${{ secrets.GIT_PATH }}@github.com/encs16/steamTestPriceTracker.git main
```

### Action for Discord webhook:
- This action trigger a CURL request after the **Steam Price Tracker** action is completed at 12:00 UTC
```yaml
name: post in discord channel

on:
  workflow_run:
   workflows: ['Steam Price Tracker'] # Post the message each time the python script is completed.
   types:
    - completed
  workflow_dispatch:  

jobs:
  track_steam_prices:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Send Steam Prices to Discord
        run: |
          curl -X POST -H "Content-Type: application/json" \
          -d "@notification.json" \
          ${{ secrets.DISCORD_WEBHOOK }}
```

## Test the GitHub Action

### 1. Action completed
![[Pasted image 20250211210323.png]]
### 2. Message posted in discord channel
![[Pasted image 20250211210333.png]]
