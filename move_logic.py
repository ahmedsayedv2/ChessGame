from move_validation import get_piece_moves
import copy

def handle_move(board_obj, move, color):
    start_pos, end_pos = move
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    piece = board_obj.board[start_row][start_col]

    if not get_piece_moves(piece, board_obj, start_pos, color, end_pos):
        return False

    board_obj.history.append(copy.deepcopy(board_obj.board))


    board_obj.board[end_row][end_col] = piece
    board_obj.board[start_row][start_col] = '  ' if (start_row + start_col) % 2 == 0 else '##'

    return True

def undo_last_move(board_obj):
    if board_obj.history:
        board_obj.board = board_obj.history.pop()
        return True
    return False