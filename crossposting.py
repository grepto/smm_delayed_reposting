import os
import argparse
import vk_api
import requests
import telegram

VK_TOKEN = os.getenv('VK_TOKEN')
VK_GROUP_ID = os.getenv('VK_GROUP_ID')
VK_LOGIN = os.getenv('VK_LOGIN')
VK_ALBUM_ID = os.getenv('VK_ALBUM_ID')
TG_TOKEN = os.getenv('TG_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')
FB_TOKEN = os.getenv('FB_TOKEN')
FB_GROUP_ID = os.getenv('FB_GROUP_ID')

FB_URL = 'https://graph.facebook.com'

def upload_photo_vkontakte(image_path):
    vk_session = vk_api.VkApi(login=VK_LOGIN, token=VK_TOKEN)
    upload = vk_api.VkUpload(vk_session)
    photo = upload.photo(
        image_path,
        album_id=VK_ALBUM_ID,
        group_id=VK_GROUP_ID
    )
    return f'photo{photo[0]["owner_id"]}_{photo[0]["id"]}'


def post_vkontakte(message, image_path=None):
    vk_session = vk_api.VkApi(login=VK_LOGIN, token=VK_TOKEN)
    vk = vk_session.get_api()
    photo = upload_photo_vkontakte(image_path) if image_path else None
    vk.wall.post(
        owner_id=f'-{VK_GROUP_ID}',
        message=message,
        attachments=photo
    )


def post_telegram(message=None, image_path=None):
    bot = telegram.Bot(token=TG_TOKEN)
    if message:
        bot.send_message(chat_id=TG_CHAT_ID, text=message)
    if image_path:
        with open(image_path, 'rb') as image:
            bot.send_photo(chat_id=TG_CHAT_ID, photo=image)


def post_facebook_photo(caption, image_path):
    url = f'{FB_URL}/{FB_GROUP_ID}/photos'
    payloads = {
        'caption': caption,
        'access_token': FB_TOKEN
    }
    with open(image_path, 'rb') as image:
        file = {'upload_file': image}
        response = requests.post(url, data=payloads, files=file)
    response.raise_for_status()


def post_facebook_text(message):
    url = f'{FB_URL}/{FB_GROUP_ID}/feed'
    payloads = {
        'message': message,
        'access_token': FB_TOKEN
    }

    response = requests.post(url, data=payloads)
    response.raise_for_status()


def post_facebook(message, image_path=None):
    if image_path:
        post_facebook_photo(message, image_path)
    else:
        post_facebook_text(message)


def post(message=None, image_path=None):
    post_facebook(message, image_path)
    post_vkontakte(message, image_path)
    post_telegram(message, image_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crossposting to Vkontakte, Telegram and Facebook')
    parser.add_argument('message', type=str,
                        help='string of message')
    parser.add_argument('image_path', type=str,
                        help='path to image file')

    args = parser.parse_args()
    message = args.message
    image_path = args.image_path
    post(message, image_path)