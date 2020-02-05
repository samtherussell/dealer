 
import socket

from .game import Game
from .player import Player
from .communicator import Communicator


def run_game_for_n_players(num_players, verbose=True):
    players = run_lobby(num_players, verbose=verbose)
    if verbose:
        print("players:", players)
    run_game(players, verbose=verbose)


def run_lobby(num_players: int, verbose=True):

    ip_address = get_local_ip()
    port = 8080

    s = socket.socket()
    s.bind((ip_address, port))
    s.listen()

    if verbose:
        print("dealer is listening at {} on port {}".format(ip_address, port))

    players = []
    names = []
    for i in range(num_players):
        conn, _ = s.accept()
        coms = Communicator(conn, verbose=verbose)
        coms.send("Welcome to the poker lobby. You are player {} of {}. Please enter name: ".format(i+1, num_players))
        while True:
            name: str = coms.recv(20)
            if name in names:
                coms.send("Someone else has that name. Please enter a different name: ")
            elif ',' in name or " " in name:
                coms.send("Name cannot contain the ',' character. Please enter a different name: ")
            else:
                names.append(name)
                break
        coms.send("Hi %s, please wait to be dealt your hand\n"%(name))
        if verbose:
            print(name, "has joined the game")
        coms.name = name
        players.append(Player(i, name, coms))

    if verbose:
        print("all players have joined")
 
    return players


def get_local_ip() -> str:
    address_list = socket.gethostbyname_ex(socket.gethostname())[2]
    ip_addresses = [a for a in address_list if a.startswith("192.168.1.")]
    if len(ip_addresses) < 1:
        raise Exception("Could not find an address that looks like a local ip")
    return ip_addresses[0]


def run_game(players, verbose=True):

    game = Game(players, verbose=verbose)
    while not game.finished():
        game.run_hand()
    game.congratulate_winner()
