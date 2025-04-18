#!/bin/bash
echo "🐍 Настройка окружения..."
sudo apt-get update
sudo apt-get install -y python3 python3-venv

echo "📥 Загрузка файлов бота..."
wget -O bot.py https://raw.githubusercontent.com/Vancltkin/tgbit/main/bot.py
wget -O requirements.txt https://raw.githubusercontent.com/Vancltkin/tgbit/main/requirements.txt

echo "🔑 Настройка токена..."
read -p "Введите токен бота: " token
echo "BOT_TOKEN='$token'" > .env

echo "🔧 Создание виртуального окружения..."
python3 -m venv venv

echo "📦 Установка библиотек..."
./venv/bin/pip install -r requirements.txt

echo "💾 Инициализация базы данных..."
./venv/bin/python bot.py --init-db

echo "✅ Установка завершена! Запустите бота командой:"
echo "./venv/bin/python bot.py"
