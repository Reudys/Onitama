import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

SIZE = 5

# =========================
# Cartas
# =========================

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
    Card("Goose",  ((-1, -1), (-1, 0), (0, 0), (0, 1))),   # se normaliza abajo
    Card("Rooster",((-1, 0), (-1, 1), (0, -1), (0, 1))),   # se normaliza abajo
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

# =========================
# Utilidades
# =========================

def inside(r: int, c: int) -> bool:
    return 0 <= r < SIZE and 0 <= c < SIZE

def opponent(player: str) -> str:
    return "R" if player == "B" else "B"

def rc_to_coord(r: int, c: int) -> str:
    file_ch = chr(ord('a') + c)
    rank = SIZE - r
    return f"{file_ch}{rank}"

def choose_int(prompt: str, valid: List[int]) -> int:
    while True:
        s = input(prompt).strip()
        if s.isdigit():
            x = int(s)
            if x in valid:
                return x
        print(f"Entrada inválida. Opciones: {valid}")

# =========================
# Estado del juego (inmutable)
# =========================

@dataclass(frozen=True)
class GameState:
    board: Tuple[Tuple[str, ...], ...]
    hands_B: Tuple[int, int]  # índices en CARDS_N
    hands_R: Tuple[int, int]
    side: int
    turn: str                # "B" o "R"

TEMPLE_R = (0, 2)
TEMPLE_B = (4, 2)

def init_state(seed: Optional[int] = None) -> GameState:
    if seed is not None:
        random.seed(seed)

    board = [["." for _ in range(SIZE)] for _ in range(SIZE)]
    board[0] = ["R", "R", "RM", "R", "R"]
    board[4] = ["B", "B", "BM", "B", "B"]

    five = random.sample(list(range(len(CARDS_N))), 5)
    hands_B = (five[0], five[1])
    hands_R = (five[2], five[3])
    side = five[4]
    turn = random.choice(["B", "R"])

    return GameState(
        board=tuple(tuple(row) for row in board),
        hands_B=hands_B,
        hands_R=hands_R,
        side=side,
        turn=turn
    )

def get_hands(state: GameState, player: str) -> Tuple[int, int]:
    return state.hands_B if player == "B" else state.hands_R

def card_moves_for_player(card: Card, player: str) -> List[Tuple[int, int]]:
    # B: como está; R: invertimos dr (vertical)
    if player == "B":
        return list(card.moves)
    return [(-dr, dc) for (dr, dc) in card.moves]

# Move: ((r,c),(nr,nc), card_index_in_hand 0/1)
Move = Tuple[Tuple[int, int], Tuple[int, int], int]

def all_legal_moves(state: GameState, player: str) -> List[Move]:
    legal: List[Move] = []
    h = get_hands(state, player)
    for hand_idx, card_idx in enumerate(h):
        card = CARDS_N[card_idx]
        moves = card_moves_for_player(card, player)
        for r in range(SIZE):
            for c in range(SIZE):
                p = state.board[r][c]
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
                    dest = state.board[nr][nc]
                    if dest != ".":
                        if player == "B" and dest.startswith("B"):
                            continue
                        if player == "R" and dest.startswith("R"):
                            continue
                    legal.append(((r, c), (nr, nc), hand_idx))
    return legal

def apply_move(state: GameState, move: Move) -> GameState:
    (r, c), (nr, nc), hand_idx = move
    player = state.turn
    opp = opponent(player)

    board = [list(row) for row in state.board]
    piece = board[r][c]
    board[r][c] = "."
    board[nr][nc] = piece

    h = list(get_hands(state, player))
    used_card = h[hand_idx]
    h[hand_idx] = state.side
    new_side = used_card

    if player == "B":
        return GameState(
            board=tuple(tuple(row) for row in board),
            hands_B=(h[0], h[1]),
            hands_R=state.hands_R,
            side=new_side,
            turn=opp
        )
    else:
        return GameState(
            board=tuple(tuple(row) for row in board),
            hands_B=state.hands_B,
            hands_R=(h[0], h[1]),
            side=new_side,
            turn=opp
        )

def check_winner(state: GameState) -> Optional[str]:
    found_BM = False
    found_RM = False
    for r in range(SIZE):
        for c in range(SIZE):
            if state.board[r][c] == "BM":
                found_BM = True
            elif state.board[r][c] == "RM":
                found_RM = True

    if not found_BM:
        return "R"
    if not found_RM:
        return "B"

    if state.board[TEMPLE_R[0]][TEMPLE_R[1]] == "BM":
        return "B"
    if state.board[TEMPLE_B[0]][TEMPLE_B[1]] == "RM":
        return "R"

    return None

