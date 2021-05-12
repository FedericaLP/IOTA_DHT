import argparse
import curses
import os
import shutil
import sys
from random import randint

from client import Client
from demo.scrolling_window import Scrolling_window
from src.config import SUPERSET_THRESHOLD
from src.utils import NODES

TEST_FILES = './test_files/'

menu_list = ["- INSERT", "- GET", "- REMOVE", "- PIN SEARCH", "- SUPERSET SEARCH"]

TITLE = ['WELCOME TO HYPFS', 'INSERT', 'GET', 'REMOVE', 'PIN SEARCH', 'SUPERSET SEARCH']
TITLE_X = 2
TITLE_Y = 1

R = [3, 6, 10]
C = [2, 2, 2]


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('ipfs_addr', type=str, help='Port number to which connect the node')
    parser.add_argument('server_port', type=int, help='Port number to which connect the node')
    return parser.parse_args(argv)


def input_string(stdscr, r, c, prompt_string):
    curses.echo()
    stdscr.addstr(r, c, prompt_string)
    stdscr.clrtoeol()
    stdscr.refresh()
    string = stdscr.getstr(r, c + len(prompt_string), 999)
    if b'\x03' in string:
        return False
    else:
        return string.decode('utf-8')


def operation(option, client):
    screen.addstr(TITLE_Y, TITLE_X, TITLE[option], highlightText)
    func = OPERATIONS.get(option)
    return func(client)


def input_int(screen, row, col, prompt_string):
    try:
        input_str = input_string(screen, row, col, prompt_string)
        if input_str == '':
            return SUPERSET_THRESHOLD
        if not input_str:
            return False
        else:
            return int(input_str)
    except Exception:
        return False


def to_menu():
    while screen.getch() != ord("\n"):
        continue
    return


def insert(client):
    path = input_string(screen, R[0], C[0], 'Object path: ')
    if not path:
        return
    if path == 'random':
        path = TEST_FILES + str(randint(0, 100))
        with open(path, 'wb') as random_file:
            random_file.write(os.urandom(512))

    is_test = False
    if path == 'test':
        paths = []
        for k in range(0, 15):
            path = TEST_FILES + str(randint(0, 100))
            paths.append(path)
            with open(path, 'wb') as random_file:
                random_file.write(os.urandom(512))
        is_test = True

    while not os.path.isfile(path):
        screen.addstr(R[0]+1, C[0], 'Error: path not valid, retry', curses.color_pair(2))
        path = input_string(screen, R[0], C[0], 'Object path: ')
        if not path:
            return
        if path == 'random':
            path = TEST_FILES + str(randint(0, 100))
            with open(path, 'wb') as random_file:
                random_file.write(os.urandom(512))

        is_test = False
        if path == 'test':
            paths = []
            for k in range(0, 15):
                path = TEST_FILES + str(randint(0, 100))
                paths.append(path)
                with open(path, 'wb') as random_file:
                    random_file.write(os.urandom(512))
            is_test = True

    screen.clrtoeol()
    screen.border(0)
    screen.addstr(R[0]+1, C[0], 'Valid path', curses.color_pair(3))

    if is_test:
        for p in paths:
            client.add_obj(p, randint(1, NODES-1))
        screen.addstr(R[-1], C[-1], '{} RANDOM FILES ADDED'.format(len(paths)))
        return to_menu()

    keyword = input_int(screen, R[1], C[1], 'Object keyword in range (0,{}): '.format(NODES-1))
    print("da console", keyword)
    if not keyword and keyword != 0:
        return
    while not 0 <= keyword < NODES:
        screen.addstr(R[1]+1, C[1], 'Error: Keyword entered not valid', curses.color_pair(2))
        keyword = input_int(screen, R[1], C[1], 'Object keyword in range (0,{}): '.format(NODES-1))
        if not keyword and keyword != 0:
            return

    screen.clrtoeol()
    screen.border(0)
    screen.addstr(R[1]+1, C[1], 'Valid Keyword', curses.color_pair(3))

    res = client.add_obj(path, keyword) 
   
    screen.addstr(R[-1], C[-1], res)

    return to_menu()


def remove(client):
    obj_hash = input_string(screen, R[0], C[0], 'Object hash: ')
    if not obj_hash:
        return
    while len(obj_hash) != 46:
        screen.addstr(R[0]+1, C[0], 'Error: hash not valid', curses.color_pair(2))
        obj_hash = input_string(screen, R[0], C[0], 'Object hash: ')
        if not obj_hash:
            return
    screen.clrtoeol()
    screen.border(0)
    screen.addstr(R[0]+1, C[0], 'Valid hash', curses.color_pair(3))

    keyword = input_int(screen, R[1], C[1], 'Object keyword in range (0,{}): '.format(NODES-1))
    if not keyword and keyword != 0:
        return

    while not 0 <= keyword < NODES:
        screen.addstr(R[1]+1, C[1], 'Error: Keyword entered not valid', curses.color_pair(2))
        keyword = input_int(screen, R[1], C[1], 'Object keyword in range (0,{}): '.format(NODES-1))
        if not keyword and keyword != 0:
            return
    screen.clrtoeol()
    screen.border(0)
    screen.addstr(R[1]+1, C[1], 'Valid Keyword', curses.color_pair(3))

    res = client.remove_obj(obj_hash, keyword)
    screen.addstr(R[-1], C[-1], res)

    return to_menu()


