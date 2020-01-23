from itertools import permutations
from typing import List, Dict, Tuple, Union

from cards import Card

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


def combos(cards: List[Card]):
    return permutations(cards, 5)


def get_cards_max(cards: List[Card]) -> Score:
    if len(cards) != 5:
        raise Exception("there should be 5 cards")

    match, trick_name, points = is_royal_flush(cards)
    if match:
        return Score(trick_name, points)
    match, trick_name, points = is_straight_flush(cards)
    if match:
        return Score(trick_name, points)
    match, trick_name, points = is_4_of_a_kind(cards)
    if match:
        return Score(trick_name, points)
    match, trick_name, points = is_full_house(cards)
    if match:
        return Score(trick_name, points)
    match, trick_name, points = is_flush(cards)
    if match:
        return Score(trick_name, points)
    match, trick_name, points = is_straight(cards)
    if match:
        return Score(trick_name, points)
    match, trick_name, points = is_3_of_a_kind(cards)
    if match:
        return Score(trick_name, points)
    match, trick_name, points = is_two_pair(cards)
    if match:
        return Score(trick_name, points)
    match, trick_name, points = is_2_of_a_kind(cards)
    if match:
        return Score(trick_name, points)
    else:
        high_card_code = high_card(cards)
        trick_cards = [card for card in cards if get_number(card) == high_card_code]
        trick_name = trick_str("High card", trick_cards)
        points = get_score(0, trick_cards)
        return Score(trick_name, points)


def trick_str(trick_name: str, cards: List[Card]) -> str:
    return trick_name + ": " + ", ".join([c.name for c in cards])


def get_score(trick_code: int, high_cards: Union[List[Card], None]) -> int:
    return trick_code * 13 + (0 if high_cards is None else high_card(high_cards))


def high_card(cards: List[Card]):
    return max(get_numbers(cards))


def is_royal_flush(cards: List[Card]) -> Union[Tuple[bool, str, int], Tuple[bool, None, None]]:
    if is_flush(cards) and contains(cards, ['1', '13', '12', '11', '10']):
        return True, trick_str("Royal flush", cards), get_score(9, None)
    else:
        return False, None, None


def is_straight_flush(cards: List[Card]) -> Union[Tuple[bool, str, int], Tuple[bool, None, None]]:
    if is_flush(cards)[0] and is_straight(cards)[0]:
        return True, trick_str("Straight flush", cards), get_score(8, cards)
    else:
        return False, None, None


def is_4_of_a_kind(cards: List[Card]) -> Union[Tuple[bool, str, int], Tuple[bool, None, None]]:
    match, trick_cards = is_n_of_a_kind(cards, 4)
    if match:
        return True, trick_str("4 of a kind", trick_cards), get_score(7, trick_cards)
    else:
        return False, None, None


def is_full_house(cards: List[Card]) -> Union[Tuple[bool, str, int], Tuple[bool, None, None]]:
    uniques = set(cards)
    if len(uniques) == 2:
        three_of_kind = [card for card in uniques if cards.count(card) == 3]
        True, trick_str("Full house", cards), get_score(6, three_of_kind)
    else:
        return False, None, None


def is_flush(cards: List[Card]) -> Union[Tuple[bool, str, int], Tuple[bool, None, None]]:
    if all_same([get_suit(card) for card in cards]):
        return True, trick_str("Flush", cards), get_score(5, cards)
    else:
        return False, None, None


def is_straight(cards: List[Card]) -> Union[Tuple[bool, str, int], Tuple[bool, None, None]]:
    if len(cards) < 2:
        raise Exception("you probably didn't want to call this")
    numbers = get_numbers(cards)
    numbers.sort()
    prev = cards[0]
    cards = cards[1:]
    for card in cards:
        if card.code != prev.code + 1:
            return False, None, None
        prev = card
    return True, trick_str("Straight", cards), get_score(4, cards)


def is_3_of_a_kind(cards: List[Card]) -> Union[Tuple[bool, str, int], Tuple[bool, None, None]]:
    match, trick_cards = is_n_of_a_kind(cards, 3)
    if match:
        return True, trick_str("3 of a kind", trick_cards), get_score(3, trick_cards)
    else:
        return False, None, None


def is_two_pair(cards: List[Card]) -> Union[Tuple[bool, str, int], Tuple[bool, None, None]]:
    uniques = set(cards)
    match = len(uniques) == 3
    if match:
        two_of_kinds = [card for card in uniques if cards.count(card) == 2 for _ in range(2)]
        return True, trick_str("Two pairs", two_of_kinds), get_score(2, two_of_kinds)
    else:
        return False, None, None


def is_2_of_a_kind(cards: List[Card]) -> Union[Tuple[bool, str, int], Tuple[bool, None, None]]:
    match, trick_cards = is_n_of_a_kind(cards, 2)
    if match:
        return True, trick_str("2 of a kind", trick_cards), get_score(1, trick_cards)
    else:
        return False, None, None


def is_n_of_a_kind(cards: List[Card], n) -> Union[Tuple[bool, List[Card]], Tuple[bool, None]]:
    numbers = get_numbers(cards)
    for x in reversed(range(13)):
        if is_n_of_an_x(numbers, n, x):
            trick_cards = [card for card in cards if get_number(card) == x]
            return True, trick_cards
    return False, None


def is_n_of_an_x(numbers: List[int], n, x) -> bool:
    if numbers.count(x) >= n:
        return True
    else:
        return False


def contains(cards: List[Card], card_nums) -> bool:
    numbers = get_numbers(cards)

    for num in card_nums:
        if CARD_NUMS[num] not in numbers:
            return False
    return True


def all_same(seq: List) -> bool:
    if len(seq) < 1:
        return True
    for x in seq:
        if x != seq[0]:
            return False
    return True


def get_numbers(cards: List[Card]) -> List[int]:
    return [get_number(card) for card in cards]


def get_suit(card: Card) -> int:
    return card.code // 13


def get_number(card: Card) -> int:
    return card.code % 13
