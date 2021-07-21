import requests
import telebot
from telebot import types
import random
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Регистрируем бота
bot_API = "ur_bot_api"
bot = telebot.TeleBot(bot_API)

pokemon_name = ""
# Текущее состояние пользователя: играет он или нет
playing = False


# Обработчик команды /game
@bot.message_handler(commands=['game'])
def game(message):
    global playing
    global pokemon_name
    # Выбираем 6 случайных id покемонов
    numbers = range(1, 501)
    rand_nums = random.sample(numbers, 6)

    bot.send_message(message.chat.id, text="Подождите немного, мы ловим покемона для вас!",
                     reply_markup=types.ReplyKeyboardRemove())

    # Находим 6 случайных имён покемонов, первое из них будет ответом
    poke_names = []
    for i in rand_nums:
        url = "http://pokeapi.co/api/v2/pokemon/{}/".format(i)
        res = requests.get(url)
        data = res.json()
        pokemon_name = data["name"].capitalize()
        poke_names.append(pokemon_name)

    # Находим id первого покемона
    pokemon_id = rand_nums[0]
    url = "http://pokeapi.co/api/v2/pokemon/{}/".format(pokemon_id)

    print("url = ", url)
    res = requests.get(url)
    data = res.json()

    # Находим имя и изображение первого покемона
    img_url = data["sprites"]["other"]["dream_world"]["front_default"]
    print("img_url = ", img_url)
    pokemon_name = data["name"].capitalize()

    # Преобразуем изображение из SVG в PNG
    response = requests.get(img_url)
    file = open("pokemon.svg", "wb")
    file.write(response.content)
    file.close()

    drawing = svg2rlg("pokemon.svg")
    renderPM.drawToFile(drawing, 'pokemon.png', fmt='PNG')

    # Отпрааляем изображение и вопрос: это что за покемон?
    bot.send_photo(message.from_user.id,
                   photo=open("pokemon.png", "rb"))

    # Создаём клавиатуру с вариантами ответа
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    random.shuffle(poke_names)
    for item in poke_names:
        keyboard.add(item)

    bot.send_message(message.chat.id, text="Это что за покемон?", reply_markup=keyboard)

    # Включаем режим игры
    playing = True


# Обработчик всех текстовых сообщений от пользователя
@bot.message_handler(func=lambda message: True, content_types=['text'])
def check_answer(message):
    global playing
    # pokemon_name - это ожидаемый ответ
    global pokemon_name
    # Если человек играет, то расцениваем его сообщение как ответ,
    # если же не играет, предлагаем начать игру
    if not playing:
        bot.send_message(message.chat.id, 'Чтобы начать игру, введите команду /game')
    else:
        # Верный ответ
        if message.text == pokemon_name:
            bot.send_message(message.chat.id, 'Верно!', reply_markup=types.ReplyKeyboardRemove())
        # Неверный ответ
        else:
            bot.send_message(message.chat.id, "Нет, это " + pokemon_name + "!",
                             reply_markup=types.ReplyKeyboardRemove())

        # Создаём клавиатуру с клавишей начала новой игры
        rep_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        key_new_game = types.InlineKeyboardButton(text="/game")
        rep_keyboard.add(key_new_game)
        bot.send_message(message.chat.id, text="Чтобы сыграть ещё раз, нажмите кнопку /game", reply_markup=rep_keyboard)
    # Выводим человека из игры
    playing = False


bot.polling(none_stop=True, interval=0)
