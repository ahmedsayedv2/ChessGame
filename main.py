import pygame 
from board import Board 
from ai import get_ai_move 
from checkmate_logic import is_checkmate, is_stalemate 
 
# Constants 
WIDTH, HEIGHT = 600, 490 
SIDE_PANEL_WIDTH = 160 
SQ_SIZE = (WIDTH - SIDE_PANEL_WIDTH) // 8 
MAX_FPS = 15 
PANEL_HEIGHT = 48 
MAX_VISIBLE_MOVES = (HEIGHT - PANEL_HEIGHT) // 20 
 
# Initialize Pygame 
pygame.init() 
screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("Chess") 
clock = pygame.time.Clock() 
font = pygame.font.SysFont("Arial", 24) 
 
# Load images 
IMAGES = {} 
pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK'] 
 
def load_images(): 
    for piece in pieces: 
        IMAGES[piece] = pygame.transform.scale( 
            pygame.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE) 
        ) 
 
def pos_to_algebraic(pos): 
    row, col = pos 
    return chr(col + ord('a')) + str(8 - row) 
 
def draw_board(screen): 
    colors = [pygame.Color("white"), pygame.Color("dodgerblue4")] 
    for r in range(8): 
        for c in range(8): 
            color = colors[(r + c) % 2] 
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)) 
 
def draw_pieces(screen, board): 
    for r in range(8): 
        for c in range(8): 
            piece = board[r][c] 
            if piece in IMAGES: 
                screen.blit(IMAGES[piece], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)) 
 
def draw_status_bar(screen, text): 
    pygame.draw.rect(screen, pygame.Color("dodgerblue4"), pygame.Rect(0, HEIGHT - PANEL_HEIGHT, WIDTH, PANEL_HEIGHT)) 
    label = font.render(text, True, pygame.Color("white")) 
    screen.blit(label, (10, HEIGHT - PANEL_HEIGHT + 10)) 
 
