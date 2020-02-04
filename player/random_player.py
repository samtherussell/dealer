import random
from base_player import PokerPlayer, GameStatus


def decide_action(game_status: GameStatus, raise_available=True):
    options = [lambda: "Fold", lambda: "Call", lambda: ("Raise", random.randint(1, game_status.you.holdings))]
    if raise_available:
        result = options[random.randint(0, 2)]()
    else:
        result = options[random.randint(0, 1)]()
    return result


def main():
    player = PokerPlayer(decide_action)
    player.play()


if __name__ == "__main__":
    main()