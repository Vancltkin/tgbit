#!/bin/bash
echo "Установка бота:"
read -p "Введите токен бота: " token
echo "BOT_TOKEN=$token" > .env
pip install python-telegram-bot==13.7
python3 -c "from bot import Database; Database()"  # Инициализация БД
echo "Установка завершена! Запустите бота командой: python3 bot.py"
