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

def handle_client(client_socket, addr):
    logging.info(f"Подключен клиент: {addr}")
    while True:
        try:
            request = client_socket.recv(1024)
            if not request:
                break
            message = request.decode('utf-8')
            logging.info(f"Получено от {addr}: {message}")
            client_socket.send(request)  # Эхо
        except Exception as e:
            logging.error(f"Ошибка при обработке клиента {addr}: {e}")
            break
    client_socket.close()
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
