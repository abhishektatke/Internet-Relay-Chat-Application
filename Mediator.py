import socket
QUIT_STRING = '<$quit$>'
def create_socket(address):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setblocking(0)
    s.bind(address)
    s.listen(10)
    print("You are listening to the address: ", address)
    return s


class Functions:
    counter = 0
    def __init__(self):
        self.rooms = {}
        self.room_player_map = {}
        self.player_room_map = {}
        self.player_list = {}
 #       self.list_rooms = {}

    def welcome_new(self, new_player):
        new_player.socket.sendall('Welcome to the chat application!\nPlease enter your name:\n')

    def list_rooms(self, player):

        if len(self.rooms) == 0:
            msg = 'There are no chatrooms active at this time, please use join command to create one\n'
            player.socket.sendall(msg.encode())
        else:

            msg = 'The available Chatrooms are: \n'
            for room in self.rooms:
                msg += room + ": " + str(len(self.rooms[room].players)) + " player(s)\n"
            player.socket.sendall(msg.encode())

    def handle_msg(self, player, msg):

        instructions = '*******************Helpdesk:*********************\n' \
		       + '*****************listrooms:********************\n' \
                       + 'Lists all the chatrooms\n' \
                       + '*****************join room_name:*******************\n' \
                       + 'To Join/create to a room\n' \
                       + '*****************listmembers room_name:********************\n' \
                       + 'List all members in the available rooms room\n' \
                       + '*****************send room_name sender_name msg:********************\n' \
                       + 'To send message to a particular room\n' \
                       + '*****************leave room_name:********************\n' \
                       + 'To leave from the specified room\n' \
                       + '*****************helpdesk: ********************\n' \
                       + 'For helpdesk\n' \
                       + '*****************quit:********************\n' \
                       + 'To quit\n' \
                       + '*****************private receiver message:********************\n' \
                       + 'to send private message to any user\n' \
                       + '\n'

        if "username:" in msg:
            name = msg.split()[1]
            player.name = name
            self.player_list[name] = player.socket
            print("There is new Client connection from ", player.name)
            player.socket.sendall(instructions)

        elif "join" in msg:
            same_room = False
            if len(msg.split()) >= 2:
                room_name = msg.split()[1]
                if player.name in self.room_player_map:
                    if self.room_player_map[player.name] == room_name:
                        player.socket.sendall(b'You are already part of the room: ' + room_name.encode())
                        same_room = True

                if not same_room:
                    if not room_name in self.rooms:
                        new_room = Room(room_name)
                        self.rooms[room_name] = new_room
                    self.rooms[room_name].players.append(player)

                    self.rooms[room_name].welcome_new(player)
                    print 'Client who joined is: ' + player.name
                    self.room_player_map[player.name] = room_name
                    print 'mapped value is: ' + str(self.room_player_map[player.name]) + '\n'
                    if room_name in self.player_room_map:
                        name = player.name
                        self.player_room_map[room_name].append(name)
                    else:
                        name = player.name
                        self.player_room_map[room_name] = list()
                        self.player_room_map[room_name].append(name)
            else:
                player.socket.sendall(instructions)



        elif "leave" in msg:
            room_name = msg.split()[1]
            if player.name in self.room_player_map:
                try:

                    if room_name in self.player_room_map:
                        if player.name in self.player_room_map[room_name]:
                            self.rooms[room_name].remove_player(player)
                            self.player_room_map[room_name].remove(player.name)
                            print 'You have left successfully'
                            msg = 'Client Left successfully' + '\n'
                            player.socket.sendall(msg.encode())
                except:
                    msg += 'Sorry!You are not part of this room, try again after joining' + '\n'
                    player.socket.sendall(msg.encode())
            else:
                print('you are not part of this room')

        elif "listmembers" in msg:
            if len(msg.split()) >= 2:
               room_name = msg.split()[1]
               self.list_members(player,room_name)

        elif "listrooms" in msg:
            self.list_rooms(player)

        elif "helpdesk" in msg:
            player.socket.sendall(instructions)

        elif "quit" in msg:
            player.socket.sendall(QUIT_STRING.encode())
            self.remove_player(player)

        elif "private" in msg:
            self.private_sending(player,msg)

        elif "send" in msg:
            room_name = msg.split()[1]
            print room_name
            player.name = msg.split()[2]
            print 'Message sent by ' + player.name
            message = msg.split()[3]
            print 'Message is: ' + message
            if player.name in self.player_room_map[room_name]:
                list_players = self.player_room_map[room_name]
                print 'Clients in ' + str(list_players)
                for players in list_players:
                    print ''.join(str(players)) + '\n'
                self.broadcast_multiple(room_name, player.name,message)
            else:
                msg += 'Not part of this room, try again after joining\n'
                player.socket.sendall(msg.encode())


        else:
            if player.name in self.room_player_map:
                self.rooms[self.room_player_map[player.name]].broadcast(player, msg.encode())
            else:
                msg = 'You are not part of this room, please see the commands from helpdesk to join\n'
                player.socket.sendall(msg.encode())

    def broadcast_multiple(self, room_name, player, msg):
            self.rooms[room_name].multiple(player, msg.encode())


    def list_members(self,player,room):
        room_name = room
        print 'room_name is: ' + room_name
        msg = 'Members are: ' + ' \n'
        if room_name in self.rooms:
            try:
                members = self.player_room_map[room_name]
                print 'members in room are' + str(members) + '\n'
                for i in members:
                    msg += (str(i)) + '\n'
                player.socket.sendall(msg)
            except:
                msg += 'The room is empty' + '\n'
                player.socket.sendall(msg.encode())
        else:
            msg = 'There is no room with the name specified'
            player.socket.sendall(msg.encode())

    def private_sending(self, sender, msg):
        receiver = msg.split()[1]
        if receiver in self.player_list:
            user = self.player_list[receiver]
            try:
                user.sendall('Private chat from ' + sender.name + ': ' + msg.rsplit(receiver, 1)[1] + '\n')
            except:
                sender.socket.sendall('receiver not present, Please check and try again')
        else:
            msg += 'Receiver not present, please check and try again' + '\n'

    def remove_player(self, player):
        if player.name in self.room_player_map:
            self.rooms[self.room_player_map[player.name]].remove_player(player)
            del self.room_player_map[player.name]
        print("Client: " + player.name + " has left\n")


class Room:
    def __init__(self, name):
        self.players = []
        self.name = name

    def welcome_new(self, from_player):
        msg = self.name + " welcomes: " + from_player.name + "to this room"+ '\n'
        for player in self.players:
            player.socket.sendall(msg.encode())

    def broadcast(self, from_player, msg):
        msg = from_player.name.encode() + ":" + msg
        for player in self.players:
            player.socket.sendall(msg)

    def multiple(self, from_player, msg):
        msg = from_player + " says: " + msg + '\n'
        for player in self.players:
            player.socket.sendall(msg)

    def remove_player(self, player):
        self.players.remove(player)
        leave_msg = player.name.encode() + " has left the room\n"
        self.broadcast(player, leave_msg)


class Player:
    def __init__(self, socket, name="new"):
        socket.setblocking(0)
        self.socket = socket
        self.name = name


    def fileno(self):
       return self.socket.fileno()
