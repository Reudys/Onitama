import random
import copy
import time
import numpy as np

SIZE = 5

class Card():
  def __init__(self, name, moves):
    self.name = name
    self.moves = moves  

  def __str__(self):
    return self.name

  def __repr__(self):
    return str(self)

CARDS = [
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

def normalized_cards():
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

def inside(r, c):
  return 0 <= r < SIZE and 0 <= c < SIZE

def rc_to_coord(r, c):
  file_ch = chr(ord('a') + c)
  rank = SIZE - r
  return f"{file_ch}{rank}"

def opponent(player):
  return "R" if player == "B" else "B"


class Player():
  def __init__(self, name, type_="human"):
    self.name = name     
    self.type_ = type_    


class OnitamaGameSession():

  def __init__(self, player_types=None, hide_print=False, minimax_time=1):
    self.hide_print = hide_print
    self.minimax_time = minimax_time

    self.n_players = 2
    self.player_types = player_types if player_types is not None else ["human", "AI"]
    self.players = [Player("B", self.player_types[0]), Player("R", self.player_types[1])]

    self.board = [["." for _ in range(SIZE)] for _ in range(SIZE)]
    self.hands = {"B": [], "R": []}
    self.side_card = None
    self.temple = {"R": (0, 2), "B": (4, 2)}

    self.curr_turn = 0
    self.curr_player = self.players[self.curr_turn]
    self.winners = []

    self.last_move_msg = ""

    self._setup_board()
    self._setup_cards()

  def _setup_board(self):
    self.board[0] = ["R", "R", "RM", "R", "R"]
    self.board[4] = ["B", "B", "BM", "B", "B"]

  def _setup_cards(self):
    five = random.sample(CARDS_N, 5)
    self.hands["B"] = [five[0], five[1]]
    self.hands["R"] = [five[2], five[3]]
    self.side_card = five[4]
    self.curr_turn = random.choice([0, 1])
    self.curr_player = self.players[self.curr_turn]

  def print_state(self):
    if self.hide_print:
      return

    turn = self.curr_player.name
    print("\n" + "=" * 45)
    print(f"Turno: {'Azul (B)' if turn=='B' else 'Rojo (R)'}")
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

  def piece_at(self, r, c):
    return self.board[r][c]

  def set_piece(self, r, c, val):
    self.board[r][c] = val

  def option_to_text(self, option):
    frm, to, _ci = option
    piece = self.piece_at(*frm)
    dest = self.piece_at(*to)
    capture = f" captura {dest}" if dest != "." else ""
    return f"{rc_to_coord(*frm)} ({piece}) -> {rc_to_coord(*to)}{capture}"

  def card_moves_for_player(self, card, player):
    if player == "B":
      return list(card.moves)
    return [(-dr, dc) for (dr, dc) in card.moves]

  def all_legal_moves(self, player):
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

  def check_winner(self):
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

  def rotate_cards(self, player, used_hand_index):
    used = self.hands[player][used_hand_index]
    self.hands[player][used_hand_index] = self.side_card
    self.side_card = used
    return used

  def get_available_decisions(self):
    return self.all_legal_moves(self.curr_player.name)

  def play_turn(self, decision):
    player = self.curr_player.name
    frm, to, ci = decision
    r, c = frm
    nr, nc = to

    piece = self.piece_at(r, c)
    if piece == ".":
      return False
    if player == "B" and not piece.startswith("B"):
      return False
    if player == "R" and not piece.startswith("R"):
      return False

    card = self.hands[player][ci]
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
    used_card = self.rotate_cards(player, ci)

    received_card = self.hands[player][ci]  
    capture_msg = f" (capturaste {dest})" if dest != "." else ""
    self.last_move_msg = (
      f"Moviste {piece} de {rc_to_coord(r,c)} -> {rc_to_coord(nr,nc)}{capture_msg}. "
      f"Usaste {used_card.name}; ahora {used_card.name} está en la mesa y recibiste {received_card.name}."
    )

    w = self.check_winner()
    if w is not None and len(self.winners) == 0:
      self.winners = [Player(w), Player(opponent(w))]

    if len(self.winners) == 0:
      self.curr_turn = 0 if self.curr_turn == 1 else 1
      self.curr_player = self.players[self.curr_turn]

    return True

  def is_terminal(self):
    return len(self.winners) == self.n_players

  def get_winners_points(self):
    if not self.is_terminal():
      return {self.players[0].name: 0, self.players[1].name: 0}

    winner_name = self.winners[0].name
    loser_name = self.winners[1].name
    return {winner_name: 1000, loser_name: 0}

  def children(self):
    options = self.get_available_decisions()
    children = []
    for option in options:
      child = copy.deepcopy(self)
      child.play_turn(option)
      children.append((option, child))
    return children

  def heuristic(self, player_name):
    opp = opponent(player_name)

    def count_pieces(color):
      cnt = 0
      for r in range(SIZE):
        for c in range(SIZE):
          p = self.board[r][c]
          if p != "." and p.startswith(color):
            cnt += 1
      return cnt

    my_p = count_pieces(player_name)
    opp_p = count_pieces(opp)
    return (my_p - opp_p) * 10

class MinimaxSolver():

  def __init__(self, player_name):
    self.player_name = player_name
    self.time_start = None
    self.max_time = None

  def __maximize(self, state, alpha, beta, depth):

    if time.time() - self.time_start >= self.max_time:
      raise StopIteration("Out of time!")

    if state.is_terminal():
      return None, state.get_winners_points()[self.player_name]

    if depth <= 0:
      return None, state.heuristic(self.player_name)

    max_child, max_utility = None, -np.inf

    for option, child in state.children():

      if child.curr_player.name == self.player_name:
        _, utility = self.__maximize(child, alpha, beta, depth-1)
      else:
        _, utility = self.__minimize(child, alpha, beta, depth-1)

      if utility > max_utility:
        max_child, max_utility = option, utility

      if max_utility >= beta:
        break

      alpha = max(alpha, max_utility)

    return max_child, max_utility

  def __minimize(self, state, alpha, beta, depth):

    if time.time() - self.time_start >= self.max_time:
      raise StopIteration("Out of time!")

    if state.is_terminal():
      return None, state.get_winners_points()[self.player_name]

    if depth <= 0:
      return None, state.heuristic(self.player_name)

    min_child, min_utility = None, np.inf

    for option, child in state.children():

      if child.curr_player.name == self.player_name:
        _, utility = self.__maximize(child, alpha, beta, depth-1)
      else:
        _, utility = self.__minimize(child, alpha, beta, depth-1)

      if utility < min_utility:
        min_child, min_utility = option, utility

      if min_utility <= alpha:
        break

      beta = min(beta, min_utility)

    return min_child, min_utility

  def solve(self, state, max_time):
    self.time_start = time.time()
    self.max_time = max_time

    best_option = None
    for depth in range(1, 10000):
      try:
        best_option, _ = self.__maximize(state, -np.inf, np.inf, depth)
      except StopIteration:
        break

    return best_option

def choose_int(prompt, valid):
  while True:
    s = input(prompt).strip()
    if s.isdigit():
      x = int(s)
      if x in valid:
        return x
    print(f"Entrada inválida. Opciones: {valid}")

def main():
  print("ONITAMA - Humano vs IA (Minimax)")
  session = OnitamaGameSession(player_types=["human", "AI"], minimax_time=30)

  while True:
    if session.is_terminal():
      session.print_state()
      pts = session.get_winners_points()
      print("\nFIN. Puntos:", pts)
      break

    session.print_state()
    player = session.curr_player.name

    options = session.get_available_decisions()
    if len(options) == 0:
      w = opponent(player)
      session.winners = [Player(w), Player(opponent(w))]
      continue

    if session.curr_player.type_ == "AI":
      solver = MinimaxSolver(session.curr_player.name)
      st = copy.deepcopy(session)
      st.hide_print = True
      decision = solver.solve(st, session.minimax_time)
      ok = session.play_turn(decision)

      if not session.hide_print:
        print(f"\n[IA] {session.option_to_text(decision)}")
        print(session.last_move_msg)
      continue

    count1 = sum(1 for m in options if m[2] == 0)
    count2 = sum(1 for m in options if m[2] == 1)
    print(f"\nJugadas disponibles: Carta 1 = {count1} | Carta 2 = {count2}")

    ci = choose_int("\nElige carta (1/2): ", [1, 2]) - 1
    options_card = [m for m in options if m[2] == ci]
    if not options_card:
      print("Esa carta no tiene movimientos. Vuelve a elegir.")
      continue

    print(f"\nMovimientos con {session.hands[player][ci].name}:")
    for i, opt in enumerate(options_card, start=1):
      print(f"{i}) {session.option_to_text(opt)}")

    mi = choose_int("> ", list(range(1, len(options_card)+1))) - 1
    decision = options_card[mi]
    ok = session.play_turn(decision)
    if not ok:
      print("Movimiento inválido.")
    else:
      print("\n" + session.last_move_msg)

if __name__ == "__main__":
  main()