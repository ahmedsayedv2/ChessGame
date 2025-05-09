from move_logic import handle_move

class Board:
    def __init__(self):
        self.board = self.create_initial_board()
        self.history = []
        self.en_passant_target = None
        self.castling_rights = {
            'white': {'K': True, 'Q': True},
            'black': {'K': True, 'Q': True}
        }
        self.en_passant_target = None  # Set to (row, col) if en passant is possible

    def create_initial_board(self):
        return [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['  ', '##', '  ', '##', '  ', '##', '  ', '##'],
            ['##', '  ', '##', '  ', '##', '  ', '##', '  '],
            ['  ', '##', '  ', '##', '  ', '##', '  ', '##'],
            ['##', '  ', '##', '  ', '##', '  ', '##', '  '],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]

    def move_piece(self, move, color):
        return handle_move(self, move, color)

    def get_all_legal_moves(self, color):
        from move_logic import get_piece_moves
        legal_moves = []
        for start_row in range(8):
            for start_col in range(8):
                piece = self.board[start_row][start_col]
                if piece.strip() == '' or piece == '##':
                    continue
                if piece[0].lower() != color[0].lower():
                    continue
                for end_row in range(8):
                    for end_col in range(8):
                        start_pos = (start_row, start_col)
                        end_pos = (end_row, end_col)
                        if get_piece_moves(piece, self, start_pos, color, end_pos):
                            legal_moves.append((start_pos, end_pos))
        return legal_moves
