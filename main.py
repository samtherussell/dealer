 
import socket

from game import Game
from player import Player
from communicator import Communicator 


def main():

    while True:    
        num_players = 4 # int(input("# players: "))
        if num_players > 1:
            break
        print("must have more than one player")

    players = run_lobby(num_players)

    print("players:", players)

    run_game(players)


def run_lobby(num_players: int):

    ip_address = get_local_ip()
    port = 8080

    s = socket.socket()
    s.bind((ip_address, port))
    s.listen()

    print("dealer is listening at {} on port {}".format(ip_address, port))

    players = []
    names = ["a", "b", "c", "d", "e"]
    for i in range(num_players):
        conn, _ = s.accept()
        coms = Communicator(conn)
        welcome = "Welcome to the poker lobby. You are player {} of {}. Please enter name: ".format(i+1, num_players)
        coms.send(welcome)
        name = names[i] # coms.recv(20)
        wait = "Hi %s, please wait to be dealt your hand\n"%(name)
        coms.send(wait)
        print(name, "has joined the game")        
        players.append(Player(i, name, coms))
 
    print("all players have joined")
 
    return players


def get_local_ip() -> str:
    address_list = socket.gethostbyname_ex(socket.gethostname())[2]
    ip_addresses = [a for a in address_list if a.startswith("192.168.1.")]
    if len(ip_addresses) < 1:
        raise Exception("Could not find an address that looks like a local ip")
    return ip_addresses[0]


def run_game(players):

    game = Game(players)
    while not game.finished():
        game.run_hand()
    game.congratulate_winner()


if __name__ == "__main__":
    main()
