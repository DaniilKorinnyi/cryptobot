import os
from handlers import *
from lib import *
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')

def check_crypto(a):
    url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={a}&CMC_PRO_API_KEY={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and a in data['data']:
            return True
    return False

def check_currency(a):
    url = f'https://pro-api.coinmarketcap.com/v1/fiat/map?CMC_PRO_API_KEY={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            currencies = [currency['symbol'] for currency in data['data']]
            if a in currencies:
                return True
    return False

def add_coin(message, bot):
    chat_id = message.chat.id
    coin_symbol = message.text.upper()
    if check(coin_symbol):
        favourite_coins = favourite.get(chat_id, [])
        favourite_coins.append(coin_symbol)
        favourite[chat_id] = favourite_coins
        bot.send_message(chat_id, f"Coin {coin_symbol} has been added to favourites.")
    else:
        bot.send_message(chat_id, f"Coin {coin_symbol} not found.")

def check(coin_symbol):
    url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={coin_symbol}&CMC_PRO_API_KEY={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and coin_symbol in data['data']:
            return True
    return False

def remove_coin(message, bot):
    chat_id = message.chat.id
    coin_symbol = message.text.upper()
    favourite_coins = favourite.get(chat_id, [])
    if coin_symbol in favourite_coins:
        favourite_coins.remove(coin_symbol)
        favourite[chat_id] = favourite_coins
        bot.send_message(chat_id, f"Coin {coin_symbol} has been removed from favourites.")
    else:
        bot.send_message(chat_id, f"Coin {coin_symbol} not found in your favourites list.")

def get_coin_price(coin_symbol):
    url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={coin_symbol}&CMC_PRO_API_KEY={API_KEY}'
    response = requests.get(url)
    data = response.json()
    if 'error' in data:
        return "Error getting cryptocurrency price."
    else:
        try:
            price = data['data'][coin_symbol]['quote']['USD']['price']
            return price
        except KeyError:
            return "Coin not found."
