from typing import List, Tuple, Set

from .player import Player
from .hand_scorer import get_hand_max, Score
from .cards import Card


class HandPlayer(Player):

    def __init__(self, player: Player, hand: List[Card]):
        super().__init__(player.ID, player.name, player.coms, player.holdings)
        self.bet_amount = 0
        self.folded = False
        self.hand = hand

    def bet(self, amount: int):
        super().bet(amount)
        self.bet_amount += amount

    def fold(self):
        self.folded = True


class Pot:

    def __init__(self, amount: int, bet: int, players: List[HandPlayer]):
        self.amount = amount
        self.bet = bet
        self.playing_players = players

    def __repr__(self):
        return "Pot(amount={}, bet={}, players={})".format(self.amount, self.bet, self.playing_players)


class Bet:

    def __init__(self, amount: int, who: HandPlayer):
        self.amount = amount
        self.who = who

    def __repr__(self):
        return "Bet(who={}, amount={})".format(self.who, self.amount)


class Bets(dict):

    def total_raise(self):
        total = 0
        for ID in self:
            total += self[ID].amount
        return total

    def max_raise(self):
        return max((self[ID].amount for ID in self)) if len(self) > 0 else 0


def deal_hands(deck, num_players: int) -> List[List[Card]]:
    hands = [[] for _ in range(num_players)]

    for i in range(2):
        for p in range(num_players):
            hands[p].append(deck.pop())

    return hands


def deal_comm_cards(deck: List[Card], discard: List[Card]) -> List[Card]:
    comm_cards: List[Card] = []
    deal_order = [discard, comm_cards, comm_cards, comm_cards, discard, comm_cards, discard, comm_cards]
    for pile in deal_order:
        pile.append(deck.pop())

    return comm_cards


def get_players_options(current_player: HandPlayer, current_bet: int, has_bet: Set[int]) -> List[str]:
    options = ["Fold", "Call"]
    diff = current_bet - current_player.bet_amount
    if current_player.ID not in has_bet and current_player.holdings > diff:
        options.append("Raise")
    has_bet.add(current_player.ID)
    return options


def get_raise_amount(action: str) -> int:
    action = action.split(" ")
    if len(action) != 2:
        raise Exception("there is no amount to raise by")
    num = int(action[1])
    if num <= 0:
        raise Exception("raise amount must be positive")
    return num


class OnePlayerLeftException(Exception):
    def __init__(self, player: Player):
        self.player = player


def get_winners(scores: List[Tuple[Player, int]]):
    winning_score: int = scores[0][1]
    winners: List[Player] = [scores[0][0]]
    i = 1
    while i < len(scores) and scores[i][1] == winning_score:
        winners.append(scores[i][0])
        i += 1
    return winners


