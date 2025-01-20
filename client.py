import socket


def start_client(server_ip='localhost', server_port=9999):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))

    while True:
        message = input("Введите сообщение (или 'exit' для выхода): ")
        if message.lower() == 'exit':
            break
        client.send(message.encode('utf-8'))
        response = client.recv(4096)
        print(f"Ответ от сервера: {response.decode('utf-8')}")

    client.close()


if __name__ == "__main__":
    server_ip = input("Введите IP-адрес сервера (по умолчанию localhost): ") or 'localhost'
    server_port_input = input("Введите порт сервера (по умолчанию 9999): ")
    server_port = int(server_port_input) if server_port_input else 9999
    start_client(server_ip, server_port)
