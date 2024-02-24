from defs import Card, Board, Color, Face, NUMERIC
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
import copy

DEBUG = False
@dataclass
class Move:
    DRAGONMOVE: int
    WINMOVE: int
    special_dst: Optional[int]
    special_src: Optional[int]
    src: Optional[Tuple[int, int]]
    dst: Optional[Tuple[int, int]]
    wait: int = 0

    @classmethod
    def board_move(cls, src: Tuple[int, int], dst: Tuple[int, int]):
        return cls(0, 0, None, None, src, dst)

    @classmethod
    def from_special(cls, src: int, dst: Tuple[int, int]):
        return cls(0, 0,  None, src, None, dst)

    @classmethod
    def to_special(cls, src: Tuple[int, int], dst: int):
        return cls(0, 0, dst, None, src, None)

    @classmethod
    def dragon_move(cls):
        return cls(1, 0,  None, None, None, None)

    @classmethod
    def win_move(cls):
        return cls(0, 1,  None, None, None, None)

    def show(self, board: Board) -> str:
        if self.DRAGONMOVE:
            return "DRAGON MOVE"
        scr_card = None
        dst_card = None
        show_src = None
        show_dst = None
        if self.src:
            scr_card = board.rows[self.src[0]][self.src[1]]
            show_src = self.src
        if self.dst:
            if self.dst[1] == 0:
                dst_card = "Empty"
            else:
                dst_card = board.rows[self.dst[0]][self.dst[1] - 1]
            show_dst = self.dst
        if self.special_src is not None:
            scr_card = board.special[self.special_src]
            show_src = self.special_src
        if self.special_dst is not None:
            dst_card = board.special[self.special_dst]
            show_dst = self.special_dst
        return f"Move {scr_card} from {show_src} to {dst_card} at {show_dst}"


def get_move_targets(board: Board) -> List[Tuple[int, int]]:
    targets = []

    for i, row in enumerate(board.rows):
        last = len(row)
        targets.append((i, last))
    return targets

def can_place_onto(src: Card, dst: Card) -> bool:
    if dst.face == Face.DRAGON or dst.face == Face.ROSE:
        return False
    if src.face == Face.DRAGON or src.face == Face.ROSE:
        return False
    if src.color != dst.color and int(src.face.value) == int(dst.face.value) - 1:
        return True

    return False

def can_move_row(board: Board, row: int, pos: int) -> bool:
    nextpos = pos + 1
    #Last card
    if nextpos >= len(board.rows[row]):
        return True
    cur: Card = board.rows[row][pos]
    nxt: Card = board.rows[row][nextpos]

    if can_place_onto(nxt, cur):
        if can_move_row(board, row, nextpos):
            return True

    return False

#This assumes that the whole row can be moved
def is_legal_move(board: Board, src: Tuple[int, int], dst: Tuple[int, int]) -> bool:
    if src[0] == dst[0]:
        return False
    #Can move everyting to empty
    if dst[1] == 0:
        return True

    if DEBUG:
        if not can_move_row(board, src[0], src[1]):
            print("Cant move row, this shouldnt happen")
            print("Src: ", src)
            print("Dst: ", dst)
            return False

    cur = board.rows[src[0]][src[1]]
    prev = board.rows[dst[0]][dst[1]-1]

    return can_place_onto(cur, prev)

def get_board_moves(board: Board) -> List[Move]:
    moves = []
    targets = get_move_targets(board)

    for i, row in enumerate(board.rows):
        row_valid = False
        for j, _ in enumerate(row):
            if can_move_row(board, i, j) or row_valid:
                row_valid = True
                for target in targets:
                    if is_legal_move(board, (i, j), target):
                        moves.append(Move.board_move((i, j), target))

    return moves

def get_special_moves(board: Board) -> List[Move]:
    targets = get_move_targets(board)
    moves = []

    #Special to board
    for i, c in enumerate(board.special):
        if c.face == Face.EMPTY or c.face == Face.TAKEN:
            continue
        for t in targets:
            if t[1] == 0:
                moves.append(Move.from_special(i, t))
            else:
                prev = board.rows[t[0]][t[1]-1]
                if can_place_onto(c, prev):
                    moves.append(Move.from_special(i, t))

    #Board to special
    for i, row in enumerate(board.rows):
        if len(row) == 0:
            continue
        for j, c in enumerate(board.special):
            if c and c.face == Face.EMPTY:
                moves.append(Move.to_special((i, len(row)-1), j))

    return moves

def calc_mins(board: Board) -> Dict[Color, int]:
    mins = {Color.RED: 10, Color.GREEN: 10, Color.BLACK: 10}
    for c in board.allcards():
        if c.face in NUMERIC:
            mins[c.color] = min(mins[c.color], int(c.face.value))
    return mins

def calc_dragons(board: Board) -> Dict[Color, int]:
    dragons = {Color.RED: 0, Color.GREEN: 0, Color.BLACK: 0}
    for c in board.special:
        if c.face == Face.DRAGON:
            dragons[c.color] += 1

    for i, row in enumerate(board.rows):
        if len(row) == 0:
            continue
        c = row[-1]
        if c.face == Face.DRAGON:
            dragons[c.color] += 1

    return dragons

