from player.random_player import random_player
from player.basic_heuristic_player import high_card_player


def main():

    # player = random_player()
    player = high_card_player()
    player.play()


if __name__ == "__main__":
    main()