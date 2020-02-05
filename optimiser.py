from typing import List
from random import random

from dealer.main import run_game_for_n_players
from player.base_player import PokerPlayer
from player.basic_heuristic_player import high_card_player
from player.basic_heuristic_player import partial_score_player
from player.random_player import random_player

from threading import Thread

player_num = 4
rand_player_num = 2
base_value = (0.3, 0.6)
delta = 0.4


def main():
    best_value = base_value
    log = []
    for _ in range(10):
        inputs = get_new_inputs(best_value)
        results = run_some_games(inputs)
        winner = max(enumerate(results), key=lambda x: x[1])[0]
        if winner >= player_num:
            print("random won")
        else:
            best_value = inputs[winner]
            log.append((inputs, results, winner, best_value))
            for l in log:
                print(l)


def get_new_inputs(best_value):
    inputs = []
    for _ in range(player_num):
        fold_threshold, call_threshold = best_value
        fold_threshold = max(fold_threshold + random() * delta - (delta / 2), 0)
        call_threshold = max(call_threshold + random() * delta - (delta / 2), 0)
        inputs.append((fold_threshold, call_threshold))
    return inputs


def run_some_games(inputs):
    results = [0] * (player_num + rand_player_num)
    for _ in range(30):
        run_game(inputs, results)
    print(results)
    return results


def run_game(inputs, results):
    server_thread = start_server()
    players: List[PokerPlayer] = [partial_score_player(False, fold, call) for (fold, call) in inputs] \
                                 + [random_player(False) for _ in range(rand_player_num)]
    threads = []
    for i, player in enumerate(players):
        player.coms.verbose = False
        threads.append(start_player(player, results, i))
    server_thread.join()
    for thread in threads:
        thread.join()


def start_server():
    t = Thread(target=run_game_for_n_players, args=(player_num + rand_player_num,), kwargs={"verbose": False})
    t.start()
    return t


def start_player(p: PokerPlayer, results, i):
    def func():
        if p.play():
            results[i] += 1

    t = Thread(target=func)
    t.start()
    return t


if __name__ == "__main__":
    main()
