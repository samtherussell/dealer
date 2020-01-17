from itertools import permutations

CARD_NUMS = { str(i+1):i for i in range(13)}
CARD_SUITS = dict(enumerate(["spades", "hearts", "clubs", "diamonds"]))

def get_hand_max(cards):
    if len(cards) != 7:
        raise Exception("there should be 7 cards")
    return max([get_cards_max(cards) for cards in combos(cards)], key=lambda x: x[1])

def get_cards_max(cards):
    if len(cards) != 5:
        raise Exception("there should be 5 cards")
    card_codes = [c.code for c in cards]
    card_names = ", ".join([c.name for c in cards])
    
    def result(trick_name, trick_ranking):
        return trick_name + ": " + card_names, score(card_codes, trick_ranking)

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

def score(cards, trick_ranking):
    return trick_ranking * 13 + (0 if cards is None else high_card(cards))

def high_card(cards):
    return max(get_numbers(cards))

def combos(cards):
    return permutations(cards, 5)

def is_royal_flush(cards):
     return is_flush(cards) and contains(cards, ['1', '13', '12', '11', '10'])

def is_straight_flush(cards):
    return is_flush(cards) and is_straight(cards)
    
def is_straight(cards):
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

def is_full_house(cards):
    return len(set(cards)) == 2

def is_two_pair(cards):
    return len(set(cards)) == 3

def is_n_of_a_kind(cards, n):
    numbers = get_numbers(cards)
    for num in reversed(range(13)):
        if is_n_of_an_X(numbers, n, num):
            return True
    return False

def is_n_of_an_X(numbers, n, x):
    return numbers.count(x) >= n

def contains(cards, card_nums):
    numbers = get_numbers(cards)

    for num in card_nums:
        if CARD_NUMS[num] not in numbers:
            return False
    return True

def is_flush(cards):
    return all_same([get_suit(card) for card in cards])

def all_same(seq):
    if len(seq) < 1:
        return True
    for x in seq:
        if x != seq[0]:
            return False
    return True

def get_numbers(cards):
    return [get_number(card) for card in cards]

def get_suit(card):
    return card // 13

def get_number(card):
    return card % 13
