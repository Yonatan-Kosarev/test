# -*- coding: utf-8 -*-
from telebot import types
import googletrans
import telebot
from googletrans import Translator
import random
import time
import psycopg2
import urllib.parse as url

bot = telebot.TeleBot("5775729535:AAEVKoZIeqZ0o0s-52ptmJwj95_aInKW2xc")

translator = Translator()
print(googletrans.LANGUAGES)
result = translator.translate('Привет', src='ru', dest='en')


path = "postgres://jfwxuyai:dFv7ECI8ETpN0Y8ig4KUH-TMMj63TtTo@jelani.db.elephantsql.com/jfwxuyai"
url.uses_netloc.append("postgres")
url_path = url.urlparse(path)
connection = psycopg2.connect(database=url_path.path[1:], user=url_path.username, password=url_path.password, host=url_path.hostname, port=url_path.port)


def table():
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS peoples(telegram_id BIGINT, record INT, score INT)")
    connection.commit()
    cursor.close()


@bot.message_handler(commands=["start"])
def greeting(message):
    hi = []
    i = 0
    while i < 15:
        result = random.choice(list(googletrans.LANGUAGES))
        if result not in hi:
            hi.append(result)
            i += 1
    for i in hi:
        bot.send_message(message.chat.id, translator.translate('hello', src='en', dest=i).text)
    bot.send_message(message.chat.id, "This is TelegramTranslateBot! You can translate from any language to any language with one command. /help")

@bot.message_handler(commands=["translate_info"])
def translate_info(message):
    bot.send_message(message.chat.id, "to translate write: /translate_(from language)_(to language)_(text) \n example: \n /translate_english_hebrew_I want chocolate")


@bot.message_handler(commands=["del_record"])
def del_record(message):
    cursor = connection.cursor()
    cursor.execute("UPDATE peoples SET record = %s WHERE telegram_id = %s", (0, message.chat.id,))
    bot.send_message(message.chat.id, "You delete your record... Your record: 0")
    connection.commit()


@bot.message_handler(commands=["top"])
def top(message):
    cursor = connection.cursor()
    cursor.execute("SELECT record FROM peoples WHERE record = (SELECT MAX(record) FROM peoples)")
    result = cursor.fetchone()
    bot.send_message(message.chat.id, "Max record = " + str(result[0]))

@bot.message_handler(commands=["del_score"])
def del_record(message):
    cursor = connection.cursor()
    cursor.execute("UPDATE peoples SET score = %s WHERE telegram_id = %s", (0, message.chat.id,))
    bot.send_message(message.chat.id, "You delete your score... Your score: 0")
    connection.commit()

@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id, "HELP MENU: \n 1) /translate_info - translate text")

def find_key(lg):
    for key, value in googletrans.LANGUAGES.items():
        if value.upper() == lg.upper():
            return key

    return "error"


def translate_text(message, from_lg, to_lg, text):
    print(4)
    if find_key(from_lg) == False or find_key(to_lg) == False:
        print(5)
        bot.send_message(message.chat.id, "Please check language")
        return
    result = translator.translate(text, src=find_key(from_lg), dest=find_key(to_lg))

    bot.send_message(message.chat.id, "Please wait...")
    time.sleep(0.5)
    bot.send_message(message.chat.id, "Your Translate: \n From " + from_lg + "\n To " + to_lg + "\n Text: " + text + "\n Translate: " + result.text)

def check_login(message):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM peoples WHERE telegram_id =%s", (message.chat.id, ))
    answer = bool(cursor.fetchone())
    connection.commit()
    cursor.close()
    return answer


@bot.message_handler(commands=["guess_translate_info"])
def guess_translate_info(message):
    if not check_login(message):
        cursor = connection.cursor()
        cursor.execute("INSERT INTO peoples (telegram_id, record, score) VALUES(%s, %s, %s)", (message.chat.id, 0, 0))
        connection.commit()
        cursor.close()

    bot.send_message(message.chat.id, "To start game write: /guess_translate (to language)")


