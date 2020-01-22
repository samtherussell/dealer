from typing import List
from card import Card


def format_cards(cards: List[Card]) -> str:
    # return " ".join(["{:02d}".format(card.py.code) for card.py in cards])
    return ", ".join([card.name for card in cards])


class Communicator:
 
    def __init__(self, conn):
        self.conn = conn
 
    def send(self, d: str):
        self.conn.send(d.encode("utf8"))
 
    def send_line(self, d: str):
        self.send(d + "\n")
 
    def send_hand(self, hand: List[Card]):
        self.send_line("Hand\n" + format_cards(hand))
 
    def send_card_reveal(self, reveals: List[Card]):
        self.send_line("Reveal {}\n{}".format(len(reveals), format_cards(reveals)))
 
    def recv(self, d: int) -> str:
        return self.conn.recv(d).decode("utf8").strip()

    def close(self):
        self.send_line("Goodbye")
        self.conn.close()
