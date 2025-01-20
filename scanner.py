import socket
import threading


def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Установка тайм-аута
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"Порт {port} открыт")
        sock.close()
    except Exception as e:
        print(f"Ошибка при сканировании порта {port}: {e}")


def port_scanner(host, start_port, end_port):
    threads = []
    for port in range(start_port, end_port + 1):
        thread = threading.Thread(target=scan_port, args=(host, port))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()  # Дожидаемся завершения всех потоков


if __name__ == "__main__":
    host = input("Введите хост/IP-адрес: ")
    start_port = int(input("Введите начальный порт: "))
    end_port = int(input("Введите конечный порт: "))
    port_scanner(host, start_port, end_port)
