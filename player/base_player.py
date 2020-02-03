import socket
import random
import sys
from abc import ABC, abstractmethod
from typing import Dict, Tuple, List

from cards import Card, card_name_lookup


def get_local_ip() -> str:
    address_list = socket.gethostbyname_ex(socket.gethostname())[2]
    ip_addresses = [a for a in address_list if a.startswith("192.168.1.")]
    if len(ip_addresses) < 1:
        raise Exception("Could not find an address that looks like a local ip")
    return ip_addresses[0]


class PokerPlayerCommunicator:

    __slots__ = ["_socket", "_lines_buffer", "_line_buffer", "verbose"]

    def __init__(self, verbose=False):
        self._socket = None
        self._lines_buffer = []
        self._line_buffer = ""
        self.verbose = verbose

    def connect(self, ip_address=None, port=8080):
        if ip_address is None:
            ip_address = get_local_ip()
        self._socket = socket.socket()
        self._socket.connect((ip_address, port))
        if self.verbose:
            print("Connected to {}:{}".format(ip_address, port))

    def read(self):
        if self._socket is None:
            raise Exception("Need to connect before calling read")
        result = self._socket.recv(100).decode("utf8")
        if result == "":
            raise Exception("Connection is closed")
        if self.verbose:
            print("Received:", result, end="")
        return result

    def send(self, string: str) -> None:
        if self._socket is None:
            raise Exception("Need to connect before calling send")
        if self.verbose:
            print("Sending:", string, end="")
        self._socket.send(string.encode("utf8"))

    def read_line(self) -> str:
        while len(self._lines_buffer) == 0:
            lines = self.read()
            lines = lines.split("\n")
            if len(lines) > 1:
                self._lines_buffer.append(self._line_buffer + lines[0])
                self._line_buffer = ""

                for line in lines[1:-1]:
                    self._lines_buffer.append(line)

            self._line_buffer += lines[-1]

        return self._lines_buffer.pop(0)

    def send_line(self, string: str) -> None:
        self.send(string + "\n")


class Player:

    __slots__ = ["name", "holdings", "folded", "actions", "bet"]

    def __init__(self, name):
        self.name: str = name
        self.holdings: int = 0
        self.folded: bool = False
        self.actions: List[List[Tuple]] = [[]]
        self.bet: int = 0

    def __repr__(self):
        return f"Name: {self.name}, Bet: {self.bet}, Holdings: {self.holdings}, Folded: {self.folded}, " + \
               f"Actions: {self.actions}"


class GameStatus:

    __slots__ = ["internal", "you", "players", "hand", "community_cards", "pot_amount", "pot_bet", "your_bet"]

    def __init__(self, name):
        self.internal: Dict = dict()
        self.you: Player = Player(name)
        self.players: Dict[str, Player] = {}
        self.hand: List[Card] = []
        self.community_cards: List[Card] = []
        self.pot_amount: int = 0
        self.pot_bet: int = 0
        self.your_bet: int = 0

    def __repr__(self):
        return f"You: {self.you}, Others: {self.players}, " + \
            f"Hand: {self.hand}, Com Cards: {self.community_cards}, Pot amount: {self.pot_amount}, " + \
               f"Pot bet: {self.pot_bet}, Your bet: {self.your_bet}, Internal State: {self.internal}"


