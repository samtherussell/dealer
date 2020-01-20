def format_cards(cards):
    # return " ".join(["{:02d}".format(card.code) for card in cards])
    return ", ".join([card.name for card in cards])

class Communicator():
 
    def __init__(self, conn):
        self.conn = conn
 
    def send(self, d):
        return self.conn.send(d.encode("utf8"))
 
    def send_line(self, d):
        return self.send(d + "\n")
 
    def send_hand(self, hand):
        self.send_line("Hand\n" + format_cards(hand))
 
    def send_card_reveal(self, reveals):
        self.send_line("Reveal {}\n{}".format(len(reveals), format_cards(reveals)))
 
    def recv(self, d):
        return self.conn.recv(d).decode("utf8").strip()

    def close(self):
        self.send_line("Goodbye")
        self.conn.close()