def draw_loading_screen(): 
    screen.fill(pygame.Color("dodgerblue4")) 
    loading_font = pygame.font.SysFont("Arial", 36) 
    loading_label = loading_font.render("Loading...", True, pygame.Color("white")) 
    screen.blit(loading_label, (WIDTH // 3, HEIGHT // 2)) 
    pygame.display.flip() 
    pygame.time.delay(1500) 
 
def draw_main_menu(): 
    screen.fill(pygame.Color("dodgerblue4")) 
    title_label = font.render("Chess Game", True, pygame.Color("black")) 
    screen.blit(title_label, (WIDTH / 2.55, HEIGHT // 2.5 - 40)) 
 
    pvp_button = pygame.Rect(WIDTH // 3, HEIGHT // 2 - 40, 200, 50) 
    pygame.draw.rect(screen, pygame.Color("white"), pvp_button) 
    pvp_label = font.render("Player vs Player", True, pygame.Color("black")) 
    screen.blit(pvp_label, (pvp_button.x + 20, pvp_button.y + 10)) 
 
    pve_button = pygame.Rect(WIDTH // 3, HEIGHT // 2 + 20, 200, 50) 
    pygame.draw.rect(screen, pygame.Color("white"), pve_button) 
    pve_label = font.render("Player vs AI", True, pygame.Color("black")) 
    screen.blit(pve_label, (pve_button.x + 40, pve_button.y + 10)) 
 
    pygame.display.flip() 
    return pvp_button, pve_button 
 
def display_winner(screen, winner): 
    font = pygame.font.SysFont("Arial", 48) 
    message = f"Checkmate! {winner} Wins!" 
    text_surface = font.render(message, True, (255, 0, 0)) 
    screen.blit(text_surface, (WIDTH // 6, HEIGHT // 3 - 40)) 
 
    play_again_btn = pygame.Rect(WIDTH // 3, HEIGHT // 2 + 30, 200, 50) 
    pygame.draw.rect(screen, pygame.Color("white"), play_again_btn) 
    btn_label = font.render("Play Again", True, pygame.Color("black")) 
    screen.blit(btn_label, (play_again_btn.x + 10, play_again_btn.y + 5)) 
    pygame.display.flip() 
    return play_again_btn 

def display_stalemate(screen): 
    font = pygame.font.SysFont("Arial", 48) 
    message = "Stalemate! It's a Draw!" 
    text_surface = font.render(message, True, (255, 255, 0)) 
    screen.blit(text_surface, (WIDTH // 6, HEIGHT // 3 - 40)) 
 
    play_again_btn = pygame.Rect(WIDTH // 3, HEIGHT // 2 + 30, 200, 50) 
    pygame.draw.rect(screen, pygame.Color("white"), play_again_btn) 
    btn_label = font.render("Play Again", True, pygame.Color("black")) 
    screen.blit(btn_label, (play_again_btn.x + 10, play_again_btn.y + 5)) 
    pygame.display.flip() 
    return play_again_btn 

def draw_coordinates(screen):
    font = pygame.font.SysFont("Arial", 18)

    # Draw row numbers on the left side
    for row in range(8):
        row_label = font.render(str(8 - row), True, pygame.Color("black"))
        screen.blit(row_label, (5, row * SQ_SIZE + SQ_SIZE // 3))

    # Draw column letters on top of the board
    for col in range(8):
        label = font.render(chr(col + ord('a')), True, pygame.Color("black"))
        x = col * SQ_SIZE + SQ_SIZE  - label.get_width() -1
        y = 5  # 5 pixels from top
        screen.blit(label, (x, y))

 
def draw_move_history(screen, moves): 
    pygame.draw.rect(screen, pygame.Color("gainsboro"), 
                     pygame.Rect(WIDTH - SIDE_PANEL_WIDTH, 0, SIDE_PANEL_WIDTH, HEIGHT - PANEL_HEIGHT)) 
    move_font = pygame.font.SysFont("Arial", 18) 
    recent_moves = moves[-MAX_VISIBLE_MOVES:] 
    for i, move in enumerate(recent_moves): 
        move_text = move_font.render(move, True, pygame.Color("black")) 
        screen.blit(move_text, (WIDTH - SIDE_PANEL_WIDTH + 10, 20 + i * 20)) 
 
def main(): 
    draw_loading_screen() 
    load_images() 
    game_running = True 
 
    while game_running: 
        board_obj = Board() 
        running = True 
        selected_sq = None 
        player_clicks = [] 
        last_move_str = "" 
        current_turn = "white" 
        game_mode = None 
        move_history = [] 
 
        while running: 
            if game_mode is None: 
                pvp_button, pve_button = draw_main_menu() 
                for e in pygame.event.get(): 
                    if e.type == pygame.QUIT: 
                        running = False 
                        game_running = False 
                    if e.type == pygame.MOUSEBUTTONDOWN: 
                        x, y = pygame.mouse.get_pos() 
                        if pvp_button.collidepoint(x, y): 
                            game_mode = "pvp" 
                        elif pve_button.collidepoint(x, y): 
                            game_mode = "pve" 
            else: 
                for e in pygame.event.get(): 
                    if e.type == pygame.QUIT: 
                        running = False 
                        game_running = False 
                    elif e.type == pygame.MOUSEBUTTONDOWN: 
                        x, y = pygame.mouse.get_pos() 
                        if y < HEIGHT - PANEL_HEIGHT: 
                            col = x // SQ_SIZE 
                            row = y // SQ_SIZE 
                            square = (row, col) 
                            if selected_sq == square: 
                                selected_sq = None 
                                player_clicks = [] 
                            else: 
                                selected_sq = square 
                                player_clicks.append(square) 
                            if len(player_clicks) == 2: 
                                start, end = player_clicks 
                                piece = board_obj.board[start[0]][start[1]] 
                                if piece.strip() != '' and piece != '##' and piece[0].lower() == current_turn[0]: 
                                    success = board_obj.move_piece((start, end), current_turn) 
                                    if success: 
                                        move_str = f"{piece} from {pos_to_algebraic(start)} to {pos_to_algebraic(end)}" 
                                        move_history.append(move_str) 
                                        if len(move_history) > MAX_VISIBLE_MOVES: 
                                            move_history.pop(0) 
                                        current_turn = "black" if current_turn == "white" else "white" 
                                        last_move_str = move_str 
                                selected_sq = None 
                                player_clicks = [] 
 
                draw_board(screen) 
                draw_pieces(screen, board_obj.board) 
                draw_coordinates(screen) 
                draw_move_history(screen, move_history) 
                if selected_sq: 
                    s = pygame.Surface((SQ_SIZE, SQ_SIZE)) 
                    s.set_alpha(100) 
                    s.fill(pygame.Color('blue')) 
                    screen.blit(s, (selected_sq[1] * SQ_SIZE, selected_sq[0] * SQ_SIZE)) 
                draw_status_bar(screen, last_move_str) 
                clock.tick(MAX_FPS) 
                pygame.display.flip() 
 
                if game_mode == "pve" and current_turn == "black": 
                    pygame.time.delay(500) 
                    ai_move = get_ai_move(board_obj, "black") 
                    if ai_move: 
                        success = board_obj.move_piece(ai_move, "black") 
                        if success: 
                            ai_move_str = f"AI moved: {pos_to_algebraic(ai_move[0])} to {pos_to_algebraic(ai_move[1])}" 
                            move_history.append(ai_move_str) 
                            if len(move_history) > MAX_VISIBLE_MOVES: 
                                move_history.pop(0) 
                            current_turn = "white" 
                            last_move_str = ai_move_str 
 
                if is_checkmate(board_obj, current_turn): 
                    winner = "White" if current_turn == "black" else "Black" 
                    btn = display_winner(screen, winner) 
                    waiting = True 
                    while waiting: 
                        for e in pygame.event.get(): 
                            if e.type == pygame.QUIT: 
                                waiting = False 
                                running = False 
                                game_running = False 
                            elif e.type == pygame.MOUSEBUTTONDOWN: 
                                x, y = pygame.mouse.get_pos() 
                                if btn.collidepoint(x, y): 
                                    waiting = False 
                                    running = False 
                elif is_stalemate(board_obj, current_turn):
                    btn = display_stalemate(screen)
                    waiting = True
                    while waiting:
                        for e in pygame.event.get():
                            if e.type == pygame.QUIT:
                                waiting = False
                                running = False
                                game_running = False
                            elif e.type == pygame.MOUSEBUTTONDOWN:
                                x, y = pygame.mouse.get_pos()
                                if btn.collidepoint(x, y):
                                    waiting = False
                                    running = False 
 
    pygame.quit() 
 
if __name__ == "__main__": 
    main()
