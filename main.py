import telebot
from telebot import types
import requests

#токен нашего бота
API_TOKEN = '7552526610:AAGp2-U726U28Sel59SKTQdHbu7retdljqQ'

bot = telebot.TeleBot(API_TOKEN)

# преподы в группе Программисты
teachers_prog = {
    'Харченко Никита Леонидович😎': 'Преподаватель введения в специальность и программирования на Python.',
    'Пташинский Игорь Андреевич🧔🏻‍♂️': 'Преподаватель истории и обществознания.',
    'Чихачёв Артем Аркадьевич🧔🏻‍♂️☁️': 'Преподаватель Интернет-маркетинга.',
    'Чиндяйкина Марина Сергеевна🦅': 'Преподаватель иностранного языка',
    'Фофанова Александра Владимировна': 'Преподаватель биологии и химии',
    'Лысогорский Иван Сергеевич': 'Преподаватель физкультуры и основы безопасности защиты Родины',
    'Волошин Александр Сергеевич': 'Конфигурирование Windows 10',

}

# преподы в группе "Дизайнеры"
teachers_diz = {
    'Потякина Валерия Андреевна🐈': 'Преподаватель математики, ОИТ, информатики.',
    'Игнатенко Екатерина Алексеевна✝️': 'Преподаватель истории искусств',
    'Пташинский Игорь Андреевич🛐🤠': 'Преподаватель истории, общества и основ Photoshop adapt',
    'Клименко Наталья Викторовна🦪🚷📵': 'Преподаватель географии',
    'Мамедова Наргиз Мехмановна👩‍🔬': 'Преподаватель химии',
    'Чиндяйкина Марина Сергеевна🦅': 'Преподаватель иностранного языка'
}


# /start
#@bot.message_handler(commands=['start'])
#def send_welcome(message):
    #bot.reply_to(message, f"Привет, {message.from_user.first_name}! Я твой помощник. Чем могу помочь?")


# /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    Доступные команды:
    /start - Приветствие
    /help - Эта помощь
    /teachers - Список преподавателей 
    /feedback - Оставить отзыв о преподавателе
    /view_feedback - Просмотреть отзывы
    /resources - полезные ресурсы для обучения
    """
    bot.reply_to(message, help_text)


# /resources
@bot.message_handler(commands=['resources'])
def resources_command(message):
    resources_text = """
    Полезные ресурсы для обучения:

    Программисты:
    1. Coursera - https://www.coursera.org/
    2. Codecademy - https://www.codecademy.com/
    3. Udemy - https://www.udemy.com/
    4. RealPython - https://realpython.com/
    5. GitHub - https://github.com/

    Дизайнеры:
    1. Canva - https://www.canva.com/
    2. Adobe Creative Cloud - https://www.adobe.com/creativecloud.html
    3. Behance - https://www.behance.net/
    4. Dribbble - https://dribbble.com/
    5. Skillshare - https://www.skillshare.com/
    """

    bot.reply_to(message, resources_text)




# URL API для авторизации на сайте колледжа
API_AUTH_URL = "https://journal.top-academy.ru/api/auth/login"  # Замените на реальный URL

# Словарь для хранения данных пользователей (в реальном проекте используйте базу данных)
user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Введите ваш логин и пароль в формате: логин:пароль")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # Проверяем, что ввод содержит двоеточие
        if ':' not in message.text:
            bot.reply_to(message, "Пожалуйста, введите данные в формате: логин:пароль")
            return

        # Разделяем логин и пароль
        login, password = message.text.split(':', maxsplit=1)

        # Отправляем запрос на API для авторизации
        response = requests.post(API_AUTH_URL, json={'login': login, 'password': password})

        # Проверяем ответ от API
        if response.status_code == 200:
            # Если авторизация успешна, сохраняем токен
            auth_token = response.json().get('token')
            user_data[message.chat.id] = auth_token
            bot.reply_to(message, "Авторизация успешна! Теперь вы можете использовать бота.")
        else:
            # Если авторизация не удалась, выводим сообщение об ошибке
            error_message = response.json().get('message', 'Ошибка авторизации. Проверьте ваш логин и пароль.')
            bot.reply_to(message, f"Ошибка: {error_message}")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

# Пример команды, которая требует авторизации
@bot.message_handler(commands=['protected'])
def protected_command(message):
    if message.chat.id in user_data:
        # Используем токен для авторизованного запроса
        auth_token = user_data[message.chat.id]
        bot.reply_to(message, f"Вы авторизованы! Ваш токен: {auth_token}")
    else:
        bot.reply_to(message, "Вы не авторизованы. Пожалуйста, авторизуйтесь.")


#  /teachers
@bot.message_handler(commands=['teachers'])
def list_teachers(message):
    teachers_list = ""
    for group, teachers in zip(['Программисты', 'Дизайнеры'], [teachers_prog, teachers_diz]):
        teachers_list += f"\nГруппа: {group}\n"
        for i, (name, desc) in enumerate(teachers.items()):
            teachers_list += f"{i + 1}. {name} - {desc}\n"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Главная', callback_data='home'))

    bot.reply_to(message, f"Доступные преподаватели:\n{teachers_list}", reply_markup=markup)


#  /feedback
@bot.message_handler(commands=['feedback'])
def feedback_command(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)

    all_teachers = list(set(list(teachers_prog.keys()) + list(teachers_diz.keys())))

    for teacher in all_teachers:
        keyboard.add(teacher)

    bot.send_message(message.chat.id, "Выберите преподавателя:", reply_markup=keyboard)


# Обработчик выбора преподавателя
@bot.message_handler(func=lambda message: message.text in set(list(teachers_prog.keys()) + list(teachers_diz.keys())))
def select_teacher(message):
    selected_teacher = message.text
    bot.send_message(message.chat.id, f"Введите ваш отзыв о {selected_teacher}:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, save_feedback, selected_teacher)


# Сохранение отзыва
def save_feedback(message, teacher):
    with open('feedback.txt', 'a+', encoding="utf-8") as file:
        file.write(f'{teacher}: {message.text}\n\n')
    bot.send_message(message.chat.id, "Ваш отзыв успешно сохранён!", reply_markup=types.ReplyKeyboardRemove())


# /view_feedback
@bot.message_handler(commands=['view_feedback'])
def view_feedback(message):
    try:
        with open('feedback.txt', 'r', encoding="utf-8") as file:
            feedback_content = file.read()
        if not feedback_content:
            bot.send_message(message.chat.id, "Отзывов пока нет.")
        else:
            bot.send_message(message.chat.id, "Отзывы:\n" + feedback_content)
    except FileNotFoundError:
        bot.send_message(message.chat.id, "Файл с отзывами не найден.")

# Обработка нажатий на кнопки
@bot.callback_query_handler(func=lambda q: q.data == 'home')
def teachers_home(query):
    bot.edit_message_text("Вы вернулись в главное меню.", query.message.chat.id, query.message.message_id,
                          query.message.reply_markup)


# Обработка сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Не понял ваше сообщение. Попробуйте ещё раз.")


# Запуск бота
if __name__ == '__main__':
    bot.infinity_polling()