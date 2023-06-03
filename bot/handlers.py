import os
import telebot
from utils import *
from lib import *

load_dotenv()

bot = telebot.TeleBot(os.getenv('API_TOKEN'))
API_KEY = os.getenv('API_KEY')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '<b>Hello! I am a crypto bot that can help you get cryptocurrency prices, convert different currencies, and create your own portfolio of favourite coins to track.</b>', parse_mode='html')

@bot.message_handler(commands=['get'])
def start_get_price(message):
    chat_id = message.chat.id
    user_data[chat_id] = {'step': 'crypto_symbol'}
    bot.send_message(chat_id, "Which cryptocurrency price would you like to know?")

@bot.message_handler(func=lambda message: message.chat.id in user_data)
def process_get_price(message):
    chat_id = message.chat.id
    step = user_data[chat_id]['step']
    if step == 'crypto_symbol':
        crypto_symbol = message.text.upper()
        user_data[chat_id]['crypto_symbol'] = crypto_symbol
        url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={crypto_symbol}&CMC_PRO_API_KEY={API_KEY}'
        response = requests.get(url)
        data = response.json()
        if 'error' in data:
            error_message = data['status']['error_message']
            bot.send_message(chat_id, text=f"Error getting cryptocurrency price: {error_message}")
        else:
            try:
                price = data['data'][crypto_symbol]['quote']['USD']['price']
                bot.send_message(chat_id, text=f"Current price of {crypto_symbol}: {price} USD")
            except KeyError:
                bot.send_message(chat_id, text=f"Cryptocurrency {crypto_symbol} not found.")
        del user_data[chat_id]

@bot.message_handler(commands=['convert'])
def start_convert(message):
    chat_id = message.chat.id
    user_data_convert[chat_id] = {'step': 'amount'}
    bot.send_message(chat_id, "Enter the conversion amount")

@bot.message_handler(func=lambda message: message.chat.id in user_data_convert)
def process_convert(message):
    chat_id = message.chat.id
    step = user_data_convert[chat_id]['step']
    if step == 'amount':
        try:
            amount = float(message.text)
            user_data_convert[chat_id]['amount'] = amount
            user_data_convert[chat_id]['step'] = 'crypto_symbol'
            bot.send_message(chat_id, "Enter the currency")
        except ValueError:
            bot.send_message(chat_id, "Invalid amount format. Please enter a numerical value.")
    elif step == 'crypto_symbol':
        a = message.text.upper()
        if check_currency(a):
            user_data_convert[chat_id]['crypto_symbol'] = a
            user_data_convert[chat_id]['step'] = 'currency'
            bot.send_message(chat_id, "Enter the currency to convert to")
        elif check_crypto(a):
            user_data_convert[chat_id]['crypto_symbol'] = a
            user_data_convert[chat_id]['step'] = 'currency'
            bot.send_message(chat_id, "Enter the currency to convert to")
        else:
            bot.send_message(chat_id, "Currency not found")
    elif step == 'currency':
        currency = message.text.upper()
        a = currency
        user_data_convert[chat_id]['currency'] = currency
        currency = user_data_convert[chat_id]['currency']
        amount = user_data_convert[chat_id]['amount']
        crypto_symbol = user_data_convert[chat_id]['crypto_symbol']
        if check_crypto(a) or check_currency(a):
            url = f'https://pro-api.coinmarketcap.com/v1/tools/price-conversion?amount={amount}&symbol={crypto_symbol}&convert={currency}&CMC_PRO_API_KEY={API_KEY}'
            response = requests.get(url)
            data = response.json()
            if 'error' in data:
                bot.send_message(chat_id, text="Error converting currencies.")
            else:
                converted_amount = data['data']['quote'][currency]['price']
                converted_amount_str = "{:.8f}".format(converted_amount)
                bot.send_message(chat_id, text=f"{amount} {crypto_symbol} = {converted_amount_str} {currency}")
            del user_data_convert[chat_id]
        else:
            bot.send_message(chat_id, "Currency not found")

@bot.message_handler(commands=['add'])
def start_add_coin(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Enter the symbol of the coin you want to add to favourites.")
    bot.register_next_step_handler(message, add_coin, bot=bot)

@bot.message_handler(commands=['favourite'])
def show_favourite(message):
    chat_id = message.chat.id
    favourite_coins = favourite.get(chat_id, [])
    if favourite_coins:
        response = "Your favourite coins and their prices on the exchange:\n"
        for coin_symbol in favourite_coins:
            price = get_coin_price(coin_symbol)
            response += f"{coin_symbol}: {price} USD\n"
    else:
        response = "You don't have any favourite coins yet."
    bot.send_message(chat_id, response)

@bot.message_handler(commands=['remove'])
def start_remove_coin(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Enter the symbol of the coin you want to remove from favourites.")
    bot.register_next_step_handler(message, remove_coin, bot=bot)

@bot.message_handler(commands=['commands'])
def show_commands(message):
    chat_id = message.chat.id
    commands = [
        "/start - Start the bot",
        "/commands - Show all available commands",
        "/get - Get price",
        "/convert - Convert",
        "/add - Add a coin to favorites",
        "/remove - Remove a coin from favorites",
        "/favourite - Show favourite coins",
    ]
    response = "Available commands:\n" + "\n".join(commands)
    bot.send_message(chat_id, response)
