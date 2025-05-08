from move_validation import get_piece_moves
import copy

def handle_move(board_obj, move, color): 
    start_pos, end_pos = move 
    start_row, start_col = start_pos 
    end_row, end_col = end_pos 
 
    piece = board_obj.board[start_row][start_col] 
 
    # Check if the move is valid 
    if not get_piece_moves(piece, board_obj, start_pos, color, end_pos): 
        return False 
 
    # Castling logic 
    if start_row==0:
        if piece[1] == 'K' and abs(start_col - end_col) == 2: 
            row = start_row 
            if end_col == 6:  # Kingside
                board_obj.board[row][5] = color[0] + 'R' 
                board_obj.board[row][7] = '  ' if (row + 7) % 2 == 0 else '##' 
            elif end_col == 2:  # Queenside
                board_obj.board[row][3] = color[0] + 'R' 
                board_obj.board[row][0] = '  ' if (row + 0) % 2 == 0 else '##' 
            board_obj.castling_rights[color]['K'] = False 
            board_obj.castling_rights[color]['Q'] = False 
    elif start_row==7:
        if piece[1] == 'K' and abs(start_col - end_col) == 2: 
            row = start_row 
            if end_col == 6:  # Kingside
                board_obj.board[row][5] = color[0] + 'R' 
                board_obj.board[row][7] = '  ' if (row + 7) % 2 == 0 else '##' 
            elif end_col == 2:  # Queenside
                board_obj.board[row][3] = color[0] + 'R' 
                board_obj.board[row][0] = '  ' if (row + 0) % 2 == 0 else '##' 
            board_obj.castling_rights[color]['K'] = False 
            board_obj.castling_rights[color]['Q'] = False 
    # Save board state
    board_obj.history.append(copy.deepcopy(board_obj.board)) 

    # === En Passant Capture ===
    if piece[1] == 'P' and (end_row, end_col) == board_obj.en_passant_target:
        board_obj.board[start_row][end_col] = '  ' if (start_row + end_col) % 2 == 0 else '##'  # Remove captured pawn

    # Move the piece
    board_obj.board[end_row][end_col] = piece 
    board_obj.board[start_row][start_col] = '  ' if (start_row + start_col) % 2 == 0 else '##' 

    # === Promotion ===
    if piece[1] == 'P':
        if (color == "white" and end_row == 0) or (color == "black" and end_row == 7):
            board_obj.board[end_row][end_col] = color[0] + 'Q'

    # === Set En Passant Target ===
    if piece[1] == 'P' and abs(end_row - start_row) == 2:
        board_obj.en_passant_target = ((start_row + end_row) // 2, start_col)
    else:
        board_obj.en_passant_target = None

    return True