def get(client):
    obj_hash = input_string(screen, R[0], C[0], 'Object hash: ')
    if not obj_hash:
        return
    while len(obj_hash) != 46:
        screen.addstr(R[0]+1, C[0], 'Error: hash not valid', curses.color_pair(2))
        obj_hash = input_string(screen, R[0], C[0], 'Object hash: ')
        if not obj_hash:
            return

    screen.clrtoeol()
    screen.border(0)
    screen.addstr(R[0]+1, C[0], 'Valid hash', curses.color_pair(3))

    res = client.get_obj(obj_hash)
    screen.addstr(R[-1], C[-1], res)

    return to_menu()


def pin_search(client):
    keyword = input_int(screen, R[0], C[0], 'Object keyword in range (0,{}): '.format(NODES-1))
    if not keyword and keyword != 0:
        return

    while not 0 <= keyword < NODES:
        screen.addstr(R[0]+1, C[0], 'Error: Keyword entered not valid', curses.color_pair(2))
        keyword = input_int(screen, R[0], C[0], 'Object keyword in range (0,{}): '.format(NODES-1))
        if not keyword and keyword != 0:
            return
    screen.clrtoeol()
    screen.border(0)
    screen.addstr(R[0]+1, C[0], 'Valid Keyword', curses.color_pair(3))

    res = client.pin_search(keyword, -1)
    if len(res) >= 1:
        scrolling_window = Scrolling_window(res, 'PIN SEARCH')
        scrolling_window.run()
        screen.refresh()
        return
    else:
        screen.addstr(R[-1], C[-1], 'NO RESULTS FOUND')
        return to_menu()


def superset_search(client):
    keyword = input_int(screen, R[0], C[0], 'Object keyword in range (0,{}): '.format(NODES-1))
    if not keyword and keyword != 0:
        return
    while not 0 <= keyword < NODES:
        screen.addstr(R[0]+1, C[0], 'Error: Keyword entered not valid', curses.color_pair(2))
        keyword = input_int(screen, R[0], C[0], 'Object keyword in range (0,{}): '.format(NODES-1))
        if not keyword and keyword != 0:
            return
    screen.clrtoeol()
    screen.border(0)
    screen.addstr(R[0]+1, C[0], 'Valid Keyword', curses.color_pair(3))

    threshold = input_int(screen, R[1], C[1], 'Threshold (default: {}): '.format(SUPERSET_THRESHOLD))
    if not threshold:
        return
    while threshold < 1:
        screen.addstr(R[1]+1, C[1], 'Error: Threshold entered not valid', curses.color_pair(2))
        threshold = input_int(screen, R[1], C[1], 'Threshold (default: {}): '.format(SUPERSET_THRESHOLD))
        if not threshold:
            return

    screen.clrtoeol()
    screen.border(0)
    screen.addstr(R[1]+1, C[1], 'Valid threshold', curses.color_pair(3))

    res = client.superset_search(keyword, threshold)
    if len(res) >= 1:
        scrolling_window = Scrolling_window(res, 'SUPERSET SEARCH')
        scrolling_window.run()
        screen.refresh()
        return
    else:
        screen.addstr(R[-1], C[-1], 'NO RESULTS FOUND')
        return to_menu()


OPERATIONS = {
    1: insert,
    2: get,
    3: remove,
    4: pin_search,
    5: superset_search
}


if __name__ == '__main__':
    args = parse_arguments(sys.argv[1:])
    IPFS_ADDR = args.ipfs_addr
    SERVER_PORT = args.server_port
    client = Client(IPFS_ADDR, SERVER_PORT)

    # clears the test directory
    if os.path.exists(TEST_FILES):
        shutil.rmtree(TEST_FILES)
    os.makedirs(TEST_FILES)


    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.start_color()
    screen.keypad(1)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    highlightText = curses.color_pair(1)
    normalText = curses.A_NORMAL
    screen.border(0)
    curses.curs_set(0)
    max_row = 5  # max number of rows
    box = curses.newwin(max_row + 2, 22, 2, 1)
    box.box()

    # main menu
    row_num = len(menu_list)

    position = 1
    while True:
        for i in range(1, max_row + 1):
            if row_num == 0:
                box.addstr(1, 1, "There aren't strings", highlightText)
            else:
                if i == position:
                    box.addstr(i, 2, menu_list[i - 1], highlightText)
                else:
                    box.addstr(i, 2, menu_list[i - 1], normalText)
                if i == row_num:
                    break
        screen.border(0)
        screen.addstr(TITLE_Y, TITLE_X, TITLE[0], highlightText)
        screen.clrtoeol()

        screen.refresh()
        box.border(0)
        box.refresh()

        pressed_key = screen.getch()

        if pressed_key == 27:
            client.close()
            break
        if pressed_key == curses.KEY_DOWN and position < i:
            position = position + 1
        if pressed_key == curses.KEY_UP and position > 1:
            position = position - 1
        if pressed_key == ord("\n") and row_num != 0:
            screen.erase()
            screen.border(0)
            operation(position, client)
            screen.erase()
            screen.border(0)
            screen.addstr(max_row + 5, 2, "{} DONE".format(TITLE[position]), curses.color_pair(3))

    curses.endwin()
    exit()

 


