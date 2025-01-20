import socket
import threading

def handle_client(client_socket):
    while True:
        # Получаем данные от клиента
        request = client_socket.recv(1024)
        if not request:
            break
        print(f"Получено: {request.decode('utf-8')}")
        # Отправляем обратно те же данные (эхо)
        client_socket.send(request)
    client_socket.close()

def start_server(host='0.0.0.0', port=9999):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)  # Слушаем до 5 клиентов
    print(f"Сервер запущен на {host}:{port}")

    while True:
        client_socket, addr = server.accept()
        print(f"Подключен клиент: {addr}")
        # Создаем новый поток для обработки клиента
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
