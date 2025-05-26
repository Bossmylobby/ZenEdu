import telebot
from telebot import types
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Получаем токен
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not API_TOKEN:
    raise ValueError("Токен бота не найден в .env файле!")

bot = telebot.TeleBot(API_TOKEN)

# Файлы для хранения данных
FEEDBACK_FILE = 'feedback.json'
TEACHERS_FILE = 'teachers.json'


# Загрузка преподавателей из файла
def load_teachers():
    default_teachers = {
        'teachers_prog': {
            'Харченко Никита Леонидович😎': 'Преподаватель введения в специальность и программирования на Python.',
            'Пташинский Игорь Андреевич🧔🏻‍♂️': 'Преподаватель истории и обществознания.',
            'Чихачёв Артем Аркадьевич🧔🏻‍♂️☁️': 'Преподаватель Интернет-маркетинга.',
            'Чиндяйкина Марина Сергеевна🦅': 'Преподаватель иностранного языка',
            'Фофанова Александра Владимировна': 'Преподаватель биологии и химии',
            'Лысогорский Иван Сергеевич': 'Преподаватель физкультуры и основы безопасности защиты Родины',
            'Волошин Александр Сергеевич': 'Конфигурирование Windows 10'
        },
        'teachers_diz': {
            'Потякина Валерия Андреевна🐈': 'Преподаватель математики, ОИТ, информатики.',
            'Игнатенко Екатерина Алексеевна✝️': 'Преподаватель истории искусств',
            'Пташинский Игорь Андреевич🛐🤠': 'Преподаватель истории, общества и основ Photoshop adapt',
            'Клименко Наталья Викторовна😒': 'Преподаватель географии',
            'Мамедова Наргиз Мехмановна👩‍🔬': 'Преподаватель химии',
            'Чиндяйкина Марина Сергеевна🦅': 'Преподаватель иностранного языка'
        }
    }

    if os.path.exists(TEACHERS_FILE):
        try:
            with open(TEACHERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Если файл поврежден, создаем новый с дефолтными значениями
            with open(TEACHERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_teachers, f, ensure_ascii=False, indent=4)
            return default_teachers
    else:
        # Если файл не существует, создаем его с дефолтными значениями
        with open(TEACHERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_teachers, f, ensure_ascii=False, indent=4)
        return default_teachers


# Сохранение преподавателей в файл
def save_teachers(teachers_data):
    with open(TEACHERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(teachers_data, f, ensure_ascii=False, indent=4)


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


# Команда /teachers
@bot.message_handler(commands=['teachers'])
def list_teachers(message):
    teachers_data = load_teachers()
    teachers_prog = teachers_data.get('teachers_prog', {})
    teachers_diz = teachers_data.get('teachers_diz', {})

    teachers_list = ""
    for group, teachers in [('Программисты', teachers_prog), ('Дизайнеры', teachers_diz)]:
        teachers_list += f"\nГруппа: {group}\n"
        for i, (name, desc) in enumerate(teachers.items()):
            teachers_list += f"{i + 1}. {name} - {desc}\n"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Главная', callback_data='home'))

    bot.reply_to(message, f"Доступные преподаватели:\n{teachers_list}", reply_markup=markup)


ADMINS = [7245536246]  # Ваш chat_id


# Команда /admin
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id not in ADMINS:
        bot.reply_to(message, "🚨 Доступ запрещён!")
        return

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Добавить преподавателя", callback_data='add_teacher'),
        types.InlineKeyboardButton("Удалить преподавателя", callback_data='remove_teacher')
    )
    markup.row(types.InlineKeyboardButton("Статистика за месяц", callback_data='stats'))
    bot.reply_to(message, "Админ-панель:", reply_markup=markup)


# Обработчик кнопки добавления преподавателя
@bot.callback_query_handler(func=lambda call: call.data == 'add_teacher')
def add_teacher_callback(call):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Программисты", callback_data='add_prog'),
        types.InlineKeyboardButton("Дизайнеры", callback_data='add_diz')
    )
    markup.row(types.InlineKeyboardButton("Назад", callback_data='back_to_admin'))
    bot.edit_message_text("Выберите группу для добавления преподавателя:",
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markup)


# Обработчик кнопки удаления преподавателя
@bot.callback_query_handler(func=lambda call: call.data == 'remove_teacher')
def remove_teacher_callback(call):
    teachers_data = load_teachers()
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Программисты", callback_data='remove_prog'),
        types.InlineKeyboardButton("Дизайнеры", callback_data='remove_diz')
    )
    markup.row(types.InlineKeyboardButton("Назад", callback_data='back_to_admin'))
    bot.edit_message_text("Выберите группу для удаления преподавателя:",
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markup)


