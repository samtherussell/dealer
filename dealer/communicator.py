from typing import List
from .cards import Card


def format_cards(cards: List[Card]) -> str:
    # return " ".join(["{:02d}".format(cards.py.code) for cards.py in cards])
    return ", ".join([card.name for card in cards])


class Communicator:
 
    def __init__(self, conn, verbose=True):
        self.conn = conn
        self.name = None
        self.verbose = verbose
 
    def send(self, d: str, verbose=True):
        if self.verbose and verbose:
            print("sending to {}: {}".format(self.name, d), end="")
        self.conn.send(d.encode("utf8"))
 
    def send_line(self, d: str, verbose=True):
        self.send(d + "\n", verbose=verbose)
 
    def send_hand(self, hand: List[Card]):
        self.send_line("Hand\n" + format_cards(hand))
 
    def send_card_reveal(self, reveals: List[Card]):
        self.send_line("Reveal {}\n{}".format(len(reveals), format_cards(reveals)))
 
    def recv(self, d: int, verbose=True) -> str:
        msg = self.conn.recv(d).decode("utf8").strip()
        if self.verbose and verbose:
            print("received from {}: {}".format(self.name, msg))
        return msg

    def close(self):
        self.send_line("Goodbye")
        self.conn.close()
