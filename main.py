import socket
import threading
import json
import time
from datetime import date


def handle_messages(connection: socket.socket):
    while True:
        try:
            msg = connection.recv(1024)
            if msg:
                print(msg.decode())
            else:
                connection.close()
                break

        except Exception as e:
            print(f'Ocorreu um erro: {e}')
            connection.close()
            break

connections = []


def handle_user_connection(connection: socket.socket, address: str) -> None:
    while True:
        try:
            msg = connection.recv(1024)
            msg_dumped = json.loads(msg)

            if msg:
                print(f'\n{msg_dumped["username"]} > {msg_dumped["message"]}\n{msg_dumped["time"]} - {msg_dumped["date"]}')

                msg_to_send = f'\n{msg_dumped["username"]} > {msg_dumped["message"]}\n{msg_dumped["time"]} - {msg_dumped["date"]}'
                broadcast(msg_to_send, connection)
            else:
                remove_connection(connection)
                break

        except Exception as e:
            print(f'Error to handle user connection: {e}')
            remove_connection(connection)
            break


def broadcast(message: str, connection: socket.socket) -> None:
    for client_conn in connections:
        if client_conn != connection:
            try:
                client_conn.send(message.encode())
            except Exception as e:
                print(f'Error broadcasting message: {e}')
                remove_connection(client_conn)


def remove_connection(conn: socket.socket) -> None:
    if conn in connections:
        conn.close()
        connections.remove(conn)


op = int(input("Digite a opção desejada:\n"
               "1 - Usuario\n"
               "2 - Servidor\n"
               "0 - Fechar\n"))


if op == 1:
    SERVER_ADDRESS = str(input("Digite o ip do servidor: "))
    SERVER_PORT = int(input("Digite a porta do servidor: "))
    username = str(input("Digite seu nome de usuario: "))

    try:
        socket_instance = socket.socket()
        socket_instance.connect((SERVER_ADDRESS, SERVER_PORT))
        threading.Thread(target=handle_messages, args=[socket_instance]).start()

        print('Connected to chat!')

        while True:
            msg = str(input("Digite a mensagem: "))
            time_raw = time.localtime()
            time_value = time.strftime("%H:%M:%S", time_raw)
            today = date.today()
            date_value = today.strftime("%d/%m/%Y")
            payload = {
                "username": username,
                "message": msg,
                "time": time_value,
                "date": date_value,
            }

            if msg == 'fechar':
                print("Saindo da sessao...")
                break

            payload = json.dumps(payload)

            socket_instance.send(bytes(payload, 'utf-8'))

        socket_instance.close()

    except Exception as erro:
        print(f'Ocorreu um erro\n {erro}')
        socket_instance.close()

if op == 2:
    LISTENING_PORT = int(input("Digite a porta do servidor: "))

    try:
        socket_instance = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_instance.bind(('', LISTENING_PORT))
        socket_instance.listen(4)

        print('Server rodando!')

        while True:
            socket_connection, address = socket_instance.accept()
            connections.append(socket_connection)
            threading.Thread(target=handle_user_connection, args=[socket_connection, address]).start()

    except Exception as erro:
        print(f'Ocorreu um erro\n {erro}')
    finally:
        if len(connections) > 0:
            for conn in connections:
                remove_connection(conn)

        socket_instance.close()

if op == 0:
    print("Fechando...")
    exit()
