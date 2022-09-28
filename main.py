from telebot import types
import telebot
from config import BASE_URL, EPISODE_LIST_PORTION, RECENT_RELEASE_ANIME_URL, TOKEN, POPULAR_ANIME_URL, ANIME_LIST_PORTION
import requests
import os
import json

# global variables

# get recent release list
response = requests.get(RECENT_RELEASE_ANIME_URL)
recent_release_anime_list = response.json()
# get popular list
response = requests.get(POPULAR_ANIME_URL)
popular_anime_list = response.json()
# anime number where break cycle
anime_number = 0
# episode number where break cycle
episode_number = 0
# episode list
episode_list = []
# favorit number where break cycle
favorit_number = 0


bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(True)
    button_recent_release_list = types.KeyboardButton('recent release list')
    button_popular_list = types.KeyboardButton('popular list')
    button_favorites_list = types.KeyboardButton('favorites list')
    button_random_anime = types.KeyboardButton('random anime')
    button_search = types.KeyboardButton('seach')
    markup.row(button_recent_release_list,button_popular_list)
    markup.row(button_favorites_list, button_random_anime)
    markup.row(button_search)
    welcome_message = '<b>Welcome!</b>\nThis project is implemented using the free anime streaming ' \
        'restful API serving anime from GogoanimeGogoAnime API.\nEnjoy watching you!'
    bot.send_message(message.chat.id, welcome_message, parse_mode='html', reply_markup=markup)    


@bot.message_handler(content_types=['text'])
def get_user_text(message):
    global anime_number
        
    if message.text == 'recent release list':
        anime_number = -1
        __show_recent_release_list(message)
    elif message.text == 'popular list':    
        anime_number = -1
        __show_popular_list(message)
    elif message.text == 'favorites list':
        __show_favorit_list(message)    


@bot.callback_query_handler(func=lambda call:True)
def buttons_handler(call):
    global recent_release_anime_list
    global popular_anime_list
    global episode_list
    global episode_number
    
    if call.data == 'next_recent_release':
        __show_recent_release_list(call.message)
    elif call.data == 'next_popular':
        __show_popular_list(call.message)    
    elif call.data == 'next_episodes':
        __show_anime_episode_buttons(call.message, episode_list)

    anime_list = []
    
    for anime in popular_anime_list:
        anime_json = {}
        anime_json["animeId"] = anime["animeId"]
        anime_json["animeImg"] = anime["animeImg"]
        anime_json["animeTitle"] = anime["animeTitle"]
        anime_list.append(anime_json)

    for anime in recent_release_anime_list:
        anime_json = {}
        anime_json["animeId"] = anime["animeId"]
        anime_json["animeImg"] = anime["animeImg"]
        anime_json["animeTitle"] = anime["animeTitle"]
        if __check_duplicate(anime_json, anime_list):
            anime_list.append(anime_json)
    
    for anime in anime_list:
        if call.data == f'list_{anime["animeId"]}':
            episode_number = 0
            __show_anime_detail(call.message, anime["animeId"])

        if call.data == f'add_{anime["animeId"]}':
            username = call.message.chat.username
            user_file = f'user_favorites\{username}.txt'

            user_favorites_list = []
            if os.path.exists(user_file):
                f = open(user_file, "r")
                json_content = f.read()
                user_favorites_list = json.loads(json_content)
                f.close()
            
            user_favorites_list.append(anime)
            jsonString = json.dumps(user_favorites_list)
            f = open(user_file, "w")
            f.write(jsonString)
            f.close()


def __check_duplicate(anime_json, anime_list):
    for a in anime_list:
        if anime_json["animeId"] == a["animeId"]:
            return False
    return True


def __show_anime(message, anime_id, anime_img, anime_title, anime_caption, markup):
    
    image_file = f'img/{anime_id}.png'

    __show_anime_photo(message, anime_img, image_file, anime_title)
    bot.send_message(message.chat.id, anime_caption, reply_markup=markup)


def __show_next_button(message, call_caption: str):
    markup_next = types.InlineKeyboardMarkup()
    markup_next.row(
        types.InlineKeyboardButton('Next', callback_data=call_caption)
    )
    bot.send_message(message.chat.id, 'for continue click on the <b>Next</b>', parse_mode='html', reply_markup=markup_next)


