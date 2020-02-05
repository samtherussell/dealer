from typing import List

from dealer.main import run_game_for_n_players
from player.random_player import random_player
from player.base_player import PokerPlayer
from player.basic_heuristic_player import high_card_player

from threading import Thread

player_num = 6


def start_server():
    Thread(target=run_game_for_n_players, args=(player_num,)).start()


def start_player(p: PokerPlayer):
    Thread(target=p.play).start()


start_server()

players: List[PokerPlayer] = [random_player() for _ in range(player_num//2)] \
                          + [high_card_player() for _ in range(player_num//2)]
for player in players:
    player.coms.verbose = False
    start_player(player)





