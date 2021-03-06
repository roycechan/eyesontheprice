import utils
import urllib
from urllib.parse import urlparse
import logging

logging.basicConfig(
                    filename="logs",
                    filemode='a',
                    format='%(asctime)s - %(module)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    )
logging.getLogger().addHandler(logging.StreamHandler())
logger = logging.getLogger(__name__)

SHOPEE_PRICE_DENOMINATION = 100000

def extract_shopee_identifiers(url):
    # Identify whether app or web link
    # App Link
    parameters = {}
    if "product" in url:
        product_path = urlparse(url).path.split('/')
    # Web Link
    else:
        product_path = urlparse(url).path.split('.')
    parameters['itemid'] = product_path[-1]
    parameters['shopid'] = product_path[-2]
    return parameters


def get_shopee_json(url):
    parameters = extract_shopee_identifiers(url)
    search_url = utils.build_search_url(utils.SHOPEE_SEARCH_LINK, parameters)
    item_json = utils.retrieve_item_details_json(search_url)
    return item_json


def get_shopee_variants(item_json):
    # store item details in dict
    item_dict = {}
    item_dict['channel'] = 'shopee'
    item_dict['item_name'] = item_json['item']['name'].title()
    item_dict['item_id'] = str(item_json['item']['itemid'])
    item_dict['shop_id'] = str(item_json['item']['shopid'])

    item_dict['item_description'] = item_json['item']['description']
    item_dict['price_min'] = int(item_json['item']['price_min']) / SHOPEE_PRICE_DENOMINATION
    item_dict['price_max'] = int(item_json['item']['price_max']) / SHOPEE_PRICE_DENOMINATION
    item_dict['currency'] = item_json['item']['currency']
    item_dict['item_brand'] = item_json['item']['brand']
    item_dict['item_sold'] = int(item_json['item']['historical_sold'])
    item_dict['item_rating'] = item_json['item']['item_rating']['rating_star']
    item_dict['item_stock'] = int(item_json['item']['stock'])
    item_dict['categories'] = [i['display_name'] for i in item_json['item']['categories']]
    if item_json['item']['models']:
        item_dict['variant_ids'] = [str(i['modelid']) for i in item_json['item']['models']]
    else:
        item_dict['variant_ids'] = [str(item_dict['item_id'])]

    # Fetch variants
    variants_display = []
    variants = []
    for variant in item_json['item']['models']:
        variant_dict = {
            'channel': item_dict['channel'],
            'variant_id': str(variant['modelid']),
            'variant_name': variant['name'].title()[:100],
            'item_id': item_dict['item_id'],
            'item_name': item_dict['item_name'],
            'shop_id': item_dict['shop_id'],
            'current_price': int(variant['price']) / SHOPEE_PRICE_DENOMINATION,
            'currency_code': variant['currency'],
            'stock': int(variant['stock'])
        }
        option = (f"{variant_dict['variant_name']} - ${variant_dict['current_price']:.2f} ({variant_dict['stock']} left)")
        variants.append(variant_dict)
        variants_display.append(option)
    # if list is empty, display main product price
    if not variants:
        variant_dict = {
            'channel': item_dict['channel'],
            'variant_id': str(item_dict['item_id']),
            'variant_name': item_dict['item_name'].title()[:100],
            'item_id': str(item_dict['item_id']),
            'item_name': item_dict['item_name'],
            'shop_id': item_dict['shop_id'],
            'current_price': int(item_json['item']['price']) / SHOPEE_PRICE_DENOMINATION,
            'currency_code': item_dict['currency'],
            'stock': int(item_dict['item_stock'])
        }
        option = (f"{variant_dict['variant_name']} - ${variant_dict['current_price']:.2f} ({variant_dict['stock']} left)")

        variants.append(variant_dict)
        variants_display.append(option)

    return item_dict, variants, variants_display
