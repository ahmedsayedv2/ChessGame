import time
import math
import copy
from move_validation import get_piece_moves
from checkmate_logic import is_checkmate, is_stalemate, is_in_check
from utils import switch_turn

# Piece value mapping and piece-square tables
pieceScore = {"K": 0, "Q": -90, "R": -50, "B": -35, "N": -30, "p": -10}
knightScore = [[-1, -1, -1, -1, -1, -1, -1, -1],
               [-1, -2, -2, -2, -2, -2, -2, -1],
               [-1, -2, -3, -3, -3, -3, -2, -1],
               [-1, -2, -3, -4, -4, -3, -2, -1],
               [-1, -2, -3, -4, -4, -3, -2, -1],
               [-1, -2, -3, -3, -3, -3, -2, -1],
               [-1, -2, -2, -2, -2, -2, -2, -1],
               [-1, -1, -1, -1, -1, -1, -1, -1]]

bishopScore = [[-4, -3, -2, -1, -1, -2, -3, -4],
               [-3, -4, -3, -2, -2, -3, -4, -3],
               [-2, -3, -4, -3, -3, -4, -3, -2],
               [-1, -2, -3, -4, -4, -3, -2, -1],
               [-1, -2, -3, -4, -4, -3, -2, -1],
               [-2, -3, -4, -3, -3, -4, -3, -2],
               [-3, -4, -3, -2, -2, -3, -4, -3],
               [-4, -3, -2, -1, -1, -2, -3, -4]]

queenScore = [[-1, -1, -1, -3, -1, -1, -1, -1],
              [-1, -2, -3, -3, -3, -1, -1, -1],
              [-1, -4, -3, -3, -3, -4, -2, -1],
              [-1, -2, -3, -3, -3, -2, -2, -1],
              [-1, -2, -3, -3, -3, -2, -2, -1],
              [-1, -4, -3, -3, -3, -4, -2, -1],
              [-1, -2, -3, -3, -3, -1, -1, -1],
              [-1, -1, -1, -3, -1, -1, -1, -1]]

rookScore = [[-4, -3, -4, -4, -4, -4, -3, -4],
             [-4, -4, -4, -4, -4, -4, -4, -4],
             [-1, -1, -2, -3, -3, -2, -1, -1],
             [-1, -2, -3, -4, -4, -3, -2, -1],
             [-1, -2, -3, -4, -4, -3, -2, -1],
             [-1, -1, -2, -3, -3, -2, -1, -1],
             [-4, -4, -4, -4, -4, -4, -4, -4],
             [-4, -3, -4, -4, -4, -4, -3, -4]]

