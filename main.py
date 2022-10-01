from email import message
from re import A
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
    TOP_AIRING_URL,
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
    username = message.from_user.first_name
    
    welcome_message = f'<b>Welcome, {username}!</b>\nThis project is implemented using the free anime streaming ' \
            'restful API serving anime from GogoanimeGogoAnime API.'
    
    help_message = '\n Helper:' \
            '\n\n/recent - get recent release episodes' \
            '\n\n/popular - get popular anime' \
            '\n\n/search - get anime search' \
            '\n\n/movies - get anime movies' \
            '\n\n/top_airing - get top airing' \
            '\n\n/genre - get anime genres' \
            '\n\n/favorite - get favorite anime' \
            '\n\n/help - get this helper'
    
    msg = help_message
    
    if message.text == '/start':
        msg = welcome_message + help_message + '\n\nEnjoy watching you!'

    bot.send_message(message.chat.id, msg, parse_mode='html')   

# get recent release anime list
@bot.message_handler(commands=['recent'])
def get_recent(message):
    show_anime_list(message=message, url=RECENT_RELEASE_ANIME_URL, title='Recent release anime list:')
    # try:
    #     response = requests.get(RECENT_RELEASE_ANIME_URL)
    #     anime_list = response.json()
    #     anime_number = 0
    # except Exception as e:
    #     print(e)
    #     bot.send_message(message.chat.id, 'Sorry, i can\'t access api service')
    #     return 

    # show_anime_detail(message) 

# get popular anime list
@bot.message_handler(commands=['popular'])
def get_popular(message):
    show_anime_list(message=message, url=POPULAR_ANIME_URL, title='Popular anime list:')
    # try:
    #     response = requests.get(POPULAR_ANIME_URL)
    #     anime_list = response.json()
    #     anime_number = 0
    # except Exception as e:
    #     print(e)
    #     bot.send_message(message.chat.id, 'Sorry, i can\'t access api service')
    #     return

    # show_anime_detail(message) 

# search anime
@bot.message_handler(commands=['search'])
def search(message):
    bot.send_message(message.chat.id, 'Enter search text:')
    bot.register_next_step_handler(message, search_handler)

# search next step handler
def search_handler(message):
    show_anime_list(message=message, url=f'{SEARCH_ANIME_URL}?keyw={message.text.lower()}', title='Found anime list:')
    # try:
    #     response = requests.get(f'{SEARCH_ANIME_URL}?keyw={message.text.lower()}')
    #     anime_list = response.json()
    #     anime_number = 0
    # except Exception as e:
    #     print(e)
    #     bot.send_message(message.chat.id, 'Sorry, i can\'t access api service')
    #     return    

    # show_anime_detail(message) 

# get anime movies
@bot.message_handler(commands=['movies'])
def get_movies(message):
    show_anime_list(message=message, url=MOVIES_ANIME_URL, title='Movies anime list:')
    # try:
    #     response = requests.get(MOVIES_ANIME_URL)
    #     anime_list = response.json()
    #     anime_number = 0
    # except Exception as e:
    #     print(e)
    #     bot.send_message(message.chat.id, 'Sorry, i can\'t access api service')
    #     return    

    # show_anime_detail(message) 

# get top airing anime
@bot.message_handler(commands=['top_airing'])
def get_top_airing(message):
    show_anime_list(message=message, url=TOP_AIRING_URL, title='Top airing anime list:')
    # try:
    #     response = requests.get(TOP_AIRING_URL)
    #     anime_list = response.json()
    #     anime_number = 0
    # except Exception as e:
    #     print(e)
    #     bot.send_message(message.chat.id, 'Sorry, i can\'t access api service')
    #     return

    # show_anime_detail(message) 

# get genre anime
@bot.message_handler(commands=['genre'])
def get_genre(message):
    bot.send_message(message.chat.id, f'Enter genre from the list:{GENRES_LIST}')
    bot.register_next_step_handler(message, genre_handler)

# genre anime next step handler
def genre_handler(message):
    if message.text.lower() not in GENRES_LIST:
        bot.send_message(message.chat.id, f'This genre is not available.\nList of available genres: {GENRES_LIST}')
        return
    
    show_anime_list(message=message, url=f'{GENRE_ANIME_URL}/{message.text.lower()}', title='Genre anime list:')
    # try:
    #     response = requests.get(f'{GENRE_ANIME_URL}/{message.text.lower()}')
    #     anime_list = response.json()
    #     anime_number = 0
    # except Exception as e:
    #     print(e)
    #     bot.send_message(message.chat.id, 'Sorry, i can\'t access api service')
    #     return    

    # show_anime_detail(message) 

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

    markup = types.InlineKeyboardMarkup()
    n = 0
    for anime in anime_list:
         markup.add(
             types.InlineKeyboardButton(anime["animeTitle"], callback_data=f'favorite_{n}')
         )
         n += 1
    bot.send_message(message.chat.id, 'Favorite anime list:', reply_markup=markup)

# show anime list
def show_anime_list(message, url, title):
    global anime_list
    global anime_number

    response = requests.get(url)
    anime_list = response.json()

    markup = types.InlineKeyboardMarkup(row_width=1)
    n = 0
    for anime in anime_list:
         markup.add(
             types.InlineKeyboardButton(anime["animeTitle"], callback_data=f'details_{n}')
         )
         n += 1
    bot.send_message(message.chat.id, title, reply_markup=markup)