# =========================
# Heurística (>=5 señales)
# =========================

CENTER_SQS = {(2,2), (2,1), (2,3), (1,2), (3,2)}

def manhattan(a: Tuple[int,int], b: Tuple[int,int]) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def evaluate(state: GameState, perspective: str) -> int:
    winner = check_winner(state)
    if winner == perspective:
        return 10_000
    if winner == opponent(perspective):
        return -10_000

    my_prefix = perspective
    op_prefix = opponent(perspective)

    my_pawns = 0
    op_pawns = 0
    my_master_pos = None
    op_master_pos = None
    my_center = 0
    op_center = 0

    for r in range(SIZE):
        for c in range(SIZE):
            p = state.board[r][c]
            if p == ".":
                continue
            if p.startswith(my_prefix):
                if p.endswith("M"):
                    my_master_pos = (r, c)
                else:
                    my_pawns += 1
                if (r, c) in CENTER_SQS:
                    my_center += 1
            elif p.startswith(op_prefix):
                if p.endswith("M"):
                    op_master_pos = (r, c)
                else:
                    op_pawns += 1
                if (r, c) in CENTER_SQS:
                    op_center += 1

    score = 0
    score += (my_pawns - op_pawns) * 120
    score += (0 if my_master_pos else -5000)
    score += (0 if op_master_pos else 5000)

    if my_master_pos:
        target = TEMPLE_R if perspective == "B" else TEMPLE_B
        score += (8 - manhattan(my_master_pos, target)) * 90
    if op_master_pos:
        op_target = TEMPLE_R if op_prefix == "B" else TEMPLE_B
        score -= (8 - manhattan(op_master_pos, op_target)) * 90

    my_moves = len(all_legal_moves(state, perspective))
    op_moves = len(all_legal_moves(state, op_prefix))
    score += (my_moves - op_moves) * 10

    score += (my_center - op_center) * 25

    if my_master_pos and op_master_pos:
        score += (6 - manhattan(my_master_pos, op_master_pos)) * 20

    return score

# =========================
# Agentes
# =========================

class AgentStats:
    def __init__(self):
        self.nodes = 0
        self.max_depth = 0
        self.time_spent = 0.0

class PlayerAgent:
    label = "Agente"

    def get_label(self) -> str:
        return self.label

    def choose(self, state: GameState, stats: AgentStats) -> Move:
        raise NotImplementedError

class HumanAgent(PlayerAgent):
    label = "Humano"

    def choose(self, state: GameState, stats: AgentStats) -> Move:
        legal = all_legal_moves(state, state.turn)
        if not legal:
            raise RuntimeError("No hay movimientos legales (estado raro).")

        h = get_hands(state, state.turn)
        print(f"\n[{self.label}] Cartas de {state.turn}: 1) {CARDS_N[h[0]].name}   2) {CARDS_N[h[1]].name}")
        print("Elige carta: 1 o 2")
        ci = choose_int("> ", [1, 2]) - 1

        legal_for_card = [m for m in legal if m[2] == ci]
        if not legal_for_card:
            print("Esa carta no tiene movimientos disponibles. Elige la otra.")
            return self.choose(state, stats)

        for i, (frm, to, _) in enumerate(legal_for_card, start=1):
            print(f"{i}) {rc_to_coord(*frm)} -> {rc_to_coord(*to)}")
        mi = choose_int("> ", list(range(1, len(legal_for_card) + 1))) - 1
        return legal_for_card[mi]

class RandomAgent(PlayerAgent):
    label = "IA - Random"

    def choose(self, state: GameState, stats: AgentStats) -> Move:
        return random.choice(all_legal_moves(state, state.turn))

class GreedyAgent(PlayerAgent):
    label = "IA - Greedy"

    def choose(self, state: GameState, stats: AgentStats) -> Move:
        player = state.turn
        legal = all_legal_moves(state, player)
        best_mv = legal[0]
        best_sc = -10**18
        for mv in legal:
            sc = evaluate(apply_move(state, mv), player)
            if sc > best_sc:
                best_sc = sc
                best_mv = mv
        return best_mv

class WorstAgent(PlayerAgent):
    label = "IA - Worst"

    def choose(self, state: GameState, stats: AgentStats) -> Move:
        player = state.turn
        legal = all_legal_moves(state, player)
        worst_mv = legal[0]
        worst_sc = 10**18
        for mv in legal:
            sc = evaluate(apply_move(state, mv), player)
            if sc < worst_sc:
                worst_sc = sc
                worst_mv = mv
        return worst_mv

