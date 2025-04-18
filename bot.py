import sqlite3
import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from dotenv import load_dotenv

# Состояния для ConversationHandler
ADD_USER, GET_UID, GET_LINK, GET_TEXT, GET_APP_LINK = range(5)
EDIT_USER, EDIT_FIELD, EDIT_VALUE = range(3)

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bot.db')
        self.init_db()
        
    def init_db(self):
        c = self.conn.cursor()
        # Таблица админа
        c.execute('''CREATE TABLE IF NOT EXISTS admin 
                    (user_id INTEGER PRIMARY KEY)''')
        # Таблица пользователей
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (uid INTEGER PRIMARY KEY,
                     link TEXT,
                     text TEXT,
                     app_link TEXT)''')
        # Таблица шаблонов
        c.execute('''CREATE TABLE IF NOT EXISTS templates
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT,
                     text TEXT,
                     app_link TEXT)''')
        self.conn.commit()
    
    def get_admin(self):
        c = self.conn.cursor()
        c.execute("SELECT user_id FROM admin")
        return c.fetchone()
    
    def set_admin(self, user_id):
        c = self.conn.cursor()
        c.execute("INSERT INTO admin (user_id) VALUES (?)", (user_id,))
        self.conn.commit()
    
    def add_user(self, uid, link, text, app_link):
        c = self.conn.cursor()
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (uid, link, text, app_link))
        self.conn.commit()
    
    def get_users(self):
        c = self.conn.cursor()
        c.execute("SELECT uid FROM users")
        return [u[0] for u in c.fetchall()]
    
    def get_user(self, uid):
        c = self.conn.cursor()
        c.execute("SELECT * FROM users WHERE uid=?", (uid,))
        return c.fetchone()
    
    def delete_user(self, uid):
        c = self.conn.cursor()
        c.execute("DELETE FROM users WHERE uid=?", (uid,))
        self.conn.commit()
    
    def update_user(self, uid, field, value):
        c = self.conn.cursor()
        c.execute(f"UPDATE users SET {field}=? WHERE uid=?", (value, uid))
        self.conn.commit()

def start(update: Update, context: CallbackContext):
    db = Database()
    user_id = update.effective_user.id
    admin = db.get_admin()
    
    if not admin:
        db.set_admin(user_id)
        update.message.reply_text("👑 Вы стали администратором бота!")
        show_admin_menu(update)
    elif user_id == admin[0]:  # Исправлено: admin[0] вместо admin
        show_admin_menu(update)
    else:
        user = db.get_user(user_id)
        if user:
            send_user_info(update, user)
        else:
            update.message.reply_text("🚫 Доступ запрещен")
            
def show_admin_menu(update):
    keyboard = [['Добавить пользователя', 'Список пользователей']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text('Админ-меню:', reply_markup=reply_markup)

def add_user_start(update: Update, context: CallbackContext):
    update.message.reply_text("Введите UID пользователя:")
    return GET_UID

def add_user_get_uid(update: Update, context: CallbackContext):
    context.user_data['uid'] = update.message.text
    update.message.reply_text("Введите ссылку пользователя:")
    return GET_LINK

def add_user_get_link(update: Update, context: CallbackContext):
    context.user_data['link'] = update.message.text
    update.message.reply_text("Введите текст для пользователя:")
    return GET_TEXT

def add_user_get_text(update: Update, context: CallbackContext):
    context.user_data['text'] = update.message.text
    update.message.reply_text("Введите ссылку на приложение:")
    return GET_APP_LINK

def add_user_finish(update: Update, context: CallbackContext):
    data = context.user_data
    try:
        db = Database()
        db.add_user(
            int(data['uid']),
            data['link'],
            data['text'],
            update.message.text
        )
        update.message.reply_text("✅ Пользователь добавлен!")
    except Exception as e:
        print(e)
        update.message.reply_text("❌ Ошибка при добавлении")
    finally:
        context.user_data.clear()
    return ConversationHandler.END

def list_users(update: Update, context: CallbackContext):
    db = Database()
    users = db.get_users()
    keyboard = [[InlineKeyboardButton(str(uid), callback_data=f'user_{uid}')] for uid in users]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите пользователя:', reply_markup=reply_markup)

def user_detail(update: Update, context: CallbackContext):
    query = update.callback_query
    uid = int(query.data.split('_')[1])
    db = Database()
    user = db.get_user(uid)
    
    text = f"UID: {user[0]}\nСсылка: {user[1]}\nТекст: {user[2]}\nПриложение: {user[3]}"
    
    keyboard = [
        [InlineKeyboardButton("✏️ Редактировать", callback_data=f'edit_{uid}'),
         InlineKeyboardButton("🗑 Удалить", callback_data=f'delete_{uid}')],
        [InlineKeyboardButton("Назад", callback_data='back')]
    ]
    query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

def delete_user(update: Update, context: CallbackContext):
    query = update.callback_query
    uid = int(query.data.split('_')[1])
    db = Database()
    db.delete_user(uid)
    query.answer("Пользователь удален")
    list_users(update, context)

def edit_user_start(update: Update, context: CallbackContext):
    query = update.callback_query
    uid = int(query.data.split('_')[1])
    context.user_data['edit_uid'] = uid
    
    keyboard = [
        [InlineKeyboardButton("Ссылка", callback_data='edit_link'),
         InlineKeyboardButton("Текст", callback_data='edit_text')],
        [InlineKeyboardButton("Ссылка на приложение", callback_data='edit_app_link')]
    ]
    query.edit_message_text("Выберите поле для редактирования:",
                           reply_markup=InlineKeyboardMarkup(keyboard))
    return EDIT_FIELD

def edit_field(update: Update, context: CallbackContext):
    query = update.callback_query
    field = query.data.split('_')[1]
    context.user_data['edit_field'] = field
    query.edit_message_text(f"Введите новое значение для {field}:")
    return EDIT_VALUE

def edit_value(update: Update, context: CallbackContext):
    value = update.message.text
    uid = context.user_data['edit_uid']
    field = context.user_data['edit_field']
    
    db = Database()
    db.update_user(uid, field, value)
    update.message.reply_text("✅ Изменения сохранены!")
    
    context.user_data.clear()
    return ConversationHandler.END

def handle_user_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    db = Database()
    user = db.get_user(user_id)
    
    if user:
        send_user_info(update, user)
    else:
        update.message.reply_text("🚫 Доступ запрещен")

def send_user_info(update, user):
    text = f"{user[2]}\n\nСсылка: {user[1]}"
    keyboard = [[InlineKeyboardButton("📨 Написать в поддержку", url=user[1])]]
    
    if user[3]:
        text += f"\nПриложение: {user[3]}"
        keyboard.append([InlineKeyboardButton("📲 Скачать приложение", url=user[3])])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, reply_markup=reply_markup)

def main():
    # Загрузка переменных окружения из .env
    load_dotenv()
    
    # Получение токена
    token = os.getenv('BOT_TOKEN')
    
    # Проверка наличия токена
    if not token:
        print("❌ Ошибка: Токен бота не найден в .env файле!")
        print("Проверьте что в файле .env есть строка:")
        print("BOT_TOKEN='ваш_токен'")
        return

    try:
        # Инициализация бота
        updater = Updater(token)
        dp = updater.dispatcher

        # ========== Обработчики команд ==========
        # Стартовая команда
        dp.add_handler(CommandHandler('start', start))
        
        # Обработчик текстовых сообщений
        dp.add_handler(MessageHandler(
            Filters.text & ~Filters.command, 
            handle_user_message
        ))

        # ========== Админ-функционал ==========
        # Добавление пользователя (ConversationHandler)
        conv_add_user = ConversationHandler(
            entry_points=[MessageHandler(Filters.regex('^Добавить пользователя$'), add_user_start)],
            states={
                GET_UID: [MessageHandler(Filters.text, add_user_get_uid)],
                GET_LINK: [MessageHandler(Filters.text, add_user_get_link)],
                GET_TEXT: [MessageHandler(Filters.text, add_user_get_text)],
                GET_APP_LINK: [MessageHandler(Filters.text, add_user_finish)]
            },
            fallbacks=[]
        )

        # Редактирование пользователя (ConversationHandler)
        conv_edit_user = ConversationHandler(
            entry_points=[CallbackQueryHandler(edit_user_start, pattern='^edit_')],
            states={
                EDIT_FIELD: [CallbackQueryHandler(edit_field, pattern='^edit_')],
                EDIT_VALUE: [MessageHandler(Filters.text, edit_value)]
            },
            fallbacks=[]
        )

        # Добавление обработчиков
        dp.add_handler(conv_add_user)
        dp.add_handler(conv_edit_user)
        dp.add_handler(MessageHandler(Filters.regex('^Список пользователей$'), list_users))
        dp.add_handler(CallbackQueryHandler(user_detail, pattern='^user_'))
        dp.add_handler(CallbackQueryHandler(delete_user, pattern='^delete_'))
        dp.add_handler(CallbackQueryHandler(list_users, pattern='^back$'))

        # Запуск бота
        print("✅ Бот успешно запущен!")
        updater.start_polling()
        updater.idle()

    except Exception as e:
        print(f"❌ Критическая ошибка: {str(e)}")
        print("Проверьте:")
        print("1. Корректность токена")
        print("2. Подключение к интернету")
        print("3. Наличие прав доступа")
        
if __name__ == '__main__':
    # Простая проверка аргументов
    if '--init-db' in sys.argv:
        Database()
        print("✅ База данных инициализирована!")
    else:
        main()
