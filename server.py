import socket
import threading
import logging
import os

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

clients = []  # Список для хранения всех подключенных клиентов

def broadcast(message, client_socket):
    """Рассылает сообщение всем клиентам, кроме отправителя."""
    for client in clients:
        if client != client_socket:
            try:
                client.send(message)
            except Exception as e:
                logging.error(f"Ошибка при отправке сообщения клиенту: {e}")
                client.close()
                clients.remove(client)

def handle_client(client_socket, addr):
    logging.info(f"Подключен клиент: {addr}")
    clients.append(client_socket)  # Добавляем нового клиента в список

    try:
        while True:
            request = client_socket.recv(1024)
            if not request:
                break
            message = request.decode('utf-8')
            logging.info(f"Получено от {addr}: {message}")
            broadcast(request, client_socket)  # Рассылаем сообщение всем клиентам
    except Exception as e:
        logging.error(f"Ошибка при обработке клиента {addr}: {e}")
    finally:
        client_socket.close()
        clients.remove(client_socket)  # Удаляем клиента из списка
        logging.info(f"Отключен клиент: {addr}")

def start_server(host='localhost', port=9999):
    setup_logging()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    logging.info(f"Сервер запущен на {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        # Создаем новый поток для обработки клиента
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

if __name__ == "__main__":
    host = input("Введите IP-адрес сервера (по умолчанию localhost): ") or 'localhost'
    port_input = input("Введите порт сервера (по умолчанию 9999): ")
    port = int(port_input) if port_input else 9999
    start_server(host, port)