def prune(board: Board) -> int:
    mins = calc_mins(board)
    totalmin = min(mins.values())
    if DEBUG:
        print("Pruning with mins: ", mins)
        print("Total min: ", totalmin)

    for i, c in enumerate(board.special):
        if c.face in NUMERIC:
            val = int(c.face.value)
            if val == mins[c.color] and val <= totalmin :
                board.special[i] = Card.from_str("EB")
                if DEBUG:
                    print("Pruned special {} ({})".format(i, c))
                return 1 + prune(board)

    for i, row in enumerate(board.rows):
        if len(row) == 0:
            continue
        c = row[-1]
        if c.face in NUMERIC:
            val = int(c.face.value)
            if val == mins[c.color] and val <= totalmin:
                row.pop()
                if DEBUG:
                    print("Pruned rows {} ({})".format(i, c))
                return 1 + prune(board)
        if c.face == Face.ROSE:
            row.pop()
            if DEBUG:
                print("Pruned rows {} ({})".format(i, c))
            return 1 + prune(board)

    return 1

def simulate_move(board: Board, move: Move) -> None:
    if move.DRAGONMOVE:
        #Not simulated cause i'm lazy
        #We just do it and rescan the board
        print("DRAGON MOVE!")
        return
    if move.special_src is not None and move.dst:
        card = board.special[move.special_src]
        if not card:
            print("ILLEGAL MOVE ", move.show(board))
            exit(1)
        board.rows[move.dst[0]].append(card)
        board.special[move.special_src] = Card.from_str("EB")

    elif move.src and move.special_dst is not None:
        card = board.rows[move.src[0]].pop(move.src[1])
        board.special[move.special_dst] = card

    elif not move.src or not move.dst:
        print("ILLEGAL MOVE ", move.show(board))
        exit(1)

    else:
        for c in board.rows[move.src[0]][move.src[1]:]:
            board.rows[move.dst[0]].append(c)

        board.rows[move.src[0]] = board.rows[move.src[0]][:move.src[1]]

    move.wait = prune(board)

def special_has_dragon(board: Board, color: Color) -> bool:
    for c in board.special:
        if c.color == color and c.face == Face.DRAGON:
            return True
    return False

def has_empty_special(board: Board) -> bool:
    for c in board.special:
        if c.face == Face.EMPTY:
            return True
    return False

def is_board_solved(board: Board) -> bool:
    for c in board.allcards():
        if c.face != Face.EMPTY and c.face != Face.TAKEN:
            return False
    return True

def get_moves(board: Board) -> List[Move]:
    moves = get_board_moves(board)
    moves += get_special_moves(board)

    dragons = calc_dragons(board)
    for c in dragons:
        if dragons[c] == 4 and (special_has_dragon(board, c) or has_empty_special(board)):
            moves.append(Move.dragon_move())

    return moves

        
@dataclass
class GameState:
    board: Board
    moves: List[Move]
    score: int = 0

def board_fastcopy(src:Board, dst:Board):
    for i,c in enumerate(src.special):
        dst.special[i].color = c.color
        dst.special[i].face = c.face
    
    for i in range(8):
        dst.rows[i].clear()
        for c in src.rows[i]:
            dst.rows[i].append(Card(c.color, c.face))

copyboard: Board = Board.new()
def test_move(board: Board, move: Move, boards: set[str]) -> bool:
    board_fastcopy(board, copyboard)
    simulate_move(copyboard, move)
    bh = copyboard.get_hash()
    return bh not in boards

def process_state(initstate: GameState, states: List[GameState], boards: set[str], skipped: List[int]) -> Optional[GameState]:
    moves = get_moves(initstate.board)

    for m in moves:
        if m.DRAGONMOVE:
            print("Dragon move")
            initstate.moves.append(m)
            return initstate
        #Test for repeated board before doing 
        #expensive deepcopy
        if not test_move(initstate.board, m, boards):
            skipped[0] += 1
            continue
        state = copy.deepcopy(initstate)
        simulate_move(state.board, m)
        if is_board_solved(state.board):
            state.moves.append(m)
            state.moves.append(Move.win_move())
            return state

        boards.add(state.board.get_hash())
        state.moves.append(m)
        state.score = calc_score(state.board)
        states.append(state)
    
    return None

def calc_score(board: Board) -> int:
    score = 0

    score += sum([len(r) for r in board.rows])
    longest_chain = 0
    for r in board.rows:
        chain = 0
        for i in range(len(r)-1):
            if can_place_onto(r[i], r[i+1]):
                chain += 1
            else:
                longest_chain = max(longest_chain, chain)
                chain = 0
        longest_chain = max(longest_chain, chain)
    score -= longest_chain

    for c in board.special:
        if c.face == Face.EMPTY:
            score -= 5
    dragons = calc_dragons(board)

    score -= max(dragons.values()) * 3

    return score


def solve(board: Board, limit: int) -> Optional[GameState]:
    print("Solving")
    initial = GameState(board, [])
    states = [initial]
    boards = set()
    boards.add(board.get_hash())
    processed = 0
    skipped = [0]

    while len(states) > 0 and processed < limit:
        state = states.pop(0)
        res = process_state(state, states, boards, skipped)
        if processed % 100 == 0:
            states.sort(key=lambda x: x.score)

        processed += 1
        if res:
            print("Solved")
            return res
        if processed % 1000 == 0:
            print("Processed {}, unique {}, left {}, skipped {}".format(processed, len(boards), len(states), skipped[0]))

    return None