def __show_recent_release_list(message):
    global recent_release_anime_list
    global anime_number
    
    n = 0
    for anime in recent_release_anime_list:
        if n <= anime_number:
            n += 1
            continue
        try:
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton(' 📺 watch', callback_data=f'watch_{anime["animeId"]}', url=anime["episodeUrl"]),
                types.InlineKeyboardButton(' ➕ add to favorite', callback_data=f'add_{anime["animeId"]}')
            )
            __show_anime(
                message, 
                anime["animeId"], 
                anime["animeImg"], 
                anime["animeTitle"], 
                f'Episode num: {anime["episodeNum"]}',
                markup)
        except:
            anime_number = n + 1
            __show_next_button(message, 'next_recent_release')
            break

        n += 1

        if n > anime_number and n % ANIME_LIST_PORTION == 0:
            anime_number = n - 1
            __show_next_button(message, 'next_recent_release')
            break   


def __show_popular_list(message):
    global popular_anime_list
    global anime_number
    
    n = 0
    for anime in popular_anime_list:
        if n <= anime_number:
            n += 1
            continue

        # try:
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(' 🗒 series list', callback_data=f'list_{anime["animeId"]}'),
            types.InlineKeyboardButton(' ➕ add to favorite', callback_data=f'add_{anime["animeId"]}')
        )
        __show_anime(
            message, 
            anime["animeId"], 
            anime["animeImg"], 
            anime["animeTitle"], 
            f'Released date: {anime["releasedDate"]}',
            markup)
        # except:
        #     anime_number = n + 1
        #     __show_next_button(message, 'next_popular')
        #     break
        
        n += 1

        if n > anime_number and n % ANIME_LIST_PORTION == 0:
            anime_number = n - 1
            __show_next_button(message, 'next_popular')
            break   


def __show_anime_episode_buttons(message, episode_list):
    global episode_number

    markup = types.InlineKeyboardMarkup()
    buttons = []
    n = 0
    for episode in episode_list:
        if n <= episode_number:
            n += 1
            continue

        button = types.InlineKeyboardButton(
            f'Episode:{episode["episodeNum"]}', 
            callback_data=f'detail_{episode["episodeId"]}',
            url=episode["episodeUrl"])

        buttons.append(button)

        n += 1

        if n % EPISODE_LIST_PORTION == 0:
            break
    
    episode_number = n
    markup.row(buttons[0], buttons[1], buttons[2], buttons[3])
    markup.row(buttons[4], buttons[5], buttons[6], buttons[7])
    bot.send_message(message.chat.id, 'Last episodes: ', reply_markup=markup)     
    if episode_number < len(episode_list) - 1:
        __show_next_button(message, 'next_episodes')


def __show_anime_detail(message, anime_id):
    global episode_list
    global episode_number

    url = f'{BASE_URL}/anime-details/{anime_id}'
    r = requests.get(url)
    anime_detail = r.json()

    image_file = f'img/{anime_id}.png'

    __show_anime_photo(message, anime_detail["animeImg"], image_file, anime_detail["animeTitle"])

    episode_list = anime_detail["episodesList"]
    episode_number = -1
    __show_anime_episode_buttons(message, episode_list)


def __show_anime_photo(message, image_url, image_file, image_title):
    r = requests.get(image_url)

    if not os.path.exists(image_file):
        r = requests.get(image_url)
        with open(image_file, 'wb') as f:
            f.write(r.content)

    with open(image_file, 'rb') as f:
        bot.send_photo(message.chat.id, photo=f, caption=image_title)

def __show_favorit_list(message):
    global favorit_number

    username = message.from_user.username
    user_file = f'user_favorites\{username}.txt'

    user_favorites_list = []
    if os.path.exists(user_file):
        f = open(user_file, "r")
        json_content = f.read()
        user_favorites_list = json.loads(json_content)
        f.close()

    if len(user_favorites_list) == 0:
        bot.send_message(message.chat.id, 'Favorites list is empty.')
        return

    n = 0

    for anime in user_favorites_list:
        if n <= favorit_number:
            n += 1
            continue

        try:
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton(' 🗒 series list', callback_data=f'list_{anime["animeId"]}'),
                types.InlineKeyboardButton(' ➕ add to favorite', callback_data=f'add_{anime["animeId"]}')
            )
            __show_anime(
                message, 
                anime["animeId"], 
                anime["animeImg"], 
                anime["animeTitle"], 
                f' ',
                markup)
        except:
            favorit_number = n + 1
            __show_next_button(message, 'next_favorit')
            break
        
        n += 1

        if n > anime_number and n % ANIME_LIST_PORTION == 0:
            favorit_number = n - 1
            __show_next_button(message, 'next_favorit')
            break   


bot.infinity_polling()