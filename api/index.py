import json
import os
import asyncio
from http.server import BaseHTTPRequestHandler
from tgtg import TgtgClient
from telegram.ext import ApplicationBuilder

basket_type = {
    "GROCERIES": "🍏"
}


async def send_message(available_baskets):
    application = ApplicationBuilder().token(os.environ.get('TELEGRAM_TOKEN')).build()
    text = [f"{basket['name']} | 🧺:  {basket['quantity']} " for basket in available_baskets]
    await application.bot.send_message(text="\n".join(text), chat_id=os.environ.get('CHAT_ID'))
    return


def get_baskets():
    client = TgtgClient(
        access_token=os.environ.get('TGTG_ACCESS_TOKEN'),
        refresh_token=os.environ.get('TGTG_REFRESH_TOKEN'),
        user_id=os.environ.get('TGTG_USER_ID')
    )
    favourites = client.get_items()
    available_baskets = []
    for favourite in favourites:
        if favourite['items_available']:
            available_baskets.append({ "name": favourite['display_name'], "quantity": favourite['items_available'] })
    return available_baskets


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            available_baskets = get_baskets()
            if len(available_baskets):
                asyncio.new_event_loop().run_until_complete(send_message(available_baskets))
        except Exception as ex:
            self.send_response(200)
            self.send_header('Content-type','text/json')
            self.end_headers()
            self.wfile.write(json.dumps({ "data": "Failed" }).encode(encoding='utf_8'))
            return
        self.send_response(200)
        self.send_header('Content-type','text/json')
        self.end_headers()
        self.wfile.write(json.dumps(available_baskets).encode(encoding='utf_8'))
        return
