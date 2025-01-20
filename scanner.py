import socket
import threading
import logging
import os

# Настройка логирования
log_directory = "logs"

if not os.path.exists(log_directory):
    os.makedirs(log_directory)


def setup_logging(filename):
    logging.basicConfig(
        filename=os.path.join(log_directory, filename),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Установка тайм-аута
        result = sock.connect_ex((host, port))
        if result == 0:
            logging.info(f"Порт {port} открыт")
            print(f"Порт {port} открыт")
        else:
            logging.info(f"Порт {port} закрыт")
            print(f"Порт {port} закрыт")
        sock.close()
    except Exception as e:
        logging.error(f"Ошибка при сканировании порта {port}: {e}")
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
    setup_logging("port_scanner.log")
    host = input("Введите хост/IP-адрес: ")
    start_port = int(input("Введите начальный порт: "))
    end_port = int(input("Введите конечный порт: "))
    port_scanner(host, start_port, end_port)
