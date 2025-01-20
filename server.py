import socket
import threading
import logging
import os
import uuid

# Настройка логирования
log_directory = "logs"

if not os.path.exists(log_directory):
    os.makedirs(log_directory)


def setup_logging():
    logging.basicConfig(
        filename=os.path.join(log_directory, "server.log"),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='a'  # Дополнение файла вместо перезаписи
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console_handler)


clients = {}  # Словарь для хранения клиентов и их уникальных идентификаторов


def broadcast(message, sender_id):
    """Рассылает сообщение всем клиентам, кроме отправителя."""
    for client_socket, client_id in clients.items():
        if client_id != sender_id:
            try:
                client_socket.send(message)
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения клиенту: {e}")
                client_socket.close()
                del clients[client_socket]


def handle_client(client_socket):
    """Обрабатывает подключение клиента."""
    client_id = str(uuid.uuid4())  # Генерируем уникальный ID для клиента
    clients[client_socket] = client_id  # Сохраняем клиента и его ID
    logging.info(f"Клиент с ID {client_id} подключился.")

    # Уведомляем всех о новом подключении
    broadcast(f"Клиент с ID {client_id} присоединился к чату.".encode('utf-8'), client_id)

    try:
        while True:
            request = client_socket.recv(1024)
            if not request:
                break
            message = request.decode('utf-8')
            logging.info(f"Клиент {client_id}: {message}")
            broadcast(f"Клиент с ID {client_id}: {message}".encode('utf-8'),
                      client_id)  # Рассылаем сообщение всем клиентам
    except Exception as e:
        logging.error(f"Ошибка при обработке клиента {client_id}: {e}")
    finally:
        client_socket.close()
        del clients[client_socket]  # Удаляем клиента из списка
        logging.info(f"Клиент с ID {client_id} отключился.")
        # Уведомляем всех об отключении
        broadcast(f"Клиент с ID {client_id} покинул чат.".encode('utf-8'), client_id)


def start_server(host='localhost', port=9999):
    setup_logging()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    logging.info(f"Сервер запущен на {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        # Создаем новый поток для обработки клиента
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    host = input("Введите IP-адрес сервера (по умолчанию localhost): ") or 'localhost'
    port_input = input("Введите порт сервера (по умолчанию 9999): ")
    port = int(port_input) if port_input else 9999
    start_server(host, port)
