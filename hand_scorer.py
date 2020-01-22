from itertools import permutations
from typing import List, Dict, Tuple, Union

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

    def result(trick_name: str, trick_card_codes: List[int], trick_ranking: int) -> Score:
        return Score(trick_name + ": " + card_names, score(trick_card_codes, trick_ranking))

    match, trick_cards = is_royal_flush(card_codes)
    if match:
        return result("Royal flush", trick_cards, 9)
    match, trick_cards = is_straight_flush(card_codes)
    if match:
        return result("Straight flush", trick_cards, 8)
    match, trick_cards = is_n_of_a_kind(card_codes, 4)
    if match:
        return result("4 of a kind", trick_cards, 7)
    match, trick_cards = is_full_house(card_codes)
    if match:
        return result("Full house", trick_cards, 6)
    match, trick_cards = is_flush(card_codes)
    if match:
        return result("Flush", trick_cards, 5)
    match, trick_cards = is_straight(card_codes)
    if match:
        return result("Straight", trick_cards, 4)
    match, trick_cards = is_n_of_a_kind(card_codes, 3)
    if match:
        return result("3 of a kind", trick_cards, 3)
    match, trick_cards = is_two_pair(card_codes)
    if match:
        return result("Two pairs", trick_cards, 2)
    match, trick_cards = is_n_of_a_kind(card_codes, 2)
    if match:
        return result("One pair", trick_cards, 1)
    else:
        return result("High card", trick_cards, 0)


def score(cards: List[int], trick_ranking: int) -> int:
    return trick_ranking * 13 + (0 if cards is None else high_card(cards))


def high_card(cards: List[int]):
    return max(get_numbers(cards))


def combos(cards: List[Card]):
    return permutations(cards, 5)


def is_royal_flush(cards: List[int]) -> Tuple[bool, List[int]]:
    return is_flush(cards) and contains(cards, ['1', '13', '12', '11', '10']), cards


def is_straight_flush(cards: List[int]) -> Tuple[bool, List[int]]:
    return is_flush(cards) and is_straight(cards), cards


def is_straight(cards: List[int]) -> Tuple[bool, Union[List[int], None]]:
    if len(cards) < 2:
        raise Exception("you probably didn't want to call this")
    numbers = get_numbers(cards)
    numbers.sort()
    prev = cards[0]
    cards = cards[1:]
    for card in cards:
        if card != prev + 1:
            return False, None
        prev = card
    return True, cards


def is_full_house(cards: List[int]) -> Tuple[bool, List[int]]:
    return len(set(cards)) == 2, cards


def is_two_pair(cards: List[int]) -> Tuple[bool, Union[List[int], None]]:
    uniques = set(cards)
    match = len(uniques) == 3
    if match:
        return True, [card for card in uniques if cards.count(card) == 2]
    else:
        return False, None


def is_n_of_a_kind(cards: List[int], n) -> Tuple[bool, Union[List[int], None]]:
    numbers = get_numbers(cards)
    for num in reversed(range(13)):
        match, trick_cards = is_n_of_an_x(numbers, n, num)
        if match:
            return True, trick_cards
    return False, None


def is_n_of_an_x(numbers, n, x) -> Tuple[bool, Union[List[int], None]]:
    if numbers.count(x) >= n:
        return True, [x for _ in range(n)]
    else:
        return False, None


def contains(cards: List[int], card_nums) -> bool:
    numbers = get_numbers(cards)

    for num in card_nums:
        if CARD_NUMS[num] not in numbers:
            return False
    return True


def is_flush(cards: List[int]) -> bool:
    return all_same([get_suit(card) for card in cards])


def all_same(seq: List) -> bool:
    if len(seq) < 1:
        return True
    for x in seq:
        if x != seq[0]:
            return False
    return True


def get_numbers(cards: List[int]) -> List[int]:
    return [get_number(card) for card in cards]


def get_suit(card: int) -> int:
    return card // 13


def get_number(card: int) -> int:
    return card % 13
