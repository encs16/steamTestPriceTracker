import requests
import json
from bs4 import BeautifulSoup

# Steam URLs
STEAM_TOP_SELLERS_URL = "https://store.steampowered.com/search/?filter=topsellers"
STEAM_API_URL = "https://store.steampowered.com/api/appdetails?appids={}&cc=us"
PRICE_FILE = "steam_prices.json"

# Get the top 50 games on the top seller section on steam
def get_top_sellers():
    response = requests.get(STEAM_TOP_SELLERS_URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    games = {}
    for result in soup.select(".search_result_row")[:50]:  # Get top 50 games from the STEAM API
        name = result.select_one(".title").text
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
            return None  # If says None means the game is unvailable or free

        price = price_data.get("final", 0) / 100  # Convert cents to dollars e.ig 120/100 = 1.2$
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
message = "Steam Price Tracker Updates:\n\n"

for game, appid in games.items():
    price_info = get_steam_price(appid)
    if price_info:
        price, discount = price_info

    prev_price = previous_prices.get(game, float("inf"))
    if isinstance(prev_price, dict):  # Ensure previous price is a float
        prev_price = prev_price.get("USD", float("inf"))
    
    new_prices[game] = price  # Store only the new USD price
    
    if price < prev_price:
        message += f"{game}: Now ${price} (Previous: ${prev_price}) - {discount}% OFF!\n"
    else:
        message += f"{game}: ${price} (No change)\n"
        
# Save updated prices
with open(PRICE_FILE, "w") as f:
    json.dump(new_prices, f, indent=4)

# Save message for GitHub Actions
with open("notification.txt", "w", encoding="utf-8") as f:
    f.write(message)

print("Steam prices updated successfully!")
