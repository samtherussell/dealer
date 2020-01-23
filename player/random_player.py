import random
from base_player import PokerPlayer


class RandomPokerPlayer(PokerPlayer):

    def decide_action(self, game_status, raise_available=True):
        print("Current state:", str(game_status))
        options = [lambda: "Fold", lambda: "Call", lambda: ("Raise",random.randint(1, 100))]
        if raise_available:
            result = options[random.randint(0, 2)]()
        else:
            result = options[random.randint(0, 1)]()
        return result

def main():
    player = RandomPokerPlayer()
    player.play()


if __name__ == "__main__":
    main()