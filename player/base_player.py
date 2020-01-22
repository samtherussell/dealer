import socket

from abc import ABC, abstractmethod


def get_local_ip() -> str:
    address_list = socket.gethostbyname_ex(socket.gethostname())[2]
    ip_addresses = [a for a in address_list if a.startswith("192.168.1.")]
    if len(ip_addresses) < 1:
        raise Exception("Could not find an address that looks like a local ip")
    return ip_addresses[0]


class PokerPlayerCommunicator:

    def __init__(self):
        self._socket = None
        self._lines_buffer = []
        self._line_buffer = ""

    def connect(self, ip_address=None, port=8080):
        if ip_address is None:
            ip_address = get_local_ip()
        self._socket = socket.socket()
        self._socket.connect((ip_address, port))

    def read(self):
        if self._socket is None:
            raise Exception("Need to connect before calling read")
        return self._socket.recv(100).decode("utf8")

    def send(self, string: str) -> None:
        if self._socket is None:
            raise Exception("Need to connect before calling send")
        print("SENDING: " + string, end="")
        self._socket.send(string.encode("utf8"))

    def read_line(self) -> str:
        if len(self._lines_buffer) == 0:
            lines = self.read()
            lines = lines.split("\n")
            if len(lines) > 1:
                self._lines_buffer.append(self._line_buffer + lines[0])
                self._line_buffer = ""

                for line in lines[1:-1]:
                    self._lines_buffer.append(line)

            self._line_buffer = lines[-1]

        return self._lines_buffer.pop(0)

    def send_line(self, string: str) -> None:
        self.send(string + "\n")


class GameStatus:

    def __init__(self):
        self.internal = dict()
        self.previous_actions = []


class PokerPlayer(ABC):
    _player_num = 1

    def __init__(self, player_name=None):
        if player_name is None:
            self.player_name = "player " + str(PokerPlayer._player_num)
            PokerPlayer._player_num += 1
        else:
            self.player_name = player_name
        self.coms = PokerPlayerCommunicator()
        self.coms.connect()
        self.game_status = GameStatus()

    def play(self):
        self.coms.read()  # what is your name
        self.coms.send_line(self.player_name)
        self.coms.read()  # welcome
        while True:
            response = self.coms.read_line()
            print(response)
            if response == "Goodbye": # Game over
                break
            elif response.startswith("Fold/Call"):
                action = self.decide_action(self.game_status, raise_available="Raise" in response)
                self.game_status.previous_actions.append(action)
                if type(action) is tuple:
                    action = " ".join((str(i) for i in action))
                elif not type(action) is str:
                    action = str(action)
                self.coms.send_line(action)
            else:
                pass

    @abstractmethod
    def decide_action(self, game_status, raise_available=True):
        pass
