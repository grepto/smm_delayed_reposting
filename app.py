import calendar
import locale
import re
import datetime
import time
import os
from sheet import get_sheet, update_sheet_cell
from gdrive import get_file
from urllib.parse import urlparse
from crossposting import post_facebook, post_telegram, post_vkontakte

SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
RANGE_NAME = 'Лист1'
PUBLISHED_ATTRIBUTE_COLUMN = 'H'


def get_day_number_by_day_name(day_name):
    locale.setlocale(locale.LC_ALL, 'ru_RU')
    try:
        return list(calendar.day_name).index(day_name)
    except ValueError:
        return None


def get_url(string):
    pattern = re.compile('(http|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?')
    result = pattern.search(string)
    try:
        return result.group(0)
    except AttributeError:
        return None


def get_file_id(url):
    parsed_url = urlparse(url)
    return parsed_url.query[3:]


def get_post_plan():
    sheet = get_sheet(SPREADSHEET_ID, RANGE_NAME)
    header_shift_rows = 2
    index_number_rows_difference = 1
    post_plan = []
    for row in sheet[header_shift_rows:]:
        post = {
            'is_vkontakte': row[0] == 'да',
            'is_telegram': row[1] == 'да',
            'is_facebook': row[2] == 'да',
            'publish_day': get_day_number_by_day_name(row[3]),
            'publish_time': row[4],
            'post_file_id': get_file_id(get_url(row[5])),
            'post_image_id': get_file_id(get_url(row[6])),
            'is_published': row[7] == 'да',
            'sheet_row_number': sheet.index(row) + index_number_rows_difference
        }
        post_plan.append(post)
    return post_plan


def get_post_text(file_id):
    post_text_file = get_file(file_id, 'text/plain')
    if post_text_file:
        with open(post_text_file, 'r') as file:
            post_text = file.read()
        return post_text


def get_post_image(file_id):
    return get_file(file_id)


def get_post_to_publish(post_plan):
    now = datetime.datetime.now()
    return list(filter(lambda x: x['publish_day'] == now.weekday()
                                 and x['publish_time'] == now.hour
                                 and not x['is_published'],
                       post_plan)
                )


def set_post_is_published(post):
    published_attribute_cell = f"{RANGE_NAME}!{PUBLISHED_ATTRIBUTE_COLUMN}{post['sheet_row_number']}"
    update_sheet_cell(SPREADSHEET_ID, published_attribute_cell, 'да')


def publish_post(post):
    post_text = get_post_text(post['post_file_id'])
    post_image_file = get_post_image(post['post_image_id'])
    if post['is_vkontakte']:
        post_vkontakte(post_text, post_image_file)
    if post['is_facebook']:
        post_facebook(post_text, post_image_file)
    if post['is_telegram']:
        post_telegram(post_text, post_image_file)
    set_post_is_published(post)


def smm_delayed_reposting():
    while True:
        post_plan = get_post_plan()
        post_to_publish = get_post_to_publish(post_plan)
        for post in post_to_publish:
            publish_post(post)
        time.sleep(300)


if __name__ == '__main__':
    smm_delayed_reposting()
