from os.path import dirname, join
from typing import List

from dealer.cards import Card, deck
from dealer.hand_scorer import all_same, get_suit


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
        return lookup[k]
    return func



from_file()(deck)