import telebot
from telebot import types
import json
import os
from datetime import datetime

# Токен бота
API_TOKEN = ''

bot = telebot.TeleBot(API_TOKEN)

# Файл для хранения отзывов в JSON формате
FEEDBACK_FILE = 'feedback.json'

# Учителя в группе Программисты
teachers_prog = {
    'Харченко Никита Леонидович😎': 'Преподаватель введения в специальность и программирования на Python.',
    'Пташинский Игорь Андреевич🧔🏻‍♂️': 'Преподаватель истории и обществознания.',
    'Чихачёв Артем Аркадьевич🧔🏻‍♂️☁️': 'Преподаватель Интернет-маркетинга.',
    'Чиндяйкина Марина Сергеевна🦅': 'Преподаватель иностранного языка',
    'Фофанова Александра Владимировна': 'Преподаватель биологии и химии',
    'Лысогорский Иван Сергеевич': 'Преподаватель физкультуры и основы безопасности защиты Родины',
    'Волошин Александр Сергеевич': 'Конфигурирование Windows 10',
}

# Учителя в группе "Дизайнеры"
teachers_diz = {
    'Потякина Валерия Андреевна🐈': 'Преподаватель математики, ОИТ, информатики.',
    'Игнатенко Екатерина Алексеевна✝️': 'Преподаватель истории искусств',
    'Пташинский Игорь Андреевич🛐🤠': 'Преподаватель истории, общества и основ Photoshop adapt',
    'Клименко Наталья Викторовна🦪🚷📵': 'Преподаватель географии',
    'Мамедова Наргиз Мехмановна👩‍🔬': 'Преподаватель химии',
    'Чиндяйкина Марина Сергеевна🦅': 'Преподаватель иностранного языка'
}


# Загрузка отзывов из файла
def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


# Сохранение отзывов в файл
def save_feedback_to_file(feedback_data):
    with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
        json.dump(feedback_data, f, ensure_ascii=False, indent=4)


# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Привет, {message.from_user.first_name}! Я твой помощник. все команды бота - /help")


# Команда /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    Доступные команды:
    /start - Приветствие
    /help - Эта помощь
    /teachers - Список преподавателей 
    /feedback - Оставить отзыв о преподавателе
    /view_feedback - Просмотреть все отзывы
    /my_reviews - Просмотреть свои отзывы
    /resources - Полезные ресурсы для обучения
    """
    bot.reply_to(message, help_text)


# Команда /resources
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


# Команда /teachers
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


# Команда /feedback
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
    bot.send_message(message.chat.id,
                     f"Введите ваш отзыв о {selected_teacher}:",
                     reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_feedback, selected_teacher)


# Сохранение отзыва
def process_feedback(message, teacher):
    feedback_data = load_feedback()
    user_id = str(message.from_user.id)

    if user_id not in feedback_data:
        feedback_data[user_id] = []

    feedback_data[user_id].append({
        'teacher': teacher,
        'text': message.text,
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    save_feedback_to_file(feedback_data)
    bot.reply_to(message, "✅ Ваш отзыв успешно сохранён!")


# Команда /view_feedback - просмотр всех отзывов
@bot.message_handler(commands=['view_feedback'])
def view_feedback(message):
    feedback_data = load_feedback()

    if not feedback_data:
        bot.reply_to(message, "Отзывов пока нет.")
        return

    response = "📝 Все отзывы:\n\n"
    for user_id, reviews in feedback_data.items():
        for review in reviews:
            response += f"👤 {review['teacher']}\n"
            response += f"➖ {review['text']}\n"
            response += f"📅 {review['date']}\n\n"

    bot.reply_to(message, response)


# Команда /my_reviews - просмотр своих отзывов
@bot.message_handler(commands=['my_reviews'])
def show_my_reviews(message):
    feedback_data = load_feedback()
    user_id = str(message.from_user.id)

    if user_id not in feedback_data or not feedback_data[user_id]:
        bot.reply_to(message, "📭 У вас пока нет отзывов.")
        return

    response = "📖 Ваши отзывы:\n\n"
    for idx, review in enumerate(feedback_data[user_id], 1):
        response += f"{idx}. {review['teacher']}\n"
        response += f"➖ {review['text']}\n"
        response += f"📅 {review['date']}\n\n"

    bot.reply_to(message, response)


# Обработка нажатий на кнопки
@bot.callback_query_handler(func=lambda q: q.data == 'home')
def teachers_home(query):
    bot.edit_message_text("Вы вернулись в главное меню.",
                          query.message.chat.id,
                          query.message.message_id)


# Обработка неизвестных сообщений
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Не понял ваше сообщение. Попробуйте ещё раз.")


# Запуск бота
if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()
