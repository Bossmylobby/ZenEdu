import telebot
from telebot import types
#токен бота
API_TOKEN = '7552526610:AAGp2-U726U28Sel59SKTQdHbu7retdljqQ'

bot = telebot.TeleBot(API_TOKEN)

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


# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Привет, {message.from_user.first_name}! Я твой помощник. Чем могу помочь?")


# Команда /help
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
    bot.send_message(message.chat.id, f"Введите ваш отзыв о {selected_teacher}:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, save_feedback, selected_teacher)


# Сохранение отзыва
def save_feedback(message, teacher):
    with open('feedback.txt', 'a+', encoding="utf-8") as file:
        file.write(f'{teacher}: {message.text}\n\n')
    bot.send_message(message.chat.id, "Ваш отзыв успешно сохранён!", reply_markup=types.ReplyKeyboardRemove())


# Команда /view_feedback
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


# Команда /resources
@bot.message_handler(commands=['resources'])
def resources_command(message):
    resources_text = """
    Полезные ресурсы для групп:

    Программисты:
    💡 Введение в программирование на Python: https://www.python.org/
    💡 Основы алгоритмов: https://ru.wikipedia.org/wiki/Алгоритм
    💡 Практические задачи по Python: https://leetcode.com/
    💡 Официальный сайт Microsoft для изучения Windows 10: https://docs.microsoft.com/en-us/windows/

    Дизайнеры:
    🖌 Основы дизайна: https://www.canva.com/learn/design-basics/
    🖌 История искусства: https://www.khanacademy.org/humanities/art-history
    🖌 Основы работы в Adobe Photoshop: https://helpx.adobe.com/photoshop/tutorials.html
    🖌 География и дизайн: https://www.nationalgeographic.com/magazine/

    Эти ресурсы помогут вам лучше освоить ваши специальности. Удачи в обучении!
    """

    bot.reply_to(message, resources_text)

# Запуск бота
if __name__ == '__main__':
    bot.infinity_polling()