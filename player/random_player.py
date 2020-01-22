import random
from base_player import PokerPlayer


class RandomPokerPlayer(PokerPlayer):

    def decide_action(self, game_status, raise_available=True):
        options = [lambda: "Fold", lambda: "Call", lambda: "Raise",int(random.random() * 100)]
        if raise_available:
            return options[random.randint(0, 2)]()
        else:
            return options[random.random(0, 1)]()


def main():
    player = RandomPokerPlayer()
    player.play()


if __name__ == "__main__":
    main()