class PokerPlayer(ABC):

    def __init__(self, player_name=None):
        if player_name is None:
            with open("names.txt", "r") as f:
                names = f.readlines()
            self.player_name = names[random.randint(0, 4945)].strip()
        else:
            self.player_name = player_name
        self.coms = PokerPlayerCommunicator(verbose=True)
        self.coms.connect()
        self.game_status = GameStatus(self.player_name)

    def play(self):
        self.coms.read()  # what is your name
        self.coms.send_line(self.player_name)
        self.coms.read()  # welcome
        while True:
            line = self.coms.read_line()
            if line == "Goodbye":  # Game over
                print("--Game is over")
                break
            elif line.startswith("Fold/Call"):
                print("--Input the move")
                while True:
                    action = self.decide_action(self.game_status, raise_available="Raise" in line)
                    self.game_status.you.actions[-1].append(action)
                    if type(action) is tuple:
                        action = " ".join((str(i) for i in action))
                    elif not type(action) is str:
                        action = str(action)
                    self.coms.send_line(action)
                    response = self.coms.read_line()
                    if response.startswith("ERROR"):
                        print(response, file=sys.stderr)
                        self.coms.read_line()  # New prompt
                    else:
                        break
            elif line == "----New Hand----":
                print("--Resetting hand state")
                if len(self.game_status.you.actions[-1]) > 0:
                    self.game_status.you.actions.append([])
                for player in self.game_status.players.values():
                    player.actions.append([])
                    player.folded = False
                    player.bet = 0
                self.game_status.hand = []
                self.game_status.community_cards = []
                self.game_status.pot_amount = 0
                self.game_status.pot_bet = 0
                self.game_status.your_bet = 0
            elif line.startswith("The following players are still in:"):
                print("--Getting which players are still in")
                names = line.split(":", maxsplit=1)[1].strip()
                names = [name.strip() for name in names.split(",")]
                print("{} players still in".format(len(names)))
                if len(self.game_status.players) == 0:
                    self.game_status.players = {name: Player(name) for name in names if name != self.player_name}
                else:
                    self.game_status.players = {player.name: player for player in self.game_status.players.values()
                                                if player.name in names}

            elif line == "Money left":
                print("--Getting how much money everyone has")
                for _ in range(len(self.game_status.players) + 1):
                    line = self.coms.read_line()
                    line = line.split(":", maxsplit=1)
                    holdings = int(line[1].strip())
                    if line[0].startswith("You"):
                        self.game_status.you.holdings = holdings
                    else:
                        self.game_status.players[line[0]].holdings = holdings
            elif line == "Hand":
                print("--Getting my hand cards")
                cards = self.coms.read_line()
                card_names = (name.strip() for name in cards.split(","))
                self.game_status.hand = [card_name_lookup[name] for name in card_names]
            elif line.startswith("Reveal"):
                print("--Getting revealed cards")
                cards = self.coms.read_line()
                card_names = (name.strip() for name in cards.split(","))
                self.game_status.community_cards += [card_name_lookup[name] for name in card_names]
            elif line.startswith("Current pot:"):
                self.game_status.pot_amount = int(line.split(":")[1].strip())
            elif line.startswith("Current pot bet:"):
                self.game_status.pot_bet = int(line.split(":")[1].strip())
            elif line.startswith("Your current bet:"):
                self.game_status.your_bet = int(line.split(":")[1].strip())
            elif line.startswith("Your holdings:"):
                self.game_status.you.holdings = int(line.split(":")[1].strip())
            elif line.startswith("Opponent action"):
                print("--Getting opponent action")
                player_name, action = (x.strip() for x in line.split(":")[1].strip().split(" ", maxsplit=1))
                player: Player = self.game_status.players[player_name]
                if action == "Folded":
                    player.folded = True
                    action = "Fold"
                elif action == "Called":
                    action = "Call"
                    diff = self.game_status.pot_bet - player.bet
                    player.holdings -= diff
                    player.bet = self.game_status.pot_bet
                else:  # Raise
                    raise_amount = int(action.split(" ")[2])
                    action = "Raise", raise_amount
                    diff = self.game_status.pot_bet - player.bet + raise_amount
                    player.holdings -= diff
                    player.bet = self.game_status.pot_bet + raise_amount
                player.actions[-1].append(action)
            elif line.startswith("Results"):
                print("--Getting results")
                num_results = int(line.split(" ")[1][1:-1])
                for _ in range(num_results):
                    self.coms.read_line()
            elif line.startswith("Pots"):
                print("--Getting pot winners")
                num_pots = int(line.split(" ")[1][1:-1])
                for _ in range(num_pots):
                    self.coms.read_line()
            elif line == "Winnings":
                print("--Getting winnings")
                for _ in range(len(self.game_status.players) + 1):
                    self.coms.read_line()
            elif "blind" in line or "You have folded so cannot bet" in line or "You have no more money so cannot bet":
                pass
            else:
                raise Exception("line not handled:", line)

    @abstractmethod
    def decide_action(self, game_status, raise_available=True):
        pass
