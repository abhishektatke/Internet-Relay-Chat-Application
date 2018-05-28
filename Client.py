import select
import socket
import sys
import Mediator

if len(sys.argv) < 2:
    print("Please provide the hostname you want to connect to")
    sys.exit(1)
else:
    server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_conn.connect((sys.argv[1], 5001))

print("You are now connected to the server\n")
msg_prefix = ''

socket_list = [sys.stdin, server_conn]

while True:
    read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])
    for s in read_sockets:
        if s is server_conn:
            msg = s.recv(4096)
            if not msg:
                print("Server not available! please try again later")
                sys.exit(2)
            else:
                if msg == Mediator.QUIT_STRING.encode():
                    sys.stdout.write('Bye, see you soon\n')
                    sys.exit(2)
                else:
                    sys.stdout.write(msg.decode())
                    if 'Please enter your name' in msg.decode():
                        msg_prefix = 'username: '
                    else:
                        msg_prefix = ''
        else:
            msg = msg_prefix + sys.stdin.readline()
            server_conn.sendall(msg.encode())
