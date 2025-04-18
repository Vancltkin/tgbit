#!/bin/bash
# Полная переустановка бота
echo "🔄 Начинаем полную переустановку..."

# Удаление старых файлов
echo "🗑️ Удаление предыдущих файлов..."
rm -rf venv .env bot.py bot.db

# Обновление пакетов
echo "🐍 Обновление системы..."
sudo apt-get update
sudo apt-get install -y python3 python3-venv

# Загрузка бота
echo "📥 Загрузка файлов..."
wget -O bot.py https://raw.githubusercontent.com/Vancltkin/tgbit/main/bot.py

# Настройка токена
echo "🔑 Настройка токена..."
read -p "Введите токен бота: " token
echo "BOT_TOKEN='$token'" > .env

# Создание окружения
echo "🔧 Создание виртуального окружения..."
python3 -m venv venv

# Установка зависимостей
echo "📦 Установка библиотек..."
./venv/bin/pip install python-telegram-bot==13.7 python-dotenv

# Инициализация БД
echo "💾 Инициализация базы данных..."
./venv/bin/python bot.py --init-db

echo "✅ Переустановка завершена! Запустите бота:"
echo "./venv/bin/python bot.py"
