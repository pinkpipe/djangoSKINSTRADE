import asyncio
import logging
import re

import aiohttp
import requests

logger = logging.getLogger(__name__)

price_cache = {}


async def fetch_price(session, market_hash_name):
    if market_hash_name in price_cache:
        logger.debug(f"Price from cache for: {market_hash_name}")
        return price_cache[market_hash_name]

    url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=5&market_hash_name={market_hash_name}"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("success", False):
                    price = data.get("median_price")
                    if price:
                        try:
                            cleaned_price = re.sub(r"[^\d.]", "", price)
                            price = float(cleaned_price)
                            price_cache[market_hash_name] = (
                                price  # Добавляю в КЭШ прайс
                            )
                            return price
                        except ValueError:
                            logger.error(f"Could not convert price: {price}")
                            return None
                    else:
                        return None
                else:
                    logger.warning(f"Market price not found for {market_hash_name}")
                    return None
            else:
                logger.error(
                    f"Failed to fetch price for {market_hash_name}. Status code: {response.status}"
                )
                return None
    except Exception as e:
        logger.error(f"Error fetching price for {market_hash_name}: {e}")
        return None


async def fetch_all_prices(market_hash_names):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_price(session, name) for name in market_hash_names]
        prices = await asyncio.gather(*tasks)
        return prices


def get_steam_inventory(steam_id, game_id="252490"):
    url = f"https://steamcommunity.com/inventory/{steam_id}/{game_id}/2"
    try:
        response = requests.get(url)
        logger.info(f"Steam API Response Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Received inventory data: {bool(data)}")
            return data
        else:
            logger.error(
                f"Failed to get inventory. Status code: {response.status_code}"
            )
            return None
    except Exception as e:
        logger.error(f"Error getting inventory: {str(e)}")
        return None


def parse_inventory_items(inventory_data):
    if not inventory_data:
        logger.error("No inventory data provided")
        return []

    if "assets" not in inventory_data or "descriptions" not in inventory_data:
        logger.error("Invalid inventory data structure")
        return []

    try:
        items = []
        assets = inventory_data["assets"]
        descriptions = {
            f"{d['classid']}_{d['instanceid']}": d
            for d in inventory_data["descriptions"]
        }
        market_names = [
            descriptions[f"{asset['classid']}_{asset['instanceid']}"].get(
                "market_name", ""
            )
            for asset in assets
            if f"{asset['classid']}_{asset['instanceid']}" in descriptions
        ]
        prices = asyncio.run(fetch_all_prices(market_names))

        logger.info(f"Found {len(assets)} assets and {len(descriptions)} descriptions")

        for asset, price in zip(assets, prices):
            key = f"{asset['classid']}_{asset['instanceid']}"
            if key in descriptions:
                description = descriptions[key]
                market_name = description.get("market_name", "")

                if price is not None:
                    formatted_price = f"{price:.2f} ₽"
                else:
                    formatted_price = "Not Found"

                item = {
                    "asset_id": asset["assetid"],
                    "name": description.get("name", ""),
                    "market_name": market_name,
                    "icon_url": f"https://steamcommunity-a.akamaihd.net/economy/image/{description.get('icon_url', '')}",
                    "tradable": description.get("tradable", 0),
                    "marketable": description.get("marketable", 0),
                    "type": description.get("type", ""),
                    "wear": next(
                        (
                            tag.get("name")
                            for tag in description.get("tags", [])
                            if tag.get("category") == "Exterior"
                        ),
                        None,
                    ),
                    "rarity": next(
                        (
                            tag.get("name")
                            for tag in description.get("tags", [])
                            if tag.get("category") == "Rarity"
                        ),
                        None,
                    ),
                    "price": formatted_price,
                }
                items.append(item)
        logger.info(f"Parsed {len(items)} items")
        return items
    except Exception as e:
        logger.error(f"Error parsing inventory items: {str(e)}")
        return []
