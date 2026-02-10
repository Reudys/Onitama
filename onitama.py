import copy
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Representamos el tablero 5×5
EMPTY = '.'

# Piezas (alumnos y maestros)
B = 'B'    # alumno azul
BM = 'BM'  # maestro azul
R = 'R'    # alumno rojo
RM = 'RM'  # maestro rojo

# Identificadores de jugador (turnos)
BLUE = 'BLUE'
RED = 'RED'

# Cartas básicas de Onitama (movimientos relativos desde perspectiva Azul)
CARDS = {
    "Tigre": [(-2, 0), (1, 0)],
    "Dragón": [(-1, -1), (-1, 1), (1, -2), (1, 2)],
    "Frog": [(-1, -1), (0, -2), (1, 1)],
    "Liebre": [(-1, 1), (0, 2), (1, -1)],
    "Crane": [(-1, 0), (1, -1), (1, 1)],
    "Mono": [(-1, -1), (-1, 1), (1, -1), (1, 1)],
    "Mantis": [(-1, -1), (-1, 1), (1, 0)],
    "Cabra": [(0, -1), (0, 1), (-2, 0), (2, 0)],
}

@dataclass
class Move:
    card_name: str
    from_pos: Tuple[int, int]
    to_pos: Tuple[int, int]

def is_blue_piece(p: str) -> bool:
    return p in (B, BM)

def is_red_piece(p: str) -> bool:
    return p in (R, RM)

class Onitama:
    def __init__(self):
        # Tablero inicial: 4 alumnos + maestro en el centro
        self.board = [
            [B, B, BM, B, B],
            [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
            [R, R, RM, R, R]
        ]

        # Cartas iniciales (puedes cambiarlas si quieres)
        self.cards = {
            "player_blue": ["Tigre", "Crane"],
            "player_red":  ["Frog", "Liebre"],
            "center": "Mantis"
        }

        self.current_player = BLUE  # Azul empieza

    def print_board(self):
        # Alineado para que BM/RM no descuadren
        print("\n  0   1   2   3   4")
        for i, row in enumerate(self.board):
            print(f"{i} " + "  ".join(f"{cell:2}" for cell in row))
        print()

    def print_cards(self):
        print(f"Cartas de Azul: {self.cards['player_blue']}")
        print(f"Carta central:  {self.cards['center']}")
        print(f"Cartas de Rojo: {self.cards['player_red']}")
        print()

    def get_possible_moves(self, player: str) -> List[Move]:
        moves: List[Move] = []
        player_key = "player_blue" if player == BLUE else "player_red"
        card_names = self.cards[player_key]

        for r in range(5):
            for c in range(5):
                piece = self.board[r][c]
                if piece == EMPTY:
                    continue

                # Filtrar piezas del jugador actual
                if player == BLUE and not is_blue_piece(piece):
                    continue
                if player == RED and not is_red_piece(piece):
                    continue

                for card_name in card_names:
                    deltas = CARDS[card_name]
                    for dr, dc in deltas:
                        # Invertimos dirección para el jugador Rojo (rotación 180°)
                        if player == RED:
                            dr, dc = -dr, -dc

                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 5 and 0 <= nc < 5:
                            target = self.board[nr][nc]

                            # No puedes capturar tu propia pieza
                            if player == BLUE and is_blue_piece(target):
                                continue
                            if player == RED and is_red_piece(target):
                                continue

                            moves.append(Move(card_name, (r, c), (nr, nc)))
        return moves

    def make_move(self, move: Move):
        r1, c1 = move.from_pos
        r2, c2 = move.to_pos

        # Mover la pieza (captura si hay rival en destino)
        piece = self.board[r1][c1]
        self.board[r1][c1] = EMPTY
        self.board[r2][c2] = piece

        # Rotación correcta de cartas:
        # - La carta usada va al centro
        # - La carta del centro pasa a la mano del mismo jugador que jugó
        player_key = "player_blue" if self.current_player == BLUE else "player_red"
        hand = self.cards[player_key]

        hand.remove(move.card_name)
        old_center = self.cards["center"]
        self.cards["center"] = move.card_name
        hand.append(old_center)

        # Cambiar turno
        self.current_player = RED if self.current_player == BLUE else BLUE

    def is_game_over(self) -> Optional[str]:
        # Victoria 1: capturar el maestro enemigo
        blue_master_alive = any(BM in row for row in self.board)
        red_master_alive  = any(RM in row for row in self.board)

        if not blue_master_alive:
            return RED
        if not red_master_alive:
            return BLUE

        # Victoria 2: maestro en el templo enemigo
        if self.board[4][2] == BM:
            return BLUE
        if self.board[0][2] == RM:
            return RED

        return None

    def play_two_players(self):
        print("=== ONITAMA - DOS JUGADORES (CONSOLA) ===")
        print("Azul (BLUE) empieza. Ambos jugadores eligen sus movimientos.\n")
        print("Escribe el número del movimiento que quieres hacer.")
        print("Escribe 0 para terminar la partida en cualquier momento.\n")

        turn = 1
        while True:
            winner = self.is_game_over()
            if winner:
                print(f"\n¡GANÓ {winner}!")
                self.print_board()
                break

            self.print_board()
            self.print_cards()

            player_name = "Azul" if self.current_player == BLUE else "Rojo"
            print(f"Turno {turn} - {player_name}")

            moves = self.get_possible_moves(self.current_player)
            if not moves:
                print(f"{player_name} no tiene movimientos posibles. ¡Juego terminado!")
                break

            print(f"Movimientos disponibles ({len(moves)}):")
            for i, m in enumerate(moves, 1):
                piece = self.board[m.from_pos[0]][m.from_pos[1]]
                print(f"{i:2d}. {m.card_name:8}  {m.from_pos} → {m.to_pos}   ({piece})")

            while True:
                try:
                    choice = input("\nElige movimiento (número) o 0 para salir: ").strip()
                    if choice == "0":
                        print("\nPartida terminada por los jugadores.")
                        return
                    choice = int(choice)
                    if 1 <= choice <= len(moves):
                        selected = moves[choice - 1]
                        print(f"→ Movimiento: {selected.card_name} {selected.from_pos} → {selected.to_pos}")
                        self.make_move(selected)
                        break
                    else:
                        print("Número fuera de rango, intenta otra vez.")
                except ValueError:
                    print("Por favor ingresa un número válido.")

            turn += 1
            print("-" * 40)

# -----------------------
if __name__ == "__main__":
    game = Onitama()
    game.play_two_players()
