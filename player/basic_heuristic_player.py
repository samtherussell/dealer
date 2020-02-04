import random
from base_player import PokerPlayer, GameStatus
from hand_scorer import high_card


def decide_action(game_status: GameStatus, raise_available=True):

    confidence = get_confidence(game_status)

    if confidence < 0.3:
        return "Fold"
    elif confidence < 0.6 or not raise_available:
        return "Call"
    else:
        amount = int(game_status.you.holdings * confidence * 0.5)
        return "Raise", amount


def get_confidence(game_status: GameStatus):
    return high_card(game_status.hand + game_status.community_cards) / 13


def main():
    player = PokerPlayer(decide_action)
    player.play()


if __name__ == "__main__":
    main()
