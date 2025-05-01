import random
import time
import math
import copy
from move_validation import get_piece_moves
from checkmate_logic import is_checkmate, is_stalemate, is_in_check
from utils import switch_turn

CHECKMATE = 100000
STALEMATE = 0
MAX_DEPTH = 10  # Balanced depth for faster but smarter decisions

pieceScore = {
    "K": 1000,
    "Q": 90,
    "R": 50,
    "B": 35,
    "N": 30,
    "P": 10
}

piecePosScores = {
    'N': [[-5, -4, -3, -3, -3, -3, -4, -5],
          [-4, -2, 0, 0, 0, 0, -2, -4],
          [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
          [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
          [-3, 0, 1.5, 2, 2, 1.5, 0, -3],
          [-3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3],
          [-4, -2, 0, 0.5, 0.5, 0, -2, -4],
          [-5, -4, -3, -3, -3, -3, -4, -5]],
    'B': [[-2, -1, -1, -1, -1, -1, -1, -2],
          [-1, 0, 0, 0, 0, 0, 0, -1],
          [-1, 0, 0.5, 1, 1, 0.5, 0, -1],
          [-1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1],
          [-1, 0, 1, 1, 1, 1, 0, -1],
          [-1, 1, 1, 1, 1, 1, 1, -1],
          [-1, 0.5, 0, 0, 0, 0, 0.5, -1],
          [-2, -1, -1, -1, -1, -1, -1, -2]],
    'R': [[0, 0, 0, 0.5, 0.5, 0, 0, 0],
          [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
          [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
          [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
          [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
          [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
          [0.5, 1, 1, 1, 1, 1, 1, 0.5],
          [0, 0, 0, 0, 0, 0, 0, 0]],
    'Q': [[-2, -1, -1, -0.5, -0.5, -1, -1, -2],
          [-1, 0, 0, 0, 0, 0, 0, -1],
          [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
          [-0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
          [0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
          [-1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1],
          [-1, 0, 0.5, 0, 0, 0, 0, -1],
          [-2, -1, -1, -0.5, -0.5, -1, -1, -2]],
    'P': [[0, 0, 0, 0, 0, 0, 0, 0],
          [5, 5, 5, 5, 5, 5, 5, 5],
          [1, 1, 2, 3, 3, 2, 1, 1],
          [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
          [0, 0, 0, 2, 2, 0, 0, 0],
          [0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5],
          [0.5, 1, 1, -2, -2, 1, 1, 0.5],
          [0, 0, 0, 0, 0, 0, 0, 0]]
}

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
        captured = temp_board.board[move[1][0]][move[1][1]]
        temp_board.move_piece(move, color)
        score = evaluate_board(temp_board)
        if captured.strip() and captured != '##':
            score += pieceScore.get(captured[1].upper(), 0) * (1 if color == 'w' else -1)
        scored.append((score, move))
    scored.sort(reverse=(color == 'w'), key=lambda x: x[0])
    return [move for (_, move) in scored]

def evaluate_board(board_obj):
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
                if piece_type in piecePosScores:
                    value += piecePosScores[piece_type][r][c]
                score += value if color == 'w' else -value
    return score

def minimax(board_obj, depth, alpha, beta, maximizing, color):
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
        return min_score, best_move

def get_ai_move(board_obj, color):
    valid_moves = get_all_possible_moves(board_obj, color)
    if not valid_moves:
        return None
    start_time = time.time()
    depth = MAX_DEPTH if count_pieces(board_obj) <= 24 else 2
    _, best_move = minimax(board_obj, depth, -math.inf, math.inf, True, color)
    print(f"AI Move Time: {time.time() - start_time:.2f}s")
    return best_move

def count_pieces(board_obj):
    return sum(1 for row in board_obj.board for piece in row if piece.strip() and piece != '##')
