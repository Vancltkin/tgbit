#!/bin/bash
echo "🐍 Установка Python-зависимостей..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip

echo "📥 Загрузка файлов бота..."
wget -O bot.py https://raw.githubusercontent.com/Vancltkin/tgbit/main/bot.py
wget -O requirements.txt https://raw.githubusercontent.com/Vancltkin/tgbit/main/requirements.txt

echo "🔑 Настройка токена..."
read -p "Введите токен бота: " token
echo "BOT_TOKEN='$token'" > .env

echo "📦 Установка библиотек..."
pip3 install -r requirements.txt

echo "💾 Инициализация базы данных..."
python3 bot.py --init-db

echo "✅ Установка завершена! Запустите бота командой:"
echo "python3 bot.py"
