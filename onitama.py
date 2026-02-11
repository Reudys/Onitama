import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

SIZE = 5

@dataclass(frozen=True)
class Card:
    name: str
    moves: Tuple[Tuple[int, int], ...]

CARDS: List[Card] = [
    Card("Tiger",  ((-2, 0), (1, 0))),
    Card("Dragon", ((-1, -2), (-1, 2), (1, -1), (1, 1))),
    Card("Frog",   ((0, -2), (-1, -1), (1, 1))),
    Card("Rabbit", ((0, 2), (-1, 1), (1, -1))),
    Card("Crab",   ((0, -2), (-1, 0), (0, 2))),
    Card("Elephant", ((-1, -1), (-1, 1), (0, -1), (0, 1))),
    Card("Goose",  ((-1, -1), (-1, 0), (0, 0), (0, 1))),
    Card("Rooster",((-1, 0), (-1, 1), (0, -1), (0, 1))),
    Card("Monkey", ((-1, -1), (-1, 1), (1, -1), (1, 1))),
    Card("Mantis", ((-1, -1), (-1, 1), (1, 0))),
    Card("Horse",  ((-1, 0), (0, -1), (1, 0))),
    Card("Ox",     ((-1, 0), (0, 1), (1, 0))),
    Card("Crane",  ((-1, 0), (1, -1), (1, 1))),
    Card("Boar",   ((-1, 0), (0, -1), (0, 1))),
    Card("Eel",    ((-1, -1), (1, -1), (0, 1))),
    Card("Cobra",  ((-1, 1), (1, 1), (0, -1))),
]

def normalized_cards() -> List[Card]:
    fixed = []
    for c in CARDS:
        if c.name == "Goose":
            fixed.append(Card("Goose", ((-1, -1), (0, -1), (0, 1), (1, 1))))
        elif c.name == "Rooster":
            fixed.append(Card("Rooster", ((-1, 1), (0, -1), (0, 1), (1, -1))))
        else:
            fixed.append(c)
    return fixed

CARDS_N = normalized_cards()

def inside(r: int, c: int) -> bool:
    return 0 <= r < SIZE and 0 <= c < SIZE

def coord_to_rc(s: str) -> Optional[Tuple[int, int]]:
    s = s.strip().lower()
    if len(s) != 2:
        return None
    file_ch, rank_ch = s[0], s[1]
    if file_ch < 'a' or file_ch > 'e':
        return None
    if rank_ch < '1' or rank_ch > '5':
        return None
    col = ord(file_ch) - ord('a')
    rank = int(rank_ch)
    row = SIZE - rank
    return row, col

def rc_to_coord(r: int, c: int) -> str:
    file_ch = chr(ord('a') + c)
    rank = SIZE - r
    return f"{file_ch}{rank}"

def opponent(player: str) -> str:
    return "R" if player == "B" else "B"

def is_master(piece: str) -> bool:
    return piece.endswith("M")

