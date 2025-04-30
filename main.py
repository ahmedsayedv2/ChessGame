import board
from utils import switch_turn
import copy
from move_validation import get_piece_moves
from checkmate_logic import is_checkmate, is_stalemate
from ai import get_ai_move


def main():
    game = board.Board()
    current_turn = 'white'
    player_mode = input("Play against (1) Human or (2) Computer? ")

    while True:
        print_board(game.board)

        if player_mode == '2' and current_turn == 'black':

            print("Computer is thinking...")
            move = get_ai_move(game, current_turn)
            if move:
                start_pos, end_pos = move
                game.move_piece(move, current_turn)

                if is_checkmate(game, switch_turn(current_turn)):
                    print(f"{switch_turn(current_turn)} is checkmated!")
                    break
                current_turn = switch_turn(current_turn)
            else:
                print("Computer couldn't find a valid move!")
                break
        else:

            move_input = input(f"{current_turn}'s move (format: start_row start_col end_row end_col): ")

            try:
                start_row, start_col, end_row, end_col = map(int, move_input.split())
                piece = game.board[start_row - 1][start_col - 1]

                if get_piece_moves(piece, game, (start_row - 1, start_col - 1), current_turn,
                                   (end_row - 1, end_col - 1)):
                    success = game.move_piece(((start_row - 1, start_col - 1), (end_row - 1, end_col - 1)),
                                              current_turn)

                    if success:
                        if is_checkmate(game, switch_turn(current_turn)):
                            print_board(game.board)
                            print(f"{switch_turn(current_turn)} is checkmated!")
                            break
                        current_turn = switch_turn(current_turn)
                    else:
                        print("Invalid move")
                else:
                    print("Invalid move!")
            except Exception as e:
                print(f"Error: {e}")


def print_board(board):
    print('\n   ' + ' '.join([f'{i + 1} ' for i in range(8)]))
    for i, row in enumerate(board):
        print(f'{i + 1}  ' + ' '.join(row))
    print()


if __name__ == "__main__":
    main()