whitePawnScore = [[-8, -8, -8, -8, -8, -8, -8, -8],
                 [-8, -8, -8, -8, -8, -8, -8, -8],
                 [-5, -6, -6, -7, -7, -6, -6, -5],
                 [-2, -3, -3, -5, -5, -3, -3, -2],
                 [-1, -2, -3, -4, -4, -3, -2, -1],
                 [-1, -2, -3, -3, -3, -3, -2, -1],
                 [-1, -1, -1, 0, 0, -1, -1, -1],
                 [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScore = [[0, 0, 0, 0, 0, 0, 0, 0],
                 [-1, -1, -1, 0, 0, -1, -1, -1],
                 [-1, -2, -3, -3, -3, -3, -2, -1],
                 [-1, -2, -3, -4, -4, -3, -2, -1],
                 [-2, -3, -3, -5, -5, -3, -3, -2],
                 [-5, -6, -6, -7, -7, -6, -6, -5],
                 [-8, -8, -8, -8, -8, -8, -8, -8],
                 [-8, -8, -8, -8, -8, -8, -8, -8]]

piecePosScores = {'N': knightScore, 'B': bishopScore, 'Q': queenScore, 'R': rookScore, "wp": whitePawnScore, "bp": blackPawnScore}

CHECKMATE = -100000
STALEMATE = 0
MAX_DEPTH = 5

# Transposition table for faster evaluation
transposition_table = {}

def get_all_possible_moves(board_obj, color):
    moves = []
    board = board_obj.board
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece.strip() and piece != '##' and piece[0].lower() == color[0].lower():
                for r2 in range(8):
                    for c2 in range(8):
                        if get_piece_moves(piece, board_obj, (r, c), color, (r2, c2)):
                            moves.append(((r, c), (r2, c2)))
    return moves

def order_moves(moves, board_obj, color):
    scored = []
    for move in moves:
        temp_board = copy.deepcopy(board_obj)
        from_pos, to_pos = move
        moved_piece = temp_board.board[from_pos[0]][from_pos[1]]
        captured_piece = temp_board.board[to_pos[0]][to_pos[1]]

        temp_board.move_piece(move, color)
        score = evaluate_board(temp_board)

        move_value = 0
        moved_val = pieceScore.get(moved_piece[1].upper(), 0)
        captured_val = pieceScore.get(captured_piece[1].upper(), 0) if captured_piece.strip() and captured_piece != '##' else 0

        if captured_val:
            move_value += (captured_val - moved_val)
        
        if is_in_check(temp_board, switch_turn(color)):
            move_value += 20  # Reward moves that lead to check

        score += move_value * (1 if color == 'w' else -1)
        scored.append((score, move))

    scored.sort(reverse=(color == 'w'), key=lambda x: x[0])
    return [move for (_, move) in scored]

def evaluate_board(board_obj):
    board_hash = str(board_obj.board)
    if board_hash in transposition_table:
        return transposition_table[board_hash][0]

    if is_checkmate(board_obj, 'black'): return CHECKMATE
    if is_checkmate(board_obj, 'white'): return -CHECKMATE
    if is_stalemate(board_obj, 'white') or is_stalemate(board_obj, 'black'): return STALEMATE

    score = 0
    board = board_obj.board
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece.strip() and piece != '##':
                piece_type = piece[1].upper()
                color = piece[0].lower()
                value = pieceScore.get(piece_type, 0)

                key = piece_type
                if piece_type == "P":
                    key = piece.lower()
                if key in piecePosScores:
                    value += piecePosScores[key][r][c]

                score += value if color == 'w' else -value

    transposition_table[board_hash] = (score, None)
    return score

def minimax(board_obj, depth, alpha, beta, maximizing, color):
    board_hash = str(board_obj.board)
    if board_hash in transposition_table:
        return transposition_table[board_hash]

    if depth == 0:
        return evaluate_board(board_obj), None

    valid_moves = get_all_possible_moves(board_obj, color)
    if not valid_moves:
        if is_in_check(board_obj, color):
            return (-CHECKMATE if maximizing else CHECKMATE), None
        return STALEMATE, None

    valid_moves = order_moves(valid_moves, board_obj, color)
    best_move = None

    if maximizing:
        max_score = -math.inf
        for move in valid_moves:
            temp_board = copy.deepcopy(board_obj)
            temp_board.move_piece(move, color)
            score, _ = minimax(temp_board, depth - 1, alpha, beta, False, switch_turn(color))
            if score > max_score:
                max_score, best_move = score, move
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        transposition_table[board_hash] = (max_score, best_move)
        return max_score, best_move
    else:
        min_score = math.inf
        for move in valid_moves:
            temp_board = copy.deepcopy(board_obj)
            temp_board.move_piece(move, color)
            score, _ = minimax(temp_board, depth - 1, alpha, beta, True, switch_turn(color))
            if score < min_score:
                min_score, best_move = score, move
            beta = min(beta, score)
            if beta <= alpha:
                break
        transposition_table[board_hash] = (min_score, best_move)
        return min_score, best_move

def get_ai_move(board_obj, color):
    valid_moves = get_all_possible_moves(board_obj, color)
    if not valid_moves:
        return None

    best_move = None
    start_time = time.time()

    
    score, move = minimax(board_obj, MAX_DEPTH, -math.inf, math.inf, True, color)
    best_move = move
    print(f"AI Move Time: {time.time() - start_time:.2f}s")
    return best_move

def count_pieces(board_obj):
    return sum(1 for row in board_obj.board for piece in row if piece.strip() and piece != '##')
