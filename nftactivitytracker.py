import logging
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler
import time
import requests
from opensea import OpenseaAPI
import config

bot = telegram.Bot(token=config.telegram_token)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def start(update, context):
    user = update.effective_user
    update.message.reply_markdown_v2(fr'Hi {user.mention_markdown_v2()} \! 👋')
    return -1

def help_command(update, context):
    update.message.reply_text('Type /track to start tracking.', parse_mode="HTML")
    return -1

def track(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    past_tx = []
    while True:
        contract_address = "0xBd3531dA5CF5857e7CfAA92426877b022e612cf8"
        collection_slug = "pudgypenguins"

        # Sales activity
        url = "https://api.opensea.io/api/v1/events?asset_contract_address=" + contract_address + "&collection_slug=" + collection_slug + "&event_type=successful&only_opensea=false&limit=20"
        headers = {"Accept": "application/json", "X-API-KEY": config.opensea_api}
        try:
            response = requests.request("GET", url, headers=headers)
            response = response.json()['asset_events']
            for sales in range(len(response)):
                tx_id = response[sales]['id']
                if tx_id not in past_tx:
                    price = int(response[sales]['total_price']) / 1000000000000000000
                    try:
                        buyer = response[sales]['transaction']['from_account']['user']['username']
                    except:
                        buyer = "None"
                    tx_hash = response[sales]['transaction']['transaction_hash']
                    try:
                        token_id = response[sales]['asset']['token_id']
                    except:
                        token_id = "BUNDLE"
                    try:
                        collection_name = response[sales]['asset']['collection']['name']
                    except:
                        collection_name = ""
                    try:
                        img_url = "https://api.opensea.io/api/v1/asset/" + contract_address + "/" + token_id
                        response1 = requests.request("GET", img_url, headers=headers)
                        img_url = response1.json()['image_preview_url']
                    except:
                        img_url = "https://logowik.com/content/uploads/images/ethereum3649.jpg"
                    try:
                        api1 = OpenseaAPI(config.opensea_api)
                        results = api1.collection(collection_slug=collection_slug)
                        results = results['collection']['stats']['floor_price']
                    except:
                        results = "Error retrieving data..."
                    address = "https://etherscan.io/tx/" + str(tx_hash)
                    address = '<a href="{}">{}</a>'.format(address, "Etherscan")
                    address2 = "https://opensea.io/assets/" + contract_address + "/" + str(token_id)
                    address2 = '<a href="{}">{}</a>'.format(address2, "OpenSea")
                    bot.sendPhoto(chat_id=config.telegram_chat_id,photo=img_url,caption=f"""💸 {buyer} purchased {collection_name} #{token_id} for <b>{price} ETH</b>\n(Current Floor: {results})\n{address} | {address2}""", parse_mode="HTML")
                    past_tx.append(tx_id)
            time.sleep(3)
        except Exception as e:
            print("Error occurred... possibly being rate limited... now waiting 30s...")
            print(e)
            time.sleep(30)
            
        # Listing activity
        url = "https://api.opensea.io/api/v1/events?asset_contract_address=" + contract_address + "&collection_slug=" + collection_slug + "&event_type=created&only_opensea=false&limit=20"
        headers = {"Accept": "application/json", "X-API-KEY": config.opensea_api}
        try:
            response = requests.request("GET", url, headers=headers)
            response = response.json()['asset_events']
            for listings in range(len(response)):
                tx_id = response[listings]['id']
                if tx_id not in past_tx:
                    price = int(response[listings]['ending_price']) / 1000000000000000000
                    try:
                        seller = response[listings]['seller']['user']['username']
                    except:
                        seller = "None"
                    try:
                        token_id = response[listings]['asset']['token_id']
                    except:
                        token_id = "BUNDLE"
                    try:
                        collection_name = response[listings]['asset']['collection']['name']
                    except:
                        collection_name = ""
                    try:
                        img_url = "https://api.opensea.io/api/v1/asset/" + contract_address + "/" + token_id
                        response1 = requests.request("GET", img_url, headers=headers)
                        img_url = response1.json()['image_preview_url']
                    except:
                        img_url = "https://logowik.com/content/uploads/images/ethereum3649.jpg"
                    try:
                        api1 = OpenseaAPI(config.opensea_api)
                        results = api1.collection(collection_slug=collection_slug)
                        results = results['collection']['stats']['floor_price']
                    except:
                        results = "Error retrieving data..."
                    address2 = "https://opensea.io/assets/" + contract_address + "/" + str(token_id)
                    address2 = '<a href="{}">{}</a>'.format(address2, "OpenSea")
                    bot.sendPhoto(chat_id=config.telegram_chat_id,photo=img_url,caption=f"""🆕 {seller} listed {collection_name} #{token_id} for <b>{price} ETH</b>\n(Current Floor: {results})\n{address2}""", parse_mode="HTML")
                    past_tx.append(tx_id)
            time.sleep(3)
        except Exception as e:
            print("Error occurred... possibly being rate limited... now waiting 30s...")
            print(e)
            time.sleep(30)
    return -1

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(config.telegram_token, workers = 32)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    dispatcher.run_async
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("track", track, run_async=True))
    
    # Start the Bot
    updater.start_polling()

if __name__ == '__main__':
    main()

