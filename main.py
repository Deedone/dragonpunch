#!/usr/bin/env python3
from defs import Board, slots, banner, Card
import copy
import pyautogui
import random
from scanner import prepare_samples, scan_board
from solver import Move, simulate_move, solve, get_moves
from time import sleep
from typing import Tuple

DELAY = 0.2
LIMIT = 30000

PITCH_Y = 31
DEBUG = False

def board_to_click(pos: Tuple[int, int]) -> Tuple[int, int]:
    x, y = slots.rows[pos[0]].click
    y += PITCH_Y * pos[1]
    return x, y

def special_to_click(pos: int) -> Tuple[int, int]:
    return slots.special[pos].click

def execute_move(move: Move) -> int:
    if move.DRAGONMOVE:
        sleep(DELAY)
        for d in slots.dragons:
            pyautogui.moveTo(d.click, duration=DELAY)
            sleep(DELAY)
            pyautogui.mouseDown()
            sleep(0.3)
            pyautogui.mouseUp()
        return 0

    if move.WINMOVE:
        print("Congratulations!")
        return 1

    startx, starty = 0, 0
    endx, endy = 0, 0

    if move.src:
        startx, starty = board_to_click(move.src)
    if move.special_src is not None:
        startx, starty = special_to_click(move.special_src)

    if move.dst:
        endx, endy = board_to_click(move.dst)

    if move.special_dst is not None:
        endx, endy = special_to_click(move.special_dst)


    pyautogui.moveTo(startx, starty, duration=DELAY)
    pyautogui.dragTo(endx, endy, duration=DELAY)
    sleep(move.wait * 0.2)
    return 0

def test_prediction(board, move):
    bcopy = copy.deepcopy(board)
    simulate_move(bcopy, move)
    board = Board.new()
    scan_board(board, slots)
    if bcopy.get_hash() != board.get_hash():
        print("Move failed")
        print("Expected")
        bcopy.show()
        print("Got")
        board.show()
        exit(1)

#Do random moves interactivly to test the prediction
def debug_mode():
    while 1:
        board = Board.new()
        scan_board(board, slots)
        board.show()

        moves = get_moves(board)
        for m in moves:
            print(m.show(board))

        move = random.choice(moves)
        print("Executing move")
        execute_move(move)
        test_prediction(board, move)

def start_new_game():
    pyautogui.moveTo(1488, 940, duration=DELAY)
    pyautogui.mouseDown()
    sleep(0.3)
    pyautogui.mouseUp()
    sleep(5)


def do_game():
    for _ in range(5):
        board = Board.new()
        scan_board(board, slots)
        board.show()
        solved = solve(board, LIMIT)
        if not solved:
            print("No solution found")
            return

        print("Soved with {} moves".format(len(solved.moves)))
        board.show()
        for m in solved.moves:
            if execute_move(m):
                return
if __name__ == "__main__":
    print(banner)
    prepare_samples()
    sleep(5)
    #while True:
        #start_new_game()
    do_game()
    #sleep(5)