class MinimaxAgent(PlayerAgent):
    label = "IA - Minimax"

    def __init__(self, time_limit_sec: float = 2.0):
        self.time_limit_sec = time_limit_sec
        self.deadline = 0.0

    def choose(self, state: GameState, stats: AgentStats) -> Move:
        player = state.turn
        self.deadline = time.perf_counter() + self.time_limit_sec

        legal = all_legal_moves(state, player)
        if not legal:
            return random.choice(legal)

        best_move = random.choice(legal)
        best_score = -10**18

        depth = 1
        while True:
            if time.perf_counter() >= self.deadline:
                break
            try:
                score, move = self._search_depth(state, depth, player, stats)
                if time.perf_counter() < self.deadline and move is not None:
                    best_score, best_move = score, move
                    stats.max_depth = max(stats.max_depth, depth)
                depth += 1
            except TimeoutError:
                break

        return best_move

    def _search_depth(self, state: GameState, depth: int, root_player: str, stats: AgentStats) -> Tuple[int, Optional[Move]]:
        alpha = -10**18
        beta = 10**18
        best_move = None
        best_score = -10**18

        legal = all_legal_moves(state, state.turn)
        maximizing_root = (state.turn == root_player)
        legal_sorted = sorted(
            legal,
            key=lambda mv: evaluate(apply_move(state, mv), root_player),
            reverse=maximizing_root
        )

        for mv in legal_sorted:
            if time.perf_counter() >= self.deadline:
                raise TimeoutError
            s2 = apply_move(state, mv)
            sc = self._alphabeta(s2, depth - 1, alpha, beta, root_player, stats)
            if sc > best_score:
                best_score = sc
                best_move = mv
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break

        return best_score, best_move

    def _alphabeta(self, state: GameState, depth: int, alpha: int, beta: int, root_player: str, stats: AgentStats) -> int:
        if time.perf_counter() >= self.deadline:
            raise TimeoutError

        stats.nodes += 1

        winner = check_winner(state)
        if winner is not None:
            return 10_000 if winner == root_player else -10_000

        if depth == 0:
            return evaluate(state, root_player)

        legal = all_legal_moves(state, state.turn)
        if not legal:
            return evaluate(state, root_player)

        maximizing = (state.turn == root_player)
        legal_sorted = sorted(
            legal,
            key=lambda mv: evaluate(apply_move(state, mv), root_player),
            reverse=maximizing
        )

        if maximizing:
            value = -10**18
            for mv in legal_sorted:
                s2 = apply_move(state, mv)
                value = max(value, self._alphabeta(s2, depth - 1, alpha, beta, root_player, stats))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:
            value = 10**18
            for mv in legal_sorted:
                s2 = apply_move(state, mv)
                value = min(value, self._alphabeta(s2, depth - 1, alpha, beta, root_player, stats))
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

# =========================
# UI / Impresión (CON IDENTIDAD DEL JUGADOR)
# =========================

def player_name(turn: str) -> str:
    return "Azul (B)" if turn == "B" else "Rojo (R)"

def print_state(state: GameState, agents: Dict[str, PlayerAgent]):
    print("\n" + "=" * 45)
    print(f"Turno: {player_name(state.turn)}  [{agents[state.turn].get_label()}]")
    print("Cartas:")
    print(f"  B: 1) {CARDS_N[state.hands_B[0]].name}   2) {CARDS_N[state.hands_B[1]].name}")
    print(f"  R: 1) {CARDS_N[state.hands_R[0]].name}   2) {CARDS_N[state.hands_R[1]].name}")
    print(f"  Mesa (side): {CARDS_N[state.side].name}")
    print("\nTablero:")
    print("    a  b  c  d  e")
    for r in range(SIZE):
        rank = SIZE - r
        row_str = " ".join(state.board[r][c].rjust(2) for c in range(SIZE))
        print(f" {rank}  {row_str}")
    print("=" * 45)

# =========================
# Selección por menú
# =========================

def choose_agent(player_label: str, time_limit_holder: Dict[str, float]) -> PlayerAgent:
    print(f"\nSelecciona agente para {player_label}:")
    print("1) Humano")
    print("2) IA - Random")
    print("3) IA - Greedy")
    print("4) IA - Worst")
    print("5) IA - Minimax")

    choice = choose_int("> ", [1, 2, 3, 4, 5])

    if choice == 1:
        return HumanAgent()
    if choice == 2:
        return RandomAgent()
    if choice == 3:
        return GreedyAgent()
    if choice == 4:
        return WorstAgent()

    if "time" not in time_limit_holder:
        s = input("Tiempo límite Minimax (segundos, ej 2): ").strip()
        try:
            time_limit_holder["time"] = float(s)
        except:
            time_limit_holder["time"] = 2.0
    return MinimaxAgent(time_limit_sec=time_limit_holder["time"])

