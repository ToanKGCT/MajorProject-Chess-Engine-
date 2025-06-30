import pygame, chess, chess.engine, sys

pygame.init()
engine = chess.engine.SimpleEngine.popen_uci("Pretrained AI/stockfish-windows-x86-64-avx2.exe")
board = chess.Board()
screen = pygame.display.set_mode((640, 640))
size = 640
square_size = size // 8
pygame.display.set_caption("Tri's Chess")

def pause_with_message(screen, message):
    font = pygame.font.SysFont(None, 48)
    text = font.render(message, True, (255, 0, 0))
    rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text, rect)
    pygame.display.flip()
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                paused = False
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                paused = False


def ask_promotion(screen, color):
    options = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
    piece_syms = ['q', 'r', 'b', 'n'] if color == chess.BLACK else ['Q', 'R', 'B', 'N']
    w, h = 60, 60
    x0 = screen.get_width() // 2 - 2 * w
    y0 = screen.get_height() // 2 - h // 2
    rects = []
    for i, sym in enumerate(piece_syms):
        rect = pygame.Rect(x0 + i * (w + 10), y0, w, h)
        pygame.draw.rect(screen, (200, 200, 200), rect)
        img = piece_images[sym]
        bbox = img.get_bounding_rect()
        # Center the visible part of the image in the rect
        img_x = rect.x + (rect.width - bbox.width) // 2 - bbox.x
        img_y = rect.y + (rect.height - bbox.height) // 2 - bbox.y
        screen.blit(img, (img_x, img_y), area=bbox)
        rects.append(rect)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mx, my):
                        return options[i]

def load_and_scale(path):
    img = pygame.image.load(path)
    return pygame.transform.scale(img, (square_size, square_size))

white_pawn   = load_and_scale("Book Diagram/wp.svg")
white_king   = load_and_scale("Book Diagram/wk.svg")
white_horse  = load_and_scale("Book Diagram/wn.svg")
white_queen  = load_and_scale("Book Diagram/wq.svg")
white_rook   = load_and_scale("Book Diagram/wr.svg")
white_bishop = load_and_scale("Book Diagram/wb.svg")

black_pawn   = load_and_scale("Book Diagram/bp.svg")
black_bishop = load_and_scale("Book Diagram/bb.svg")
black_king   = load_and_scale("Book Diagram/bk.svg")
black_horse  = load_and_scale("Book Diagram/bn.svg")
black_queen  = load_and_scale("Book Diagram/bq.svg")
black_rook   = load_and_scale("Book Diagram/br.svg")

# Load other piece images the same way...

# Colors
light = (240, 217, 181)  # Light squares
dark = (181, 136, 99)    # Dark squares

piece_images = {
    'P': white_pawn,
    'N': white_horse,
    'B': white_bishop,
    'R': white_rook,
    'Q': white_queen,
    'K': white_king,
    'p': black_pawn,
    'n': black_horse,
    'b': black_bishop,
    'r': black_rook,
    'q': black_queen,
    'k': black_king,
}

dragging = False
dragged_piece = None
dragged_from = None
mouse_x, mouse_y = 0, 0
invalid_reason = ""


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            col = mx // square_size
            row = 7 - (my // square_size)
            square = chess.square(col, row)
            piece = board.piece_at(square)
            if piece and ((board.turn and piece.color) or (not board.turn and not piece.color)):
                dragging = True
                dragged_piece = piece
                dragged_from = square
                mouse_x, mouse_y = mx, my
        elif event.type == pygame.MOUSEBUTTONUP and dragging:
            mx, my = pygame.mouse.get_pos()
            col = mx // square_size
            row = 7 - (my // square_size)
            to_square = chess.square(col, row)
            move = chess.Move(dragged_from, to_square)
            # Check for promotion
            promotion = None
            if (dragged_piece.piece_type == chess.PAWN and
                (chess.square_rank(to_square) == 0 or chess.square_rank(to_square) == 7)):
                promotion = ask_promotion(screen, dragged_piece.color)
                move = chess.Move(dragged_from, to_square, promotion=promotion)
            # Use pseudo-legal moves to allow king capture
            if move in board.generate_pseudo_legal_moves():
                board.push(move)
                board_fen = board.board_fen()
                if 'K' not in board_fen:
                    invalid_reason = "Black wins! White king captured."
                    running = False
                    break
                elif 'k' not in board_fen:
                    invalid_reason = "White wins! Black king captured."
                    running = False
                    break
                else:
                    invalid_reason = ""

                if running and not board.is_game_over() and 'K' in board.board_fen() and 'k' in board.board_fen():
                    try:
                        result = engine.play(board, chess.engine.Limit(time=0.1))
                        board.push(result.move)
                        board_fen = board.board_fen()
                        if 'K' not in board_fen:
                            invalid_reason = "Black wins! White king captured."
                            running = False
                            break
                        elif 'k' not in board_fen:
                            invalid_reason = "White wins! Black king captured."
                            running = False
                            break
                        else:
                            invalid_reason = ""
                    except Exception as e:
                        invalid_reason = "Engine error: " + str(e)
                        running = False
                        break
            else:
                invalid_reason = "Invalid move!"
            dragging = False
            dragged_piece = None
            dragged_from = None
        elif event.type == pygame.MOUSEMOTION and dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()

    # Draw chessboard
    for row in range(8):
        for col in range(8):
            color = light if (row + col) % 2 == 0 else dark
            pygame.draw.rect(screen, color, (col * square_size, row * square_size, square_size, square_size))

    # Draw pieces
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            # Don't draw the piece being dragged on the board
            if dragging and square == dragged_from:
                continue
            img = piece_images[piece.symbol()]
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)
            bbox = img.get_bounding_rect()
            x = col * square_size + (square_size - bbox.width) // 2
            y = row * square_size + (square_size - bbox.height) // 2
            screen.blit(img, (x, y), area=bbox)

    # Draw the dragged piece following the mouse
    if dragging and dragged_piece:
        img = piece_images[dragged_piece.symbol()]
        bbox = img.get_bounding_rect()
        x = mouse_x - bbox.width // 2
        y = mouse_y - bbox.height // 2
        screen.blit(img, (x, y), area=bbox)

    # Show notification
    pygame.display.flip()


engine.quit()
pygame.quit()
