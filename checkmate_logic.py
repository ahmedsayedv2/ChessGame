import board
import copy


def find_king(board, king_color):

    king_symbol = 'wK' if king_color == 'white' else 'bK'
    for row in range(8):
        for col in range(8):
            if board[row][col] == king_symbol:
                return (row, col)
    return None


def is_in_check(board_obj, color):

    board = board_obj.board if hasattr(board_obj, 'board') else board_obj
    king_pos = find_king(board, color)

    if not king_pos:
        return False

    opposite_color = 'black' if color == 'white' else 'white'

    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece.strip() != '' and piece[0].lower() == opposite_color[0].lower():
                if is_piece_threatening_king(piece, (row, col), king_pos, board):
                    return True
    return False


def is_piece_threatening_king(piece, piece_pos, king_pos, board):

    pr, pc = piece_pos
    kr, kc = king_pos


    if piece[1].lower() == 'p':
        if piece[0] == 'b':
            return kr == pr + 1 and (kc == pc - 1 or kc == pc + 1)
        elif piece[0] == 'w':
            return kr == pr - 1 and (kc == pc - 1 or kc == pc + 1)


    if piece[1].lower() == 'n':
        return (abs(kr - pr), abs(kc - pc)) in [(2, 1), (1, 2)]


    if piece[1].lower() in ['r', 'q']:
        if pr == kr:
            step = 1 if kc > pc else -1
            for c in range(pc + step, kc, step):
                if not is_empty(board[pr][c]):
                    return False
            return True
        if pc == kc:
            step = 1 if kr > pr else -1
            for r in range(pr + step, kr, step):
                if not is_empty(board[r][pc]):
                    return False
            return True

    if piece[1].lower() in ['b', 'q']:
        if abs(pr - kr) == abs(pc - kc):
            step_r = 1 if kr > pr else -1
            step_c = 1 if kc > pc else -1
            r, c = pr + step_r, pc + step_c
            while r != kr and c != kc:
                if not is_empty(board[r][c]):
                    return False
                r += step_r
                c += step_c
            return True

    # تهديدات الملك
    if piece[1].lower() == 'k':
        return max(abs(kr - pr), abs(kc - pc)) == 1

    return False


def is_checkmate(board_obj, color):
    if not is_in_check(board_obj, color):
        return False

    for move in board_obj.get_all_legal_moves(color):
        temp_board = copy.deepcopy(board_obj)
        temp_board.move_piece(move, color)
        if not is_in_check(temp_board, color):
            return False

    return True


def is_stalemate(board_obj, color):

    if is_in_check(board_obj, color):
        return False


    if len(board_obj.get_all_legal_moves(color)) == 0:
        return True

    return False


def is_empty(square):
    return square in ['  ', '##']