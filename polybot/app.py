import flask
from flask import request
import os
from bot import Bot, QuoteBot, ImageProcessingBot

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_APP_URL = os.environ['TELEGRAM_APP_URL']

@app.route('/', methods=['GET'])
def index():
    return 'Ok'

@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()

    # TODO: This is an attempt to be creative with the code but it hasn't worked well. Some more thought is needed here
    # msg = req["message"]
    # chat_id = msg["chat"]["id"]

    # if bot.is_current_msg_photo(msg):
    #     img_bot = bot.create_child("image", chat_id)
    #     img_bot.handle_message(msg)
    # elif bot.is_a_reply(msg):
    #     quote_bot = bot.create_child("quote", chat_id)
    #     quote_bot.handle_message(msg)
    # else:
    bot.handle_message(req["message"])
    return 'Ok'

if __name__ == "__main__":
    bot = ImageProcessingBot(TELEGRAM_TOKEN, TELEGRAM_APP_URL)

    app.run(host='0.0.0.0', port=8443)
