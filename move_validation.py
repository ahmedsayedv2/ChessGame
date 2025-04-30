from checkmate_logic import *
from board import *
import copy


def is_empty(square):
    return square in ['  ', '##']


def simulate_move(board, start_pos, end_pos):
    temp_board = copy.deepcopy(board)
    piece = temp_board[start_pos[0]][start_pos[1]]
    temp_board[start_pos[0]][start_pos[1]] = '  ' if (start_pos[0] + start_pos[1]) % 2 else '##'
    temp_board[end_pos[0]][end_pos[1]] = piece
    return temp_board


def is_valid_pawn_move(board, start_pos, end_pos, color):
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    direction = -1 if color == 'white' else 1

    if start_col == end_col:
        if end_row == start_row + direction and is_empty(board[end_row][end_col]):
            return True
        if ((color == 'white' and start_row == 6) or (color == 'black' and start_row == 1)):
            if (end_row == start_row + 2 * direction and
                    is_empty(board[start_row + direction][start_col]) and
                    is_empty(board[end_row][end_col])):
                return True

    if abs(start_col - end_col) == 1 and end_row == start_row + direction:
        target = board[end_row][end_col]
        if not is_empty(target) and target[0].lower() != color[0].lower():
            return True

    return False


def is_valid_rook_move(board, start_pos, end_pos, color):
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    if start_row != end_row and start_col != end_col:
        return False

    step_row = 0 if start_row == end_row else (1 if end_row > start_row else -1)
    step_col = 0 if start_col == end_col else (1 if end_col > start_col else -1)

    row, col = start_row + step_row, start_col + step_col
    while (row, col) != (end_row, end_col):
        if not is_empty(board[row][col]):
            return False
        row += step_row
        col += step_col

    target = board[end_row][end_col]
    return is_empty(target) or target[0].lower() != color[0].lower()


def is_valid_bishop_move(board, start_pos, end_pos, color):
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    if abs(start_row - end_row) != abs(start_col - end_col):
        return False

    step_row = 1 if end_row > start_row else -1
    step_col = 1 if end_col > start_col else -1

    row, col = start_row + step_row, start_col + step_col
    while (row, col) != (end_row, end_col):
        if not is_empty(board[row][col]):
            return False
        row += step_row
        col += step_col

    target = board[end_row][end_col]
    return is_empty(target) or target[0].lower() != color[0].lower()


def is_valid_queen_move(board, start_pos, end_pos, color):
    return (is_valid_rook_move(board, start_pos, end_pos, color) or
            is_valid_bishop_move(board, start_pos, end_pos, color))


def is_valid_knight_move(board, start_pos, end_pos, color):
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    if (abs(start_row - end_row), abs(start_col - end_col)) not in [(2, 1), (1, 2)]:
        return False

    target = board[end_row][end_col]
    return is_empty(target) or target[0].lower() != color[0].lower()


def is_valid_king_move(board, start_pos, end_pos, color):
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    if max(abs(start_row - end_row), abs(start_col - end_col)) > 1:
        return False

    target = board[end_row][end_col]
    return is_empty(target) or target[0].lower() != color[0].lower()


def get_piece_moves(piece, board_obj, start_pos, color, end_pos):
    board = board_obj.board if hasattr(board_obj, 'board') else board_obj

    if piece.strip() == '' or piece == '##':
        return False

    if piece[0].lower() != color[0].lower():
        return False

    piece_type = piece[1].lower()
    move_is_valid = False

    if piece_type == 'p':
        move_is_valid = is_valid_pawn_move(board, start_pos, end_pos, color)
    elif piece_type == 'r':
        move_is_valid = is_valid_rook_move(board, start_pos, end_pos, color)
    elif piece_type == 'b':
        move_is_valid = is_valid_bishop_move(board, start_pos, end_pos, color)
    elif piece_type == 'q':
        move_is_valid = is_valid_queen_move(board, start_pos, end_pos, color)
    elif piece_type == 'n':
        move_is_valid = is_valid_knight_move(board, start_pos, end_pos, color)
    elif piece_type == 'k':
        move_is_valid = is_valid_king_move(board, start_pos, end_pos, color)

    if not move_is_valid:
        return False

    temp_board_obj = copy.deepcopy(board_obj)
    temp_board_obj.board = simulate_move(board, start_pos, end_pos)

    if is_in_check(temp_board_obj, color):
        return False

    return True