# =========================
# Partida + Benchmark (con logs por movimiento y captura + identidad)
# =========================

def play_one_game(
    agent_B: PlayerAgent,
    agent_R: PlayerAgent,
    seed: Optional[int] = None,
    verbose: bool = True,
    max_turns: int = 500
) -> Tuple[str, Dict[str, AgentStats]]:

    state = init_state(seed=seed)
    stats = {"B": AgentStats(), "R": AgentStats()}
    agents: Dict[str, PlayerAgent] = {"B": agent_B, "R": agent_R}

    turns = 0
    while True:
        turns += 1
        if turns > max_turns:
            scB = evaluate(state, "B")
            winner = "B" if scB >= 0 else "R"
            if verbose:
                print_state(state, agents)
                print("\n⚠️ Límite de turnos alcanzado. Ganador por evaluación:", player_name(winner))
            return winner, stats

        winner = check_winner(state)
        if winner:
            if verbose:
                print_state(state, agents)
                print("\n🏆 GANADOR:", player_name(winner))
            return winner, stats

        if verbose:
            print_state(state, agents)

        turn = state.turn
        t0 = time.perf_counter()
        mv = agents[turn].choose(state, stats[turn])
        dt = time.perf_counter() - t0
        stats[turn].time_spent += dt

        # ---- LOG DEL MOVIMIENTO + CAPTURA + IDENTIDAD ----
        (r, c), (nr, nc), hand_idx = mv
        card_idx = get_hands(state, turn)[hand_idx]
        card_name = CARDS_N[card_idx].name

        captured = state.board[nr][nc]
        did_capture = (captured != ".")

        if verbose:
            msg = (
                f"\n👉 {player_name(turn)} [{agents[turn].get_label()}] "
                f"usa {card_name}: {rc_to_coord(r,c)} -> {rc_to_coord(nr,nc)}"
            )
            if did_capture:
                msg += f"  🔥 Captura: {captured}"
            print(msg)

        state = apply_move(state, mv)

def benchmark(n_games: int, agent_B: PlayerAgent, agent_R: PlayerAgent, seed: int = 123):
    wins = {"B": 0, "R": 0}
    total_nodes = {"B": 0, "R": 0}
    total_time = {"B": 0.0, "R": 0.0}
    total_depth = {"B": 0, "R": 0}

    for i in range(n_games):
        w, st = play_one_game(agent_B, agent_R, seed=seed + i, verbose=False)
        wins[w] += 1
        for p in ("B", "R"):
            total_nodes[p] += st[p].nodes
            total_time[p] += st[p].time_spent
            total_depth[p] += st[p].max_depth

    print("\n=== BENCHMARK ===")
    print(f"Partidas: {n_games}")
    print(f"B: {agent_B.get_label()}   vs   R: {agent_R.get_label()}")
    print(f"Ganó B: {wins['B']} | Ganó R: {wins['R']}")

    for p in ("B", "R"):
        avg_nodes = total_nodes[p] / n_games
        avg_time = total_time[p] / n_games
        avg_depth = total_depth[p] / n_games
        print(f"\nJugador {p}:")
        print(f"  Nodos promedio: {avg_nodes:.1f}")
        print(f"  Tiempo promedio: {avg_time:.3f}s")
        print(f"  Profundidad máx promedio (IDS): {avg_depth:.2f}")

# =========================
# Main
# =========================

def main():
    print("ONITAMA (Consola) + IA (Minimax + AlphaBeta + IDS)")
    print("\n1) Jugar 1 partida")
    print("2) Benchmark (muchas partidas)")
    mode = choose_int("> ", [1, 2])

    if mode == 1:
        time_limit_holder: Dict[str, float] = {}
        agent_B = choose_agent("Azul (B)", time_limit_holder)
        agent_R = choose_agent("Rojo (R)", time_limit_holder)
        play_one_game(agent_B, agent_R, seed=None, verbose=True)

    else:
        s = input("Cantidad de partidas (ej 50): ").strip()
        try:
            n_games = int(s)
        except:
            n_games = 50

        time_limit_holder: Dict[str, float] = {}
        agent_B = choose_agent("Azul (B)", time_limit_holder)
        agent_R = choose_agent("Rojo (R)", time_limit_holder)

        benchmark(n_games, agent_B, agent_R, seed=123)

if __name__ == "__main__":
    main()