from itertools import permutations
from typing import List, Dict

from card import Card

CARD_NUMS = {str(i+1): i for i in range(13)}
CARD_SUITS: Dict[int, str] = dict(enumerate(["spades", "hearts", "clubs", "diamonds"]))


class Score:

    def __init__(self, trick_name: str, value: int):
        self.trick_name = trick_name
        self.value = value

    def __repr__(self):
        return "{} [{}]".format(self.trick_name, self.value)

def get_hand_max(cards: List[Card]) -> Score:
    if len(cards) != 7:
        raise Exception("there should be 7 cards")
    return max([get_cards_max(cards) for cards in combos(cards)], key=lambda x: x.value)


def get_cards_max(cards: List[Card]) -> Score:
    if len(cards) != 5:
        raise Exception("there should be 5 cards")
    card_codes = [c.code for c in cards]
    card_names = ", ".join([c.name for c in cards])

    def result(trick_name: str, trick_ranking: int) -> Score:
        return Score(trick_name + ": " + card_names, score(card_codes, trick_ranking))

    if is_royal_flush(card_codes):
        return result("Royal flush", 9)
    elif is_straight_flush(card_codes):
        return result("Straight flush", 8)
    elif is_n_of_a_kind(card_codes, 4):
        return result("4 of a kind", 7)
    elif is_full_house(card_codes):
        return result("Full house", 6)
    elif is_flush(card_codes):
        return result("Flush", 5)
    elif is_straight(card_codes):
        return result("Straight", 4)
    elif is_n_of_a_kind(card_codes, 3):
        return result("3 of a kind", 3)
    elif is_two_pair(card_codes):
        return result("Two pairs", 2)
    elif is_n_of_a_kind(card_codes, 2):
        return result("One pair", 1)
    else:
        return result("High card", 0)


def score(cards: List[int], trick_ranking: int) -> int:
    return trick_ranking * 13 + (0 if cards is None else high_card(cards))


def high_card(cards: List[int]):
    return max(get_numbers(cards))


def combos(cards: List[Card]):
    return permutations(cards, 5)


def is_royal_flush(cards: List[int]):
    return is_flush(cards) and contains(cards, ['1', '13', '12', '11', '10'])


def is_straight_flush(cards: List[int]):
    return is_flush(cards) and is_straight(cards)


def is_straight(cards: List[int]):
    if len(cards) < 2:
        raise Exception("you probably didn't want to call this")
    numbers = get_numbers(cards)
    numbers.sort()
    prev = cards[0]
    cards = cards[1:]
    for card in cards:
        if card != prev + 1:
            return False
        prev = card
    return True


def is_full_house(cards: List[int]):
    return len(set(cards)) == 2


def is_two_pair(cards: List[int]):
    return len(set(cards)) == 3


def is_n_of_a_kind(cards: List[int], n):
    numbers = get_numbers(cards)
    for num in reversed(range(13)):
        if is_n_of_an_x(numbers, n, num):
            return True
    return False


def is_n_of_an_x(numbers, n, x):
    return numbers.count(x) >= n


def contains(cards: List[int], card_nums):
    numbers = get_numbers(cards)

    for num in card_nums:
        if CARD_NUMS[num] not in numbers:
            return False
    return True


def is_flush(cards: List[int]):
    return all_same([get_suit(card) for card in cards])


def all_same(seq: List):
    if len(seq) < 1:
        return True
    for x in seq:
        if x != seq[0]:
            return False
    return True


def get_numbers(cards: List[int]):
    return [get_number(card) for card in cards]


def get_suit(card: int):
    return card // 13


def get_number(card: int):
    return card % 13
