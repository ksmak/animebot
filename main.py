from telebot import types
import telebot
from config import (
    TOKEN, 
    RECENT_RELEASE_ANIME_URL, 
    POPULAR_ANIME_URL, 
    DETAILS_ANIME_URL, 
    SEARCH_ANIME_URL, 
    GENRE_ANIME_URL, 
    MOVIES_ANIME_URL, 
    TOP_AIRIN_URL,
    GENRES_LIST, 
    EPISODE_LIST_PORTION, 
)
import requests
import os
import json

# global variables
anime_list = []
anime_number = 0
episode_list = []
episode_number = 0

bot = telebot.TeleBot(TOKEN)

# start
@bot.message_handler(commands=['start', 'help'])
def start(message):
    username = message.from_user.username
    
    welcome_message = f'<b>Welcome, {username}!</b>\nThis project is implemented using the free anime streaming ' \
            'restful API serving anime from GogoanimeGogoAnime API.'
    
    help_message = '\n Helper:' \
            '\n/release             - get receant episodes' \
            '\n/popular             - get popular anime' \
            '\n/search              - get anime search' \
            '\n/movies              - get anime movies' \
            '\n/top-airing          - get top airing' \
            '\n/genre <genre type>  - get anime genres' \
            '\n/favorite            - get favorite anime' \
            '\n\nEnjoy watching you!'
    
    msg = help_message
    
    if message.text == 'start':
        msg = welcome_message + help_message

    bot.send_message(message.chat.id, msg, parse_mode='html')   

# get recent release anime list
@bot.message_handler(commands=['recent'])
def get_recent(message):
    global anime_list
    global anime_number
    
    try:
        response = requests.get(RECENT_RELEASE_ANIME_URL)
        anime_list = response.json()
        anime_number = 0
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Sorry, i can\'t access api service')
        return 

    fields = [
        {"title":"Episode: ", "field":"episodeNum"}, 
        {"title":"SUB of DUB: ", "field":"subOrDub"}
    ]
    show_anime_detail(message, fields) 

# get popular anime list
@bot.message_handler(commands=['popular'])
def get_popular(message):
    global anime_list
    global anime_number
    
    try:
        response = requests.get(POPULAR_ANIME_URL)
        anime_list = response.json()
        anime_number = 0
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Sorry, i can\'t access api service')
        return

    fields = [
        {"title":"Released:", "field":"releasedDate"}
    ]
    show_anime_detail(message, fields) 

# search anime
@bot.message_handler(commands=['search'])
def search(message):
    global anime_list
    global anime_number
    
    cmds = message.text.split()
    if len(cmds) != 2:
        bot.send_message(message.chat.id, 'Sorry, I didn\'t understand your command')
        return

    try:
        response = requests.get(f'{SEARCH_ANIME_URL}?keyw={cmds[1]}')
        anime_list = response.json()
        anime_number = 0
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Sorry, i can\'t access api service')
        return    

    fields = [
        {"title":"Released:", "field":"status"}
    ]
    show_anime_detail(message, anime_list, fields) 

# get anime movies
@bot.message_handler(commands=['movies'])
def get_movies(message):
    global anime_list
    global anime_number
    
    try:
        response = requests.get(MOVIES_ANIME_URL)
        anime_list = response.json()
        anime_number = 0
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Sorry, i can\'t access api service')
        return    

    fields = [
        {"title":"Released:", "field":"releasedDate"}
    ]
    show_anime_detail(message, fields) 

# get top airing anime
@bot.message_handler(commands=['top-airing'])
def get_top_airing(message):
    global anime_list
    global anime_number
    
    try:
        response = requests.get(TOP_AIRIN_URL)
        anime_list = response.json()
        anime_number = 0
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Sorry, i can\'t access api service')
        return

    fields = [
        {"title":"Latest episode:", "field":"latestEp"}
    ]
    show_anime_detail(message, fields) 

# get genre anime
@bot.message_handler(commands=['genre'])
def get_genre(message):
    global anime_list
    global anime_number
    
    cmds = message.text.split()
    if len(cmds) != 2:
        bot.send_message(message.chat.id, 'Sorry, I didn\'t understand your command')
        return

    if cmds[1] not in GENRES_LIST:
        bot.send_message(message.chat.id, f'This genre is not available.\nList of available genres: {GENRES_LIST}')
        return

    try:
        response = requests.get(f'{GENRE_ANIME_URL}/{cmds[1]}')
        anime_list = response.json()
        anime_number = 0
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Sorry, i can\'t access api service')
        return    

    fields = [
        {"title":"Released:", "field":"releasedDate"}
    ]
    show_anime_detail(message, anime_list, fields) 

# get favorite anime list
@bot.message_handler(commands=['favorite'])
def get_favorite(message):
    global anime_list
    global anime_number
    
    username = message.from_user.username
    user_file = f'user_favorites\{username}.txt'

    try:
        anime_list = []
        if os.path.exists(user_file):
            f = open(user_file, "r")
            json_content = f.read()
            anime_list = json.loads(json_content)
            f.close()
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Sorry, i can\'t access user favorite file.')
        return

    if len(anime_list) == 0:
        bot.send_message(message.chat.id, 'Favorites list is empty.')
        return

    anime_number = 0
    fields = []

    show_anime_detail(message, fields, is_favorite=True) 