class OnitamaGame:
    def __init__(self):
        self.board: List[List[str]] = [["." for _ in range(SIZE)] for _ in range(SIZE)]
        self.hands: Dict[str, List[Card]] = {"B": [], "R": []}
        self.side_card: Card = None
        self.turn: str = "B"
        self.temple: Dict[str, Tuple[int, int]] = {}

        self._setup_board()
        self._setup_cards()

    def _setup_board(self):
        self.board[0] = ["R", "R", "RM", "R", "R"]
        self.board[4] = ["B", "B", "BM", "B", "B"]
        self.temple["R"] = (0, 2)
        self.temple["B"] = (4, 2)

    def _setup_cards(self):
        five = random.sample(CARDS_N, 5)
        self.hands["B"] = [five[0], five[1]]
        self.hands["R"] = [five[2], five[3]]
        self.side_card = five[4]
        self.turn = random.choice(["B", "R"])

    def print_state(self):
        print("\n" + "=" * 45)
        print(f"Turno: {'Azul (B)' if self.turn=='B' else 'Rojo (R)'}")
        print("Cartas:")
        print(f"  B: 1) {self.hands['B'][0].name}   2) {self.hands['B'][1].name}")
        print(f"  R: 1) {self.hands['R'][0].name}   2) {self.hands['R'][1].name}")
        print(f"  Mesa (side): {self.side_card.name}")
        print("\nTablero:")
        print("    a  b  c  d  e")
        for r in range(SIZE):
            rank = SIZE - r
            row_str = " ".join(self.board[r][c].rjust(2) for c in range(SIZE))
            print(f" {rank}  {row_str}")
        print("=" * 45)

    def piece_at(self, r: int, c: int) -> str:
        return self.board[r][c]

    def set_piece(self, r: int, c: int, val: str):
        self.board[r][c] = val

    def card_moves_for_player(self, card: Card, player: str) -> List[Tuple[int, int]]:
        if player == "B":
            return list(card.moves)
        return [(-dr, dc) for (dr, dc) in card.moves]

    def all_legal_moves(self, player: str) -> List[Tuple[Tuple[int,int], Tuple[int,int], int]]:
        legal = []
        for idx, card in enumerate(self.hands[player]):
            moves = self.card_moves_for_player(card, player)
            for r in range(SIZE):
                for c in range(SIZE):
                    p = self.piece_at(r, c)
                    if p == ".":
                        continue
                    if player == "B" and not p.startswith("B"):
                        continue
                    if player == "R" and not p.startswith("R"):
                        continue
                    for dr, dc in moves:
                        nr, nc = r + dr, c + dc
                        if not inside(nr, nc):
                            continue
                        dest = self.piece_at(nr, nc)
                        if dest != ".":
                            if player == "B" and dest.startswith("B"):
                                continue
                            if player == "R" and dest.startswith("R"):
                                continue
                        legal.append(((r, c), (nr, nc), idx))
        return legal

    def check_winner(self) -> Optional[str]:
        found_BM = False
        found_RM = False
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] == "BM":
                    found_BM = True
                elif self.board[r][c] == "RM":
                    found_RM = True
        if not found_BM:
            return "R"
        if not found_RM:
            return "B"
        if self.board[self.temple["R"][0]][self.temple["R"][1]] == "BM":
            return "B"
        if self.board[self.temple["B"][0]][self.temple["B"][1]] == "RM":
            return "R"
        return None

    def rotate_cards(self, used_hand_index: int):
        player = self.turn
        used = self.hands[player][used_hand_index]
        self.hands[player][used_hand_index] = self.side_card
        self.side_card = used

    def make_move(self, frm: Tuple[int,int], to: Tuple[int,int], card_index: int) -> bool:
        r, c = frm
        nr, nc = to
        player = self.turn
        card = self.hands[player][card_index]
        piece = self.piece_at(r, c)

        if piece == ".":
            return False
        if player == "B" and not piece.startswith("B"):
            return False
        if player == "R" and not piece.startswith("R"):
            return False

        allowed = self.card_moves_for_player(card, player)
        dr, dc = nr - r, nc - c
        if (dr, dc) not in allowed:
            return False
        if not inside(nr, nc):
            return False

        dest = self.piece_at(nr, nc)
        if dest != ".":
            if player == "B" and dest.startswith("B"):
                return False
            if player == "R" and dest.startswith("R"):
                return False

        self.set_piece(nr, nc, piece)
        self.set_piece(r, c, ".")
        self.rotate_cards(card_index)
        self.turn = opponent(self.turn)
        return True

    def pass_turn(self, card_index: int) -> bool:
        if self.all_legal_moves(self.turn):
            return False
        self.rotate_cards(card_index)
        self.turn = opponent(self.turn)
        return True

def choose_int(prompt: str, valid: List[int]) -> int:
    while True:
        s = input(prompt).strip()
        if s.isdigit():
            x = int(s)
            if x in valid:
                return x
        print(f"Entrada inválida. Opciones: {valid}")

def main():
    print("ONITAMA (Consola) - 2 jugadores")
    game = OnitamaGame()

    while True:
        winner = game.check_winner()
        if winner:
            game.print_state()
            print("\n🏆 GANADOR:", "Azul (B)" if winner == "B" else "Rojo (R)")
            break

        game.print_state()
        player = game.turn
        legal = game.all_legal_moves(player)

        print("\nElige carta: 1 o 2")
        ci = choose_int("> ", [1, 2]) - 1

        if not legal:
            game.pass_turn(ci)
            continue

        legal_for_card = [m for m in legal if m[2] == ci]
        if not legal_for_card:
            continue

        for i, (frm, to, _) in enumerate(legal_for_card, start=1):
            print(f"{i}) {rc_to_coord(*frm)} -> {rc_to_coord(*to)}")

        mi = choose_int("> ", list(range(1, len(legal_for_card) + 1))) - 1
        frm, to, _ = legal_for_card[mi]
        game.make_move(frm, to, ci)

if __name__ == "__main__":
    main()