# Обработчик выбора группы для добавления
@bot.callback_query_handler(func=lambda call: call.data in ['add_prog', 'add_diz'])
def select_group_for_add(call):
    group = 'teachers_prog' if call.data == 'add_prog' else 'teachers_diz'
    msg = bot.edit_message_text(
        f"Введите имя и описание преподавателя для группы {call.data.replace('add_', '')} в формате:\n\nИмя Преподавателя - Описание",
        call.message.chat.id,
        call.message.message_id)
    bot.register_next_step_handler(msg, process_add_teacher, group)


# Процесс добавления преподавателя
def process_add_teacher(message, group):
    try:
        name, description = message.text.split(' - ', 1)
        teachers_data = load_teachers()

        if group not in teachers_data:
            teachers_data[group] = {}

        teachers_data[group][name.strip()] = description.strip()
        save_teachers(teachers_data)

        bot.reply_to(message, f"✅ Преподаватель {name} успешно добавлен в группу {group.replace('teachers_', '')}!")
    except ValueError:
        bot.reply_to(message, "❌ Неверный формат. Используйте: Имя - Описание")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")


# Обработчик выбора группы для удаления
@bot.callback_query_handler(func=lambda call: call.data in ['remove_prog', 'remove_diz'])
def select_group_for_remove(call):
    teachers_data = load_teachers()
    group = 'teachers_prog' if call.data == 'remove_prog' else 'teachers_diz'
    teachers = teachers_data.get(group, {})

    markup = types.InlineKeyboardMarkup()

    if not teachers:
        bot.edit_message_text(f"В группе {group.replace('teachers_', '')} нет преподавателей для удаления.",
                              call.message.chat.id,
                              call.message.message_id)
        return

    for teacher in teachers.keys():
        callback_data = f"remove_teacher_{group}_{teacher}"
        markup.add(types.InlineKeyboardButton(teacher, callback_data=callback_data))

    markup.add(types.InlineKeyboardButton("Назад", callback_data='back_to_admin'))
    bot.edit_message_text(f"Выберите преподавателя для удаления из группы {group.replace('teachers_', '')}:",
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markup)


# Обработчик удаления конкретного преподавателя
@bot.callback_query_handler(func=lambda call: call.data.startswith('remove_teacher_'))
def remove_specific_teacher(call):
    parts = call.data.split('_')
    if len(parts) < 4:
        bot.answer_callback_query(call.id, "❌ Ошибка при удалении")
        return

    group = '_'.join(parts[2:-1])
    teacher_name = parts[-1]

    teachers_data = load_teachers()

    if group in teachers_data and teacher_name in teachers_data[group]:
        del teachers_data[group][teacher_name]
        save_teachers(teachers_data)
        bot.edit_message_text(f"✅ Преподаватель {teacher_name} удалён из группы {group.replace('teachers_', '')}.",
                              call.message.chat.id,
                              call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ Преподаватель не найден")


# Обработчик кнопки "Назад" в админ-панели
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_admin')
def back_to_admin(call):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Добавить преподавателя", callback_data='add_teacher'),
        types.InlineKeyboardButton("Удалить преподавателя", callback_data='remove_teacher')
    )
    markup.row(types.InlineKeyboardButton("Статистика за месяц", callback_data='stats'))
    bot.edit_message_text("Админ-панель:",
                          call.message.chat.id,
                          call.message.message_id,
                          reply_markup=markup)


# Команда /feedback
@bot.message_handler(commands=['feedback'])
def feedback_command(message):
    teachers_data = load_teachers()
    all_teachers = list(teachers_data.get('teachers_prog', {}).keys()) + list(
        teachers_data.get('teachers_diz', {}).keys())

    if not all_teachers:
        bot.reply_to(message, "Список преподавателей пуст.")
        return

    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for teacher in all_teachers:
        keyboard.add(teacher)

    bot.send_message(message.chat.id, "Выберите преподавателя:", reply_markup=keyboard)


# Обработчик выбора преподавателя для отзыва
@bot.message_handler(func=lambda message: True)
def handle_teacher_selection(message):
    teachers_data = load_teachers()
    all_teachers = list(teachers_data.get('teachers_prog', {}).keys()) + list(
        teachers_data.get('teachers_diz', {}).keys())

    if message.text in all_teachers:
        selected_teacher = message.text
        bot.send_message(message.chat.id,
                         f"Введите ваш отзыв о {selected_teacher}:",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, process_feedback, selected_teacher)
    else:
        bot.reply_to(message, "Не понял ваше сообщение. Попробуйте ещё раз.")


# Остальные команды (/start, /help, /resources и т.д.) остаются без изменений
# ...

if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()