# show anime detail
def show_anime_detail(message, is_favorite=False):
    global anime_number
    global episode_list
    
    if len(anime_list) == 0:
        bot.send_message(message.chat.id, 'List is empty')
        return

    try:
        r = requests.get(f'{DETAILS_ANIME_URL}/{anime_list[anime_number]["animeId"]}')
        anime = r.json()

        caption = f'<b>{anime["animeTitle"]}</b>' \
            f'\n<u>Synopsis:</u> {anime["synopsis"][:200]}' \
            f'\n<u>Type:</u> {anime["type"]}' \
            f'\n<u>Released:</u> {anime["releasedDate"]}' \
            f'\n<u>Status:</u> {anime["status"]}' \
            f'\n<u>Genres:</u> {anime["genres"]}' \
            f'\n<u>Total episodes:</u> {anime["totalEpisodes"]}'
        
        episode_list = anime["episodesList"]
                
        markup = types.InlineKeyboardMarkup()
        
        if is_favorite:
            markup.row(
                types.InlineKeyboardButton('📚 Episodes', callback_data=f'show_episodes'),
                types.InlineKeyboardButton('📗 Select episode', callback_data=f'select_episode'),
                types.InlineKeyboardButton('❌ Remove from favorite', callback_data=f'remove_favorite')
            )
        else:
            markup.row(
                types.InlineKeyboardButton('📚 Episodes', callback_data=f'show_episodes'),
                types.InlineKeyboardButton('📗 Select episode', callback_data=f'select_episode'),
                types.InlineKeyboardButton('⭐ Add favorite', callback_data=f'add_favorite')
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
    global episode_number
    
    if call.data == 'show_episodes':
        try:
            episode_number = 0
            show_episodes(call.message)
        except Exception as e:
            print(e)
            bot.send_message(call.message.chat.id, 'Sorry, i can\'t show anime episodes.')
            return
        return    
    elif call.data == 'next_episodes':
        try:
            show_episodes(call.message)
        except Exception as e:
            print(e)
            bot.send_message(call.message.chat.id, 'Sorry, i can\'t show anime episodes.')
            return
        return    
    elif call.data == 'select_episode':
        bot.send_message(call.message.chat.id, 'Enter episode number:')
        bot.register_next_step_handler(call.message, select_episode)
        return
    elif call.data == 'add_favorite':
        add_favorite(call.message)
        return
    elif call.data == 'remove_favorite':
        remove_favorite(call.message)    
        return

    for n in range(len(anime_list)):
        if call.data == f'details_{n}':
            anime_number = n
            show_anime_detail(call.message)
            return
    
    for n in range(len(anime_list)):
        if call.data == f'favorite_{n}':
            anime_number = n
            show_anime_detail(call.message, is_favorite=True)    
            return        
    
# show anime episodes
def show_episodes(message):
    global anime_list
    global anime_number
    global episode_list
    global episode_number

    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = []
    while episode_number < len(episode_list):
        buttons.append(
            types.InlineKeyboardButton(f'📺 {episode_list[episode_number]["episodeNum"]}', 
                url=episode_list[episode_number]["episodeUrl"])
        )

        if len(buttons) == 4:
            markup.row(*buttons)
            buttons = []

        if (episode_number + 1) % EPISODE_LIST_PORTION == 0:
            episode_number += 1
            break
    
        episode_number += 1
    
    if len(buttons) > 0:
        markup.row(*buttons)
    
    if episode_number < len(episode_list):
        markup.row(
            types.InlineKeyboardButton('Next episodes', callback_data=f'next_episodes'),    
        )

    bot.send_message(message.chat.id, 'Last episodes: ', reply_markup=markup)        

# select episode
def select_episode(message):
    n = -1
    try:
        n = int(message.text)
    except:
        bot.send_message(message.chat.id, 'The value must be an integer!')
        return    
    
    if n < 1 or n > len(episode_list):
        bot.send_message(message.chat.id, f'The value must be between 1 and {len(episode_list)}!')
        return 
    
    for episode in episode_list:
        if episode["episodeNum"] == str(n):
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton(f'📺 {episode["episodeNum"]}', 
                    url=episode["episodeUrl"])    

            )
            bot.send_message(message.chat.id, 'Selected episode: ', reply_markup=markup)  
            break
    
# add anime to favorite list
def add_favorite(message):
    global anime_list
    global anime_number
    
    username = message.chat.username
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
            bot.send_message(message.chat.id, 'The anime added to favorites.')
        except Exception as e:
            print(e)
            bot.send_message(message.chat.id, 'Sorry, I can\'t write user favorite file')    
        finally:    
            f.close()
    else:
        bot.send_message(message.chat.id, 'The anime already added to favorites.')        
            
# remove anime from favorites list
def remove_favorite(message):
    global anime_list
    global anime_number
    
    username = message.chat.username
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

    anime_json = {
        "animeId": anime_list[anime_number]["animeId"],
        "animeTitle": anime_list[anime_number]["animeTitle"],
        "animeImg": anime_list[anime_number]["animeImg"],
    }
    favorite_list.remove(anime_json)
    jsonString = json.dumps(favorite_list)
    try:
        f = open(user_file, "w")
        f.write(jsonString)
        bot.send_message(message.chat.id, 'The anime removed from favorites')
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

bot.set_my_commands([
    types.BotCommand("/start", "main menu"),
    types.BotCommand("/help", "print helper"),
    types.BotCommand("/recent", "get recent release episodes"),
    types.BotCommand("/popular", "get popular anime"),
    types.BotCommand("/search", "get anime search"),
    types.BotCommand("/movies", "get anime movies"),
    types.BotCommand("/top_airing", "get top airing"),
    types.BotCommand("/genre", "get anime genres"),
    types.BotCommand("/favorite", "get favorite anime"),

])

bot.infinity_polling()