import random
import time
import math
import copy
from move_validation import get_piece_moves
from checkmate_logic import is_checkmate, is_stalemate, is_in_check
from utils import switch_turn


CHECKMATE = 100000
STALEMATE = 0
MAX_DEPTH = 3


pieceScore = {"K": 0, "Q": 90, "R": 50, "B": 35, "N": 30, "P": 10}


knightScore = [[1, 1, 1, 1, 1, 1, 1, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScore = [[4, 3, 2, 1, 1, 2, 3, 4],
               [3, 4, 3, 2, 2, 3, 4, 3],
               [2, 3, 4, 3, 3, 4, 3, 2],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [2, 3, 4, 3, 3, 4, 3, 2],
               [3, 4, 3, 2, 2, 3, 4, 3],
               [4, 3, 2, 1, 1, 2, 3, 4]]

queenScore = [[1, 1, 1, 3, 1, 1, 1, 1],
              [1, 2, 3, 3, 3, 1, 1, 1],
              [1, 4, 3, 3, 3, 4, 2, 1],
              [1, 2, 3, 3, 3, 2, 2, 1],
              [1, 2, 3, 3, 3, 2, 2, 1],
              [1, 4, 3, 3, 3, 4, 2, 1],
              [1, 2, 3, 3, 3, 1, 1, 1],
              [1, 1, 1, 3, 1, 1, 1, 1]]

rookScore = [[4, 3, 4, 4, 4, 4, 3, 4],
             [4, 4, 4, 4, 4, 4, 4, 4],
             [1, 1, 2, 3, 3, 2, 1, 1],
             [1, 2, 3, 4, 4, 3, 2, 1],
             [1, 2, 3, 4, 4, 3, 2, 1],
             [1, 1, 2, 3, 3, 2, 1, 1],
             [4, 4, 4, 4, 4, 4, 4, 4],
             [4, 3, 4, 4, 4, 4, 3, 4]]

whitePawnScore = [[8, 8, 8, 8, 8, 8, 8, 8],
                  [8, 8, 8, 8, 8, 8, 8, 8],
                  [5, 6, 6, 7, 7, 6, 6, 5],
                  [2, 3, 3, 5, 5, 3, 3, 2],
                  [1, 2, 3, 4, 4, 3, 2, 1],
                  [1, 2, 3, 3, 3, 3, 2, 1],
                  [1, 1, 1, 0, 0, 1, 1, 1],
                  [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScore = [[0, 0, 0, 0, 0, 0, 0, 0],
                  [1, 1, 1, 0, 0, 1, 1, 1],
                  [1, 2, 3, 3, 3, 3, 2, 1],
                  [1, 2, 3, 4, 4, 3, 2, 1],
                  [2, 3, 3, 5, 5, 3, 3, 2],
                  [5, 6, 6, 7, 7, 6, 6, 5],
                  [8, 8, 8, 8, 8, 8, 8, 8],
                  [8, 8, 8, 8, 8, 8, 8, 8]]

piecePosScores = {'N': knightScore, 'B': bishopScore, 'Q': queenScore,
                  'R': rookScore, "wp": whitePawnScore, "bp": blackPawnScore}


def find_random_move(valid_moves):

    return random.choice(valid_moves) if valid_moves else None


def get_all_possible_moves(board_obj, color):

    moves = []
    board = board_obj.board
    for start_row in range(8):
        for start_col in range(8):
            piece = board[start_row][start_col]
            if piece.strip() and piece != '##' and piece[0].lower() == color[0].lower():
                for end_row in range(8):
                    for end_col in range(8):
                        start_pos = (start_row, start_col)
                        end_pos = (end_row, end_col)
                        if get_piece_moves(piece, board_obj, start_pos, color, end_pos):
                            moves.append((start_pos, end_pos))
    return moves


def order_moves(moves, board_obj, color):

    scored_moves = []
    board = board_obj.board
    for move in moves:
        score = 0
        start, end = move
        piece = board[start[0]][start[1]]
        target = board[end[0]][end[1]]

        if target.strip() and target != '##':
            score += 10 * pieceScore.get(target[1].upper(), 0)
        if (end[0], end[1]) in [(3, 3), (3, 4), (4, 3), (4, 4)]:
            score += 5

        temp_board = copy.deepcopy(board_obj)
        temp_board.move_piece(move, color)
        if is_in_check(temp_board, switch_turn(color)):
            score += 30

        scored_moves.append((score, move))

    scored_moves.sort(reverse=True, key=lambda x: x[0])
    return [move for (score, move) in scored_moves]


def evaluate_board(board_obj):

    if is_checkmate(board_obj, 'black'): return CHECKMATE
    if is_checkmate(board_obj, 'white'): return -CHECKMATE
    if is_stalemate(board_obj, 'white') or is_stalemate(board_obj, 'black'): return STALEMATE

    score = 0
    board = board_obj.board
    center_control = 0
    piece_development = 0

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.strip() and piece != '##':
                piece_type = piece[1].upper()
                color = piece[0].lower()
                value = pieceScore.get(piece_type, 0)

                if piece_type == 'P':
                    pos_key = 'wp' if color == 'w' else 'bp'
                    value += piecePosScores[pos_key][row][col]
                else:
                    value += piecePosScores.get(piece_type, [[0] * 8] * 8)[row][col]

                if (row, col) in [(3, 3), (3, 4), (4, 3), (4, 4)]:
                    center_control += 1 if color == 'w' else -1

                if piece_type in ['N', 'B']:
                    if color == 'w' and row < 6:
                        piece_development += 1
                    elif color == 'b' and row > 1:
                        piece_development -= 1

                if color == 'w':
                    score += value
                else:
                    score -= value

    score += center_control * 3 + piece_development * 2
    return score


def minimax(board_obj, depth, alpha, beta, maximizing_player, color):

    if depth == 0:
        return evaluate_board(board_obj), None

    valid_moves = get_all_possible_moves(board_obj, color)
    if not valid_moves:
        if is_in_check(board_obj, color):
            return (-CHECKMATE, None) if maximizing_player else (CHECKMATE, None)
        return (STALEMATE, None)

    valid_moves = order_moves(valid_moves, board_obj, color)
    best_move = None

    if maximizing_player:
        max_score = -math.inf
        for move in valid_moves:
            temp_board = copy.deepcopy(board_obj)
            temp_board.move_piece(move, color)
            current_score, _ = minimax(temp_board, depth - 1, alpha, beta, False, switch_turn(color))
            if current_score > max_score:
                max_score = current_score
                best_move = move
                alpha = max(alpha, current_score)
            if beta <= alpha: break
        return max_score, best_move
    else:
        min_score = math.inf
        for move in valid_moves:
            temp_board = copy.deepcopy(board_obj)
            temp_board.move_piece(move, color)
            current_score, _ = minimax(temp_board, depth - 1, alpha, beta, True, switch_turn(color))
            if current_score < min_score:
                min_score = current_score
                best_move = move
                beta = min(beta, current_score)
            if beta <= alpha: break
        return min_score, best_move


def get_ai_move(board_obj, color, difficulty="hard"):

    valid_moves = get_all_possible_moves(board_obj, color)
    if not valid_moves: return None

    if difficulty == "easy":
        return find_random_move(valid_moves)
    elif difficulty == "medium":
        return find_random_move(valid_moves) if random.random() < 0.3 else None

    start_time = time.time()
    depth = MAX_DEPTH + 1 if count_pieces(board_obj) < 10 else MAX_DEPTH
    _, best_move = minimax(board_obj, depth, -math.inf, math.inf, True, color)
    print(f"AI Move Time: {time.time() - start_time:.2f}s")
    return best_move


def count_pieces(board_obj):

    return sum(1 for row in board_obj.board for piece in row if piece.strip() and piece != '##')