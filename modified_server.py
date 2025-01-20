import socket
import threading
import logging
import os
import json
from collections import deque

# Настройка логирования
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

def setup_logging():
    logging.basicConfig(
        filename=os.path.join(log_directory, "server.log"),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='a'
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console_handler)

clients = {}  # Словарь для хранения клиентов и их имен
history = deque(maxlen=100)  # Хранение последних 100 сообщений
server_running = True
server_paused = False

# Файл для хранения идентификаторов сессий
IDENTITY_FILE = "identities.json"

def load_identities():
    """Загружает идентификаторы сессий из файла."""
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, "r") as file:
            return json.load(file)
    return {}

def save_identities(identities):
    """Сохраняет идентификаторы сессий в файл."""
    with open(IDENTITY_FILE, "w") as file:
        json.dump(identities, file)

def clear_identities():
    """Очищает файл идентификации."""
    if os.path.exists(IDENTITY_FILE):
        os.remove(IDENTITY_FILE)
        logging.info("Файл идентификации очищен.")

def broadcast(message, sender_name):
    """Рассылает сообщение всем клиентам, кроме отправителя."""
    for client_socket, client_name in clients.items():
        if client_name != sender_name:
            try:
                client_socket.send(message)
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения клиенту: {e}")
                client_socket.close()
                del clients[client_socket]

def handle_client(client_socket):
    """Обрабатывает подключение клиента."""
    try:
        client_socket.send("Введите ваше имя: ".encode('utf-8'))
        name = client_socket.recv(1024).decode('utf-8')

        # Загружаем текущие идентификаторы
        identities = load_identities()
        identities[client_socket.fileno()] = name  # Сохраняем идентификатор
        save_identities(identities)  # Сохраняем изменения
        clients[client_socket] = name
        logging.info(f"Клиент {name} подключился.")

        # Отправка истории сообщений новому клиенту
        for msg in history:
            client_socket.send(msg.encode('utf-8'))

        welcome_message = f"{name} присоединился к чату.".encode('utf-8')
        history.append(welcome_message.decode('utf-8'))
        broadcast(welcome_message, name)

        while True:
            if server_paused:
                continue
            request = client_socket.recv(1024)
            if not request:
                break
            message = f"{name}: {request.decode('utf-8')}"
            logging.info(message)
            history.append(message)
            broadcast(request, name)  # Рассылаем сообщение всем клиентам
    except Exception as e:
        logging.error(f"Ошибка при обработке клиента {name}: {e}")
    finally:
        client_socket.close()
        del clients[client_socket]  # Удаляем клиента из списка
        identities = load_identities()  # Загружаем идентификаторы
        if client_socket.fileno() in identities:
            del identities[client_socket.fileno()]  # Удаляем идентификатор из словаря
            save_identities(identities)  # Сохраняем изменения
        logging.info(f"Клиент {name} отключился.")
        broadcast(f"{name} покинул чат.".encode('utf-8'), name)

def start_server(host='localhost', port=9999):
    setup_logging()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    logging.info(f"Сервер запущен на {host}:{port}")

    while server_running:
        try:
            client_socket, addr = server.accept()
            # Создаем новый поток для обработки клиента
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
        except Exception as e:
            logging.error(f"Ошибка при подключении клиента: {e}")

def command_thread():
    """Поток для обработки команд управления сервером."""
    global server_running, server_paused
    while True:
        command = input("Введите команду (stop, pause, show_logs, clear_logs, clear_id): ")
        if command == "stop":
            server_running = False
            logging.info("Сервер остановлен.")
            break
        elif command == "pause":
            server_paused = not server_paused
            status = "приостановлен" if server_paused else "возобновлен"
            logging.info(f"Сервер {status}.")
        elif command == "show_logs":
            with open(os.path.join(log_directory, "server.log"), "r") as log_file:
                print(log_file.read())
        elif command == "clear_logs":
            open(os.path.join(log_directory, "server.log"), "w").close()
            logging.info("Логи очищены.")
        elif command == "clear_id":
            clear_identities()

if __name__ == "__main__":
    # Запуск управляющего потока
    command_thread_instance = threading.Thread(target=command_thread)
    command_thread_instance.start()

    # Запуск сервера
    host = input("Введите IP-адрес сервера (по умолчанию localhost): ") or 'localhost'
    port_input = input("Введите порт сервера (по умолчанию 9999): ")
    port = int(port_input) if port_input else 9999
    start_server(host, port)

    # Ожидание завершения управляющего потока
    command_thread_instance.join()