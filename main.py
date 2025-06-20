import telebot
from telebot import types
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not API_TOKEN:
    raise ValueError("Токен бота не найден в .env файле!")

bot = telebot.TeleBot(API_TOKEN)

# Файлы
TEACHERS_FILE = 'teachers.json'
FEEDBACK_FILE = 'feedback.json'

# Админы (замени на свой chat_id)
ADMINS = [7245536246]


# === Работа с преподавателями ===

def load_teachers():
    if os.path.exists(TEACHERS_FILE):
        with open(TEACHERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"Программисты": {}, "Дизайнеры": {}}


def save_teachers(data):
    with open(TEACHERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# === Работа с отзывами ===

def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_feedback_to_file(feedback_data):
    with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
        json.dump(feedback_data, f, ensure_ascii=False, indent=4)


# === Команды ===

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Привет, {message.from_user.first_name}! Все команды: /help")


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, """
/start — начать работу
/help — помощь
/teachers — список преподавателей
/feedback — оставить отзыв
/view_feedback — все отзывы
/my_reviews — мои отзывы
/resources — полезные ресурсы
/admin — админ-панель
""")


@bot.message_handler(commands=['resources'])
def resources_command(message):
    bot.reply_to(message, """
Полезные ресурсы:
— Программисты: Coursera, Codecademy, Udemy, GitHub
— Дизайнеры: Canva, Adobe, Behance, Dribbble
""")


@bot.message_handler(commands=['teachers'])
def list_teachers(message):
    data = load_teachers()
    result = ""
    for group, teachers in data.items():
        result += f"\n📚 {group}:\n"
        for i, (name, desc) in enumerate(teachers.items(), 1):
            result += f"{i}. {name} — {desc}\n"
    bot.reply_to(message, result)


@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id not in ADMINS:
        bot.reply_to(message, "❌ У вас нет доступа.")
        return
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ Добавить преподавателя", callback_data='add_teacher'))
    markup.add(types.InlineKeyboardButton("🗑️ Удалить преподавателя", callback_data='remove_teacher'))
    bot.reply_to(message, "🔐 Админ-панель:", reply_markup=markup)


# === Добавление преподавателя ===

@bot.callback_query_handler(func=lambda c: c.data == 'add_teacher')
def add_teacher_start(callback):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add("Программисты", "Дизайнеры")
    msg = bot.send_message(callback.message.chat.id, "Выберите группу:", reply_markup=keyboard)
    bot.register_next_step_handler(msg, process_group_for_add)


def process_group_for_add(message):
    group = message.text.strip()
    if group not in ["Программисты", "Дизайнеры"]:
        bot.reply_to(message, "❌ Неверная группа.")
        return
    msg = bot.send_message(message.chat.id, "Введите имя преподавателя:")
    bot.register_next_step_handler(msg, lambda m: process_name_for_add(m, group))


def process_name_for_add(message, group):
    name = message.text.strip()
    msg = bot.send_message(message.chat.id, "Введите описание преподавателя:")
    bot.register_next_step_handler(msg, lambda m: finish_add_teacher(m, group, name))


def finish_add_teacher(message, group, name):
    desc = message.text.strip()
    data = load_teachers()
    data[group][name] = desc
    save_teachers(data)
    bot.reply_to(message, f"✅ Преподаватель {name} добавлен в группу {group}.")


# === Удаление преподавателя ===

@bot.callback_query_handler(func=lambda c: c.data == 'remove_teacher')
def remove_teacher_start(callback):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add("Программисты", "Дизайнеры")
    msg = bot.send_message(callback.message.chat.id, "Выберите группу:", reply_markup=keyboard)
    bot.register_next_step_handler(msg, process_group_for_remove)


def process_group_for_remove(message):
    group = message.text.strip()
    data = load_teachers()
    if group not in data:
        bot.reply_to(message, "❌ Группа не найдена.")
        return
    if not data[group]:
        bot.reply_to(message, "В этой группе нет преподавателей.")
        return
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for name in data[group].keys():
        keyboard.add(name)
    msg = bot.send_message(message.chat.id, "Выберите преподавателя для удаления:", reply_markup=keyboard)
    bot.register_next_step_handler(msg, lambda m: finish_remove_teacher(m, group))


def finish_remove_teacher(message, group):
    name = message.text.strip()
    data = load_teachers()
    if name in data[group]:
        del data[group][name]
        save_teachers(data)
        bot.reply_to(message, f"🗑️ {name} удалён из группы {group}.")
    else:
        bot.reply_to(message, "❌ Преподаватель не найден.")


# === Отзывы ===

@bot.message_handler(commands=['feedback'])
def feedback_command(message):
    data = load_teachers()
    all_teachers = []
    for teachers in data.values():
        all_teachers.extend(teachers.keys())
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for name in all_teachers:
        keyboard.add(name)
    msg = bot.send_message(message.chat.id, "Выберите преподавателя:", reply_markup=keyboard)


@bot.message_handler(func=lambda m: m.text in sum([list(v.keys()) for v in load_teachers().values()], []))
def select_teacher(message):
    selected_teacher = message.text
    bot.send_message(message.chat.id, f"Напишите отзыв о {selected_teacher}:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_feedback, selected_teacher)


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
    bot.reply_to(message, "✅ Отзыв сохранён.")


@bot.message_handler(commands=['view_feedback'])
def view_feedback(message):
    feedback_data = load_feedback()
    if not feedback_data:
        bot.reply_to(message, "Отзывов пока нет.")
        return
    result = "📋 Все отзывы:\n\n"
    for reviews in feedback_data.values():
        for review in reviews:
            result += f"👤 {review['teacher']}\n➖ {review['text']}\n📅 {review['date']}\n\n"
    bot.reply_to(message, result)


@bot.message_handler(commands=['my_reviews'])
def show_my_reviews(message):
    feedback_data = load_feedback()
    user_id = str(message.from_user.id)
    if user_id not in feedback_data or not feedback_data[user_id]:
        bot.reply_to(message, "📭 У вас нет отзывов.")
        return
    result = "📖 Ваши отзывы:\n\n"
    for i, review in enumerate(feedback_data[user_id], 1):
        result += f"{i}. {review['teacher']}\n➖ {review['text']}\n📅 {review['date']}\n\n"
    bot.reply_to(message, result)


# === Запуск ===

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
