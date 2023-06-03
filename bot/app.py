from flask import Flask
from handlers import *
from utils import *
from lib import *
import threading

app = Flask(__name__)


t = threading.Thread(target=bot.polling, daemon=True)
t.start()

if __name__ == '__main__':
    app.run()

