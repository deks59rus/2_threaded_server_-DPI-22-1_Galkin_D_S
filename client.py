import socket


def start_client(server_ip, server_port):
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
    server_ip = input("Введите IP-адрес сервера: ")
    server_port = int(input("Введите порт сервера: "))
    start_client(server_ip, server_port)