def buttons(t_ans_tr, t_ans_en, var, message, lg):
    print(66)
    keyboard = types.InlineKeyboardMarkup()
    for i in range(4):
        print(77)
        if var[i] == t_ans_tr:
            callback_true = types.InlineKeyboardButton(text=var[i], callback_data="v_tr")
            keyboard.add(callback_true)
            print(88)
        else:
            callback_false = types.InlineKeyboardButton(text=var[i], callback_data="v_fl")
            keyboard.add(callback_false)
            print(99)
    bot.send_message(message.chat.id, "translate the word: " + t_ans_en + " to: " + lg +" and press the button", reply_markup=keyboard)
    # true_index = var.index(t_ans_tr)
    # calbacks = ["var1", "var2", "var3", "var4"]
    # calbacks[true_index] = "true"
    # print(var)
    # callback_USD = types.InlineKeyboardButton(text=var[0], callback_data="calbacks[0]")
    # callback_EUR = types.InlineKeyboardButton(text=var[1], callback_data="calbacks[1]")
    # callback_BYN = types.InlineKeyboardButton(text=var[2], callback_data="calbacks[2]")
    # callback_RUB = types.InlineKeyboardButton(text=var[3], callback_data="calbacks[3]")
    # keyboard = types.InlineKeyboardMarkup()
    # keyboard.add(callback_USD)
    # keyboard.add(callback_BYN)
    # keyboard.add(callback_RUB)
    # keyboard.add(callback_EUR)
    # bot.send_message(message.chat.id, "Нажми кнопку и узнай курс валюты", reply_markup=keyboard)
    print(111)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline_rates(call):
    # Если сообщение из чата с ботом
    print(call.data)
    if call.message:
        if call.data == "v_fl":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="False answer")
            cursor = connection.cursor()
            cursor.execute("SELECT score, record FROM peoples WHERE telegram_id =%s", (call.message.chat.id,))
            tim = cursor.fetchone()
            score = tim[0]
            record = tim[1]
            if score > record:
                cursor.execute("UPDATE peoples SET record = %s WHERE telegram_id = %s", (score, call.message.chat.id,))
                bot.send_message(call.message.chat.id, "You update your record! Your record: " + str(score))
                connection.commit()
            else:
                bot.send_message(call.message.chat.id, "Your record: " + str(record))
            cursor.execute("UPDATE peoples SET score = %s WHERE telegram_id = %s", (0, call.message.chat.id,))
            connection.commit()
            cursor.close()

        if call.data == "v_tr":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="True answer")
            cursor = connection.cursor()
            cursor.execute("SELECT score FROM peoples WHERE telegram_id =%s", (call.message.chat.id, ))
            score = cursor.fetchone()[0]
            score += 1
            cursor.execute("UPDATE peoples SET score = %s WHERE telegram_id = %s", (score, call.message.chat.id, ))

            bot.send_message(call.message.chat.id, "Your score: " + str(score))
            connection.commit()
            cursor.close()


def guess_translate(message, to_lg):
    print(11)
    if find_key(to_lg) == "error":
        print(22)
        return
    with open('eng_words.txt', 'r') as file:
        print(33)
        words = file.readlines()
        words = [s.strip("\n") for s in words]

        word = random.choice(words)

        result = translator.translate(word, src=find_key("english"), dest=find_key(to_lg))
        print(44)
        i = 0
        variants = []
        while i != 3:
            v = translator.translate(random.choice(words), src=find_key("english"), dest=find_key(to_lg))
            if v not in variants:
                variants.append(v.text)
                i += 1
        print(result.text)
        variants.insert(random.randint(0, 3), result.text)
    buttons(result.text, word, variants, message, to_lg)


print(7)
@bot.message_handler(content_types=["text"])
def translate(message):
    if "/translate" in message.text:
        print(8)
        try:
            print(6)
            from_language = message.text.split("_")[1]
            to_language = message.text.split("_")[2]
            text = message.text.split("_")[3]
            translate_text(message, from_language, to_language, text)
            return
        except:
            bot.send_message(message.chat.id, "Please check command")
    if "/guess_translate" in message.text:
        print(1)
        to_lg = message.text.split("_")[2]
        guess_translate(message, to_lg)
        return

        bot.send_message(message.chat.id, "Please check command")




bot.polling()