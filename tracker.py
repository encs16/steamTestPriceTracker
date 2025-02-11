import requests
import json
from bs4 import BeautifulSoup

# Steam URLs
STEAM_TOP_SELLERS_URL = "https://store.steampowered.com/search/?filter=topsellers"
STEAM_API_URL = "https://store.steampowered.com/api/appdetails?appids={}&cc=us"
PRICE_FILE = "steam_prices.json"

# Get the top 30 games on the top seller section on Steam
def get_top_sellers():
    response = requests.get(STEAM_TOP_SELLERS_URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    games = {}
    for result in soup.select(".search_result_row")[:30]:  # Get top 30 games
        name = result.select_one(".title").text.strip()
        appid = result["data-ds-appid"]
        games[name] = appid
    return games

# Fetch Prices using requests
def get_steam_price(appid):
    url = STEAM_API_URL.format(appid)
    response = requests.get(url)

    try:
        data = response.json().get(str(appid), {}).get("data", {})
        price_data = data.get("price_overview", {})

        if not price_data:
            return None  

        price = price_data.get("final", 0) / 100  
        discount = price_data.get("discount_percent", 0)
        return price, discount
    except json.JSONDecodeError:
        return None

# Load previous prices
try:
    with open(PRICE_FILE, "r") as f:
        previous_prices = json.load(f)
except FileNotFoundError:
    previous_prices = {}

# Get top sellers & check prices
games = get_top_sellers()
new_prices = {}
message_list = []  # List to store lines of the message

for game, appid in games.items():
    price_info = get_steam_price(appid)
    if price_info:
        price, discount = price_info

        prev_price = previous_prices.get(game, float("inf"))
        if isinstance(prev_price, dict):  # Ensure previous price is a float
            prev_price = prev_price.get("USD", float("inf"))

        new_prices[game] = price  # Store only the new USD price
        
        if price < prev_price:
            message_list.append(f"{game}: Now ${price:.2f} (Previous: ${prev_price:.2f}) - {discount}% OFF!")
        else:
            message_list.append(f"{game}: ${price:.2f} (No change)")

# Save updated prices
with open(PRICE_FILE, "w") as f:
    json.dump(new_prices, f, indent=4)

# Save message for GitHub Actions
notification_data = {"content": "\n".join(message_list)}

with open("notification.json", "w", encoding="utf-8") as f:
    json.dump(notification_data, f, ensure_ascii=False, indent=4)

print("Steam prices updated successfully! JSON ready for Discord Webhook.")