# show anime detail
def show_anime_detail(message, fields, is_favorite=False):
    global anime_number

    try:
        caption = f'<b>{anime_list[anime_number]["animeTitle"]}</b>'
        for field in fields:
            caption += f'\n{anime_list[anime_number][field]}'

        markup = types.InlineKeyboardMarkup()
        
        if is_favorite:
            markup.row(
                types.InlineKeyboardButton('📺 Episodes', callback_data=f'show_episodes'),
                types.InlineKeyboardButton('⭐ Remove from favorite', callback_data=f'add_favorite') 
            )
        else:
            markup.row(
                types.InlineKeyboardButton('📺 Episodes', callback_data=f'show_episodes'),
                types.InlineKeyboardButton('⭐ Add favorite', callback_data=f'add_favorite') 
            )

        if anime_number < len(anime_list) - 1:
            markup.row(
                types.InlineKeyboardButton('Next', callback_data=f'next') 
            )    
        
        show_photo(message, anime_list[anime_number]["animeId"], 
            anime_list[anime_number]["animeImg"], caption, markup)

    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, 'Sorry, i can\'t show anime details.')
        return

# show anime photo
def show_photo(message, anime_id, url, caption, markup):
    image_file = f'img/{anime_id}.png'

    if not os.path.exists(image_file):
        r = requests.get(url)
        with open(image_file, 'wb') as f:
            f.write(r.content)

    with open(image_file, 'rb') as f:
        bot.send_photo(message.chat.id, photo=f, caption=caption, reply_markup=markup, parse_mode='html')

# callback query
@bot.callback_query_handler(func=lambda call:True)
def buttons_handler(call):
    global anime_list
    global anime_number
    global episode_list
    global episode_number
    
    if call.data == 'show_episodes':
        try:
            response = requests.get(f'{DETAILS_ANIME_URL}/{anime_list[anime_number]["animeId"]}')
            anime_details = response.json(response)
            episode_list = anime_details["episodesList"]
            episode_number = 0
            show_episodes(call.message)

        except Exception as e:
            print(e)
            bot.send_message(call.message.chat.id, 'Sorry, i can\'t show anime episodes.')
            return

    elif call.data == 'add_favorite':
        add_favorite(call.message)

    elif call.data == 'next':    
        get_next(call.message)
    
# show anime episodes
def show_episodes(message):
    global anime_list
    global anime_number
    global episode_list
    global episode_number

    markup = types.InlineKeyboardMarkup(row_width=4)
    
    while episode_number < len(episode_list) - 1:
        markup.add(
            types.InlineKeyboardButton(f'Episode: {episode_list[episode_number]["episodeNum"]}', 
                url=episode_list[episode_number]["episodeUrl"])
        )
        episode_number += 1
        if (episode_number + 1) % EPISODE_LIST_PORTION == 0:
            break
    
    bot.send_message(message.chat.id, 'Last episodes: ', reply_markup=markup)     
    
    if episode_number < len(episode_list) - 1:
        markup.row(
            types.InlineKeyboardButton('📺 Next episodes', callback_data=f'show_episodes'),    
        )

# add anime to favorite list
def add_favorite(message):
    global anime_list
    global anime_number
    
    username = message.from_user.username
    user_file = f'user_favorites\{username}.txt'

    favorite_list = []
    if os.path.exists(user_file):
        try:
            f = open(user_file, "r")
            json_content = f.read()
            favorite_list = json.loads(json_content)
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, 'Sorry, I can\'t read user favorite file')
        finally:
            f.close()

    
    if is_not_duplicate(favorite_list, anime_list[anime_number]):
        anime_json = {
            "animeId": anime_list[anime_number]["animeId"],
            "animeTitle": anime_list[anime_number]["animeTitle"],
            "animeImg": anime_list[anime_number]["animeImg"],
        }
        favorite_list.append(anime_json)
        jsonString = json.dumps(favorite_list)
        try:
            f = open(user_file, "w")
            f.write(jsonString)
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, 'Sorry, I can\'t write user favorite file')    
        finally:    
            f.close()

# check duplicat element in list
def is_not_duplicate(elements, elem):
    for e in elements:
        if e["animeId"] == elem["animeId"]:
            return False
    return True        

# get next anime
def get_next(message):
    global anime_list
    global anime_number

    if anime_number >= len(anime_list) - 1:
        bot.send_message(message.chat.id, 'This is the last anime on the list.')
        return
    
    anime_number += 1

    show_anime_detail(message)

bot.set_my_commands([
    telebot.types.BotCommand("/start", "main menu"),
    telebot.types.BotCommand("/help", "print helper"),
    telebot.types.BotCommand("/release", "get receant episodes"),
    telebot.types.BotCommand("/popular", "get popular anime"),
    telebot.types.BotCommand("/search", "get anime search"),
    telebot.types.BotCommand("/movies", "get anime movies"),
    telebot.types.BotCommand("/top-airing", "get top airing"),
    telebot.types.BotCommand("/genre", "get anime genres"),
    telebot.types.BotCommand("/favorite", "get favorite anime"),

])

bot.infinity_polling()