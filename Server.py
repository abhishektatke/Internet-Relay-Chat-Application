import select
import socket
import sys
from Mediator import Functions, Room, Player
import Mediator


hostname = sys.argv[1]
sock = Mediator.create_socket((hostname, 5001))

mediator = Functions()
conn_list = []
conn_list.append(sock)

while True:
    # Player.fileno()
    read_players, write_players, error_sockets = select.select(conn_list, [], [])
    for player in read_players:
        if player is sock:
            new_conn_sock, add = player.accept()
            new_player = Player(new_conn_sock)
            conn_list.append(new_player)
            mediator.welcome_new(new_player)

        else:
            msg = player.socket.recv(4096)
            if msg:
                msg = msg.decode().lower()
                mediator.handle_msg(player, msg)

            else:
                player.socket.close()
                conn_list.remove(player)
                print 'Client ' + str(player.name) + '  is not connected anymore'



    for sock in error_sockets:
        sock.close()
        conn_list.remove(sock)
