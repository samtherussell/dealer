 
import random
import socket

from game import Game
from player import Player
from communicator import Communicator 
 
def main():
    
    num_players = int(input("# players: "))
    players = run_lobby(num_players)
 
    print("players:", players)
 
    run_game(players)
 
def run_lobby(num_players):

    ip_address = socket.gethostbyname(socket.gethostname())
    port = 8080
    
    s = socket.socket()
    s.bind((ip_address, port))
    s.listen()

    print("dealer is listening at {} on port {}".format(ip_address, port))
 
    players = []
 
    for i in range(num_players):
        conn, addr = s.accept()
        coms = Communicator(conn)
        welcome = "Welcome to the poker lobby. You are player {} of {}. Please enter name: ".format(i+1, num_players)
        coms.send(welcome)
        name = coms.recv(20)
        wait = "Hi %s, please wait to be dealt your hand\n"%(name)
        coms.send(wait)
        print(name, "has joined the game")        
        players.append(Player(i, name, coms))
 
    print("all players have joined")
 
    return players
 
def run_game(players):
 
    game = Game(players)
    while not game.finished():
        game.run_hand()
       
if __name__ == "__main__":
    main()
