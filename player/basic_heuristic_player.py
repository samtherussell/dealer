from typing import Callable, List
from math import exp
from os.path import join, dirname

from dealer.cards import Card
from .base_player import PokerPlayer, GameStatus
from dealer.hand_scorer import high_card, get_partial_hand_max, get_cards_max, all_same, get_suit


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
            if amount == 0:
                return "Call"
            return "Raise", amount

    return decide_action


def high_card_confidence(game_status: GameStatus) -> float:
    return high_card(game_status.hand + game_status.community_cards) / 13


def partial_score_confidence(game_status: GameStatus) -> float:
    cards = game_status.hand + game_status.community_cards
    if len(cards) < 5:
        return hand_start_scorer(cards) / 3
    else:
        return get_partial_hand_max(cards).value / (9*13)


def from_file():
    with open(join(dirname(__file__), "poker_hands.txt")) as f:
        lines = f.readlines()
    lookup = {}
    for line in lines:
        k, v = line.strip().split("\t", 1)
        lookup[k] = v

    def func(cards: List[Card]) -> float:
        k = "".join([card.name.split(" ")[0] for card in cards])
        if all_same([get_suit(card) for card in cards]):
            k += "s"
        if k in lookup:
            return float(lookup[k])
        else:
            return 0
    return func


hand_start_scorer = from_file()


def high_card_player(verbose, fold_threshold, call_threshold):
    return PokerPlayer(
        heuristic_decide_action(high_card_confidence, fold_threshold=fold_threshold, call_threshold=call_threshold),
        verbose=verbose)


def partial_score_player(verbose, fold_threshold, call_threshold):
    return PokerPlayer(
        heuristic_decide_action(partial_score_confidence, fold_threshold=fold_threshold, call_threshold=call_threshold),
        verbose=verbose)
