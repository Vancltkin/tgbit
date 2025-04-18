#!/bin/bash
echo "Установка бота:"

# Установка зависимостей
if ! command -v pip3 &>/dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Загрузка файлов
wget -O bot.py https://raw.githubusercontent.com/Vancltkin/tgbit/main/bot.py
wget -O requirements.txt https://raw.githubusercontent.com/Vancltkin/tgbit/main/requirements.txt

read -p "Введите токен бота: " token
echo "BOT_TOKEN=$token" > .env

# Установка пакетов
pip3 install -r requirements.txt

# Инициализация БД
python3 bot.py --init-db

echo "Установка завершена! Запустите бота командой: python3 bot.py"
