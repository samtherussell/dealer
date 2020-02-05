from typing import Callable
from math import exp
from .base_player import PokerPlayer, GameStatus
from dealer.hand_scorer import high_card


def heuristic_decide_action(get_confidence: Callable[[GameStatus], float], fold_threshold=0.3,
                            call_threshold=0.6):
    def decide_action(game_status: GameStatus, raise_available=True):

        confidence = get_confidence(game_status)
        if confidence < fold_threshold:
            return "Fold"
        elif confidence < call_threshold or not raise_available:
            return "Call"
        else:
            possible_amount = game_status.you.holdings + game_status.your_bet - game_status.pot_bet
            amount = round(possible_amount * confidence * 0.5 * (1 + exp(-possible_amount + 1)))
            print(game_status.you.holdings, game_status.pot_bet, confidence, amount)
            if amount == 0:
                return "Call"
            return "Raise", amount
    return decide_action


def high_card_confidence(game_status: GameStatus) -> float:
    return high_card(game_status.hand + game_status.community_cards) / 13


def high_card_player():
    return PokerPlayer(heuristic_decide_action(high_card_confidence))

