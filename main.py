import telebot
from telebot import types

# Ваш токен, полученный от @BotFather
API_TOKEN = '7552526610:AAGp2-U726U28Sel59SKTQdHbu7retdljqQ'

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)

# Учителя в группах
teachers_prog = {
    'Харченко Никита Леонидович😎': 'Преподаватель введения в специальность и программирования на Python.',
    'Пташинский Игорь Андреевич🧔🏻‍♂️': 'Преподаватель истории и обществознания.',
    'Чихачёв Артем Аркадьевич🧔🏻‍♂️☁️': 'Преподаватель Интернет-маркетинга.',
    'Чиндяйкина Марина Сергеевна🦅': 'Преподаватель иностранного языка',
    'Фофанова Александра Владимировна': 'Преподаватель биологии'
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
    /menu - Открыть основное меню
    /teachers - Список преподавателей
    """
    bot.reply_to(message, help_text)


# Команда /menu
@bot.message_handler(commands=['menu'])
def send_menu(message):
    menu_text = """
    Основное меню:
    1. Оставить отзыв
    2. Посмотреть отзывы
    3. Учебные материалы
    Выберите пункт:
    """
    bot.reply_to(message, menu_text)


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