class Hand:

    def __init__(self, players: List[Player], deck: List[Card], start_pos: int, round_num: int):

        self.deck = deck
        self.all_players = players

        self.discard: List[Card] = []
        self.hands = deal_hands(self.deck, len(players))
        self.all_hand_players = [HandPlayer(p, h) for p, h in zip(players, self.hands)]
        self.face_down_community_cards = deal_comm_cards(self.deck, self.discard)
        self.face_up_community_cards = []

        self.start_pos: int = start_pos
        self.round_num: int = round_num
        self.top_pot: Pot = Pot(0, 0, list(self.all_hand_players))
        self.pots: List[Pot] = [self.top_pot]

        print("Hand initiated:", str(self))

    def put_cards_back_in_deck(self):
        self.deck.extend(self.discard)
        self.deck.extend([card for hand in self.hands for card in hand])
        self.deck.extend(self.face_up_community_cards)
        self.deck.extend(self.face_down_community_cards)

    def run(self):

        self.notify_players("---- New Hand :: Round {} ----".format(self.round_num))
        self.notify_player_statuses()
        self.deal_hands()

        self.run_bet_round(blinds=True)
        self.reveal_cards(3)
        self.run_bet_round()
        self.reveal_cards(1)
        self.run_bet_round()
        self.reveal_cards(1)
        self.run_bet_round()
        self.decide_winner()

        self.put_cards_back_in_deck()
        self.update_player_holdings()

    def update_player_holdings(self):
        for player, hand_player in zip(self.all_players, self.all_hand_players):
            player.holdings = hand_player.holdings

    def notify_players(self, s, exclude=None):
        print("Sending to all {}".format(s))
        for player in self.all_hand_players:
            if exclude is None \
                    or type(exclude) == int and player.ID is not exclude \
                    or type(exclude) == list and player.ID not in exclude:
                player.coms.send_line(s, verbose=False)

    def notify_player_statuses(self):

        self.notify_players("The following players are still in: " + ", ".join([p.name for p in self.all_hand_players]))
        self.notify_players("Money left")

        for player in self.all_hand_players:
            player.coms.send_line("You: {}".format(player.holdings), verbose=False)
            self.notify_players("{}: {}".format(player.name, player.holdings), exclude=player.ID)

    def get_blinds(self, small_blind=5, big_blind=10) -> List[Bet]:
        if self.start_pos > len(self.top_pot.playing_players):
            raise Exception("start position {} larger than number of players".format(self.start_pos))

        if small_blind > big_blind:
            raise Exception("Small blind is bigger than big blind")

        small_blind_enable = len(self.top_pot.playing_players) > 2

        self.notify_players("Big blind is {}".format(big_blind))
        self.notify_players("Small blind is {}".format(small_blind if small_blind_enable else 0))

        bets = []
        for i, player in enumerate(self.top_pot.playing_players):
            if i == (self.start_pos - 1) % len(self.top_pot.playing_players):
                blind = min(big_blind, player.holdings)
                player.bet(blind)
                player.coms.send_line("You are big blind")
                bets.append(Bet(blind, player))
            elif small_blind_enable and i == (self.start_pos - 2) % len(self.top_pot.playing_players):
                blind = min(small_blind, player.holdings)
                player.bet(blind)
                player.coms.send_line("You are small blind")
                bets.append(Bet(blind, player))
            else:
                player.coms.send_line("You are not the blind", verbose=False)

        return bets

    def deal_hands(self):
        for player in self.top_pot.playing_players:
            player.coms.send_hand(player.hand)
        print("dealt hands")

    def mod(self, index: int) -> int:
        x = len(self.top_pot.playing_players)
        if x == 0:
            return 0
        else:
            return index % x

    def prev(self, index: int) -> int:
        return self.mod(index - 1)

    def next(self, index: int) -> int:
        return self.mod(index + 1)

    def run_bet_round(self, blinds=False):

        if len(self.top_pot.playing_players) < 2:
            return

        has_bet = set()
        bets = Bets()

        if blinds:
            for bet in self.get_blinds():
                bets[bet.who.ID] = bet

        current_index: int = self.start_pos
        round_end_index = self.prev(current_index)
        while len([p for p in self.top_pot.playing_players if not p.folded and p.has_money()]) > 1:
            current_player = self.top_pot.playing_players[current_index]
            if current_player.folded:
                current_player.coms.send_line("You have folded so cannot bet")
            elif not current_player.has_money():
                current_player.coms.send_line("You have no more money so cannot bet")
            else:
                available_options = get_players_options(current_player, self.top_pot.bet + bets.max_raise(), has_bet)
                current_player.coms.send_line(self.get_player_status(bets, current_player))

                reset_round_end_index = self.get_and_run_player_action(available_options, bets, current_player)

                if reset_round_end_index:
                    round_end_index = self.prev(current_index)

            if current_index == round_end_index:
                break
            current_index = self.next(current_index)

        self.add_bets_to_pots(bets)

        self.start_pos = self.mod(self.start_pos)

    def get_player_status(self, bets, current_player):
        current_pot = self.top_pot.amount + bets.total_raise()
        current_pot_bet = self.top_pot.bet + bets.max_raise()
        current_player_bet = current_player.bet_amount
        current_player_holdings = current_player.holdings
        status = "Current pot: {}\nCurrent pot bet: {}\nYour current bet: {}\nYour holdings: {}" \
            .format(current_pot, current_pot_bet, current_player_bet, current_player_holdings)
        return status

    def add_bets_to_pots(self, bets: Bets):
        max_raise = bets.max_raise()
        if all([bets[ID].amount == max_raise for ID in bets]):
            self.top_pot.bet += max_raise
            self.top_pot.amount += bets.total_raise()
            self.top_pot.playing_players = [p for p in self.top_pot.playing_players if not p.folded]
        else:
            bets = list(bets.values())
            bets.sort(key=lambda x: x.amount)
            current_pot = self.pots.pop()
            base_pot_amount = current_pot.amount
            prev_pot_bet = current_pot.bet
            while len(bets) > 0:
                bet = bets[0]
                bet_amount = bet.amount
                new_bet = bet_amount + prev_pot_bet
                new_pot = base_pot_amount + bet_amount * len(bets)
                pot_players = [bet.who for bet in bets if not bet.who.folded]
                self.pots.append(Pot(new_pot, new_bet, pot_players))
                for b in bets:
                    b.amount -= bet_amount
                bets = [bet for bet in bets if bet.amount > 0]
                prev_pot_bet = new_bet
                base_pot_amount = 0
            self.top_pot = self.pots[-1]

    def get_and_run_player_action(self, available_options: List[str], bets: Bets, current_player: HandPlayer) -> bool:
        while True:
            current_player.coms.send_line("/".join(available_options))
            action = current_player.coms.recv(20)

            try:
                display, reset_round_end_index = self.run_player_action(available_options, bets, current_player, action)
                current_player.coms.send_line("SUCCESS")
                break
            except Exception as e:
                current_player.coms.send_line("ERROR: {}".format(e))

        self.notify_players("Opponent action: {} {}".format(current_player.name, display), exclude=current_player.ID)
        return reset_round_end_index

    def run_player_action(self, available_options: List[str], bets: Bets, current_player: HandPlayer, action: str) \
            -> Tuple[str, bool]:

        if action == "Fold":
            current_player.fold()
            return "Folded", False
        elif action == "Call":
            self.call_bet(current_player, bets)
            return "Called", False
        elif "Raise" in available_options and action.startswith("Raise"):
            display = self.raise_bet(current_player, action, bets)
            return display, True
        elif action == "Money":
            current_player.holdings += 100
            raise Exception("Money added")
        else:
            raise Exception("Invalid command")

    def call_bet(self, current_player, bets):
        current_max_bet = self.top_pot.bet + bets.max_raise()
        diff = min(current_max_bet - current_player.bet_amount, current_player.holdings)
        current_player.bet(diff)
        if current_player.ID in bets:
            bets[current_player.ID].amount += diff
        else:
            bets[current_player.ID] = Bet(diff, current_player)

    def raise_bet(self, current_player, action, bets):
        raise_amount = get_raise_amount(action)
        current_max_bet = self.top_pot.bet + bets.max_raise()
        diff = (current_max_bet - current_player.bet_amount) + raise_amount
        if current_player.holdings < diff:
            raise Exception("not enough money to raise by " + str(raise_amount))
        current_player.bet(diff)
        if current_player.ID in bets:
            bets[current_player.ID].amount += diff
        else:
            bets[current_player.ID] = Bet(diff, current_player)
        return "Raised by {} to {}".format(raise_amount, current_player.bet_amount)

    def reveal_cards(self, num):
        cards = self.face_down_community_cards[:num]
        for player in self.top_pot.playing_players:
            player.coms.send_card_reveal(cards)

        self.face_down_community_cards = self.face_down_community_cards[num:]
        self.face_up_community_cards = self.face_up_community_cards + cards
        print("revealed cards:", cards)

    def decide_winner(self):

        def score_player_hand(player: HandPlayer) -> Tuple[HandPlayer, Score]:
            return player, get_hand_max(player.hand + self.face_up_community_cards)

        scores: List[Tuple[HandPlayer, Score]] = [score_player_hand(player) for player in self.all_hand_players \
                                                  if not player.folded]
        scores.sort(key=lambda x: x[1].value, reverse=True)

        print("SCORES:", scores)
        self.notify_players("Results [{}]".format(len(scores)))

        for score in scores:
            player = score[0]
            trick_name = score[1].trick_name
            self.notify_players("{} got {}".format(player.name, trick_name), exclude=player.ID)

        for score in scores:
            player = score[0]
            trick_name = score[1].trick_name
            player.coms.send_line("You got {}".format(trick_name), verbose=False)

        self.notify_players("Pots [{}]".format(len(self.pots)))
        winnings = {player.ID: 0 for player in self.all_hand_players}
        print("POTS:", self.pots)
        for pot in self.pots:
            pot_amount = pot.amount
            player_ids = [p.ID for p in pot.playing_players]
            pot_scores = [(p[0], p[1].value) for p in scores if p[0].ID in player_ids]
            winners = get_winners(pot_scores)
            share = int(pot_amount / len(winners))
            self.notify_players("{} win {} bet pot worth {} giving {} each"
                                .format(", ".join((w.name for w in winners)), pot.bet, pot.amount, share))
            for winner in winners:
                winnings[winner.ID] += share

        self.notify_players("Winnings")
        for player in self.all_hand_players:
            amount = winnings[player.ID]
            player.win(amount)
            player.coms.send_line("In total you won {}".format(amount), verbose=False)
            self.notify_players("In total {} won {}".format(player.name, amount), exclude=player.ID)

    def __repr__(self):
        return "players={}, hands={}, face_up_community_card={}, face_down_community_cards={}, pot={}" \
            .format(self.top_pot.playing_players, self.hands, self.face_up_community_cards,
                    self.face_down_community_cards, self.top_pot.amount)
