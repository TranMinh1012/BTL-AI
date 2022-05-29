from cgitb import small
import copy
import sys
import pygame
import random
import numpy as np
from tkinter import Scale, messagebox
from audio import *
from pygame import mixer

# --- PYGAME SETUP ---

WIDTH = 600
HEIGHT = 600

ROWS = 3
COLS = 3
SQSIZE = WIDTH // COLS

LINE_WIDTH = 15
CIRC_WIDTH = 15
CROSS_WIDTH = 20

RADIUS = SQSIZE // 4

OFFSET = 50

# --- COLORS ---

BG_COLOR = (255, 195, 195)  #background
LINE_COLOR = (255, 254, 183) #đường viền X O
CIRC_COLOR = (243, 36, 36)
CROSS_COLOR = (77, 119, 255) #X O

pygame.init()
x_score = 0
o_score = 0

screen = pygame.display.set_mode ((WIDTH, HEIGHT) )
pygame.display.set_caption('CARO 3x3')
BG = pygame.image.load("image/images.jpg")

class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

# --- CLASSES ---

class Board:

    def __init__(self):
        self.squares = np.zeros( (ROWS, COLS) )
        self.empty_sqrs = self.squares # [squares]
        self.marked_sqrs = 0

    def final_state(self, show=False):
        '''
            @return 0 if there is no win yet
            @return 1 if player 1 wins
            @return 2 if player 2 wins
        '''

        # vertical wins
        for col in range(COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[0][col] == 2 else CROSS_COLOR
                    iPos = (col * SQSIZE + SQSIZE // 2, 20)
                    fPos = (col * SQSIZE + SQSIZE // 2, HEIGHT - 20)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[0][col]

        # horizontal wins
        for row in range(ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = CIRC_COLOR if self.squares[row][0] == 2 else CROSS_COLOR
                    iPos = (20, row * SQSIZE + SQSIZE // 2)
                    fPos = (WIDTH - 20, row * SQSIZE + SQSIZE // 2)
                    pygame.draw.line(screen, color, iPos, fPos, LINE_WIDTH)
                return self.squares[row][0]

        # desc diagonal
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, 20)
                fPos = (WIDTH - 20, HEIGHT - 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        # asc diagonal
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = CIRC_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                iPos = (20, HEIGHT - 20)
                fPos = (WIDTH - 20, 20)
                pygame.draw.line(screen, color, iPos, fPos, CROSS_WIDTH)
            return self.squares[1][1]

        # no win yet
        return 0

    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        empty_sqrs = []
        for row in range(ROWS):
            for col in range(COLS):
                if self.empty_sqr(row, col):
                    empty_sqrs.append( (row, col) )
        
        return empty_sqrs

    def isfull(self):
        if self.marked_sqrs == 9 :
            return self.marked_sqrs

    def isempty(self):
        if self.empty_sqrs == 0 :
            return self.marked_sqrs

class AI:

    def __init__(self, level=1, player=2):
        self.level = level
        self.player = player

    # --- RANDOM ---

    def rnd(self, board):
        empty_sqrs = board.get_empty_sqrs()
        idx = random.randrange(0, len(empty_sqrs))

        return empty_sqrs[idx] # (row, col)

    # --- MINIMAX ---

    def minimax(self, board, maximizing):
        
        # terminal case
        case = board.final_state()

        # player 1 wins
        if case == 1:
            return 1, None # eval, move

        # player 2 wins
        if case == 2:
            return -1, None

        # draw
        elif board.isfull():
            return 0, None

        if maximizing:
            max_eval = -100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)

            return max_eval, best_move

        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)

            return min_eval, best_move

    # --- MAIN EVAL ---

    def eval(self, main_board):
        if self.level == 0:
            # random choice
            eval = 'random'
            move = self.rnd(main_board)
        else:
            # minimax algo choice
            eval, move = self.minimax(main_board, False)

        return move # row, col

class Game:

    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.player = 1   #1-cross  #2-circles
        self.running = True
        self.show_lines()

    # --- DRAW METHODS ---

    def show_lines(self):
        # bg
        screen.fill( BG_COLOR )

        # vertical
        pygame.draw.line(screen, LINE_COLOR, (SQSIZE, 0), (SQSIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (WIDTH - SQSIZE, 0), (WIDTH - SQSIZE, HEIGHT), LINE_WIDTH)

        # horizontal
        pygame.draw.line(screen, LINE_COLOR, (0, SQSIZE), (WIDTH, SQSIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (0, HEIGHT - SQSIZE), (WIDTH, HEIGHT - SQSIZE), LINE_WIDTH)

    def draw_fig(self, row, col):
        if self.player == 1:
            # draw cross
            # desc line
            start_desc = (col * SQSIZE + OFFSET, row * SQSIZE + OFFSET)
            end_desc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH)
            # asc line
            start_asc = (col * SQSIZE + OFFSET, row * SQSIZE + SQSIZE - OFFSET)
            end_asc = (col * SQSIZE + SQSIZE - OFFSET, row * SQSIZE + OFFSET)
            pygame.draw.line(screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH)
        
        elif self.player == 2:
            # draw circle
            center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
            pygame.draw.circle(screen, CIRC_COLOR, center, RADIUS, CIRC_WIDTH)

    # --- OTHER METHODS ---

    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()

    def next_turn(self):
        self.player = self.player % 2 + 1


    def isover(self):
        if self.board.isfull() == 9 :
            return 9;
        return self.board.final_state(show=True);
            

    def reset(self):
        self.__init__()

def options():
    screen = pygame.display.set_mode ((1000, 520) )
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        screen.fill("white")
        
        MENU_TEXT = get_font(50).render("HOW TO PLAY",True ,"#E60965")
        MENU_RECT = MENU_TEXT.get_rect(center=(500,40))
        screen.blit(MENU_TEXT,MENU_RECT)
        filename = ("text_help/how_to_play.txt")
        i=100
        with open(filename) as f:
            for line in f:
                OPTIONS_TEXT = get_font(20).render(line, True, "#15133C")
                OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(500, i))
                i = i+30
                screen.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(500, 480), 
                            text_input="BACK", font=get_font(30), base_color="#15133C", hovering_color="#D18CE0")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    screen = pygame.display.set_mode ((WIDTH, HEIGHT) )
                    main()

        pygame.display.update()
        
def main():
    audio_music("Josefina")
    while True:
        screen.fill( BG_COLOR)
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        MENU_TEXT = get_font(50).render("MAIN MENU",True ,"#FFFF00")
        MENU_RECT = MENU_TEXT.get_rect(center=(300,100))
        PLAY_BUTTON = Button(image=pygame.image.load("image/Play Rect.png"), pos =(300,200), 
                            text_input="PLAY", font = get_font(40), base_color = "#F0D9FF", hovering_color ="#77D970")
        OPTIONS_BUTTON = Button(image=pygame.image.load("image/Options Rect.png"), pos =(300,300), 
                                text_input="HOW TO PLAY", font = get_font(40), base_color = "#F0D9FF", hovering_color ="#77D970")
        QUIT_BUTTON = Button(image=pygame.image.load("image/Quit Rect.png"), pos =(300,400), 
                            text_input="QUIT", font = get_font(40), base_color = "#F0D9FF", hovering_color ="#77D970")
        # Mute sound
        mute_music=pygame.image.load("image/Mute Music.png")
        mute_music=pygame.transform.scale(mute_music, (40, 40))
        MUTE_BUTTON = Button(mute_music, pos =(560,50),
            text_input="", font = get_font(40), base_color = "#F0D9FF", hovering_color ="#77D970")

        # Unmute sound
        unmute_music=pygame.image.load("image/Unmute Music.png")
        unmute_music=pygame.transform.scale(unmute_music, (40, 40))
        UNMUTE_BUTTON = Button(unmute_music, pos =(490,50),
            text_input="", font = get_font(40), base_color = "#F0D9FF", hovering_color ="#77D970")
        screen.blit(MENU_TEXT,MENU_RECT)
        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON, MUTE_BUTTON, UNMUTE_BUTTON] :
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    gamemode()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()
                if MUTE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    stop_music()
                if UNMUTE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play_music()
                    
        pygame.display.update()
 
def get_font(size): # Returns Press-Start-2P in the desired size
    return pygame.font.Font("image/font_bold.otf", size)
def notification(check,x_score,o_score,mode) :
    audio_music("end game")
    msg=""
    score=f'X score | {x_score}   -   {o_score} | O score'
    while True:
        NOTI_MOUSE_POS = pygame.mouse.get_pos()
        screen.fill(BG_COLOR)
        if check == 1 :
            msg = "X is Winner"
        elif check == 2 :
            msg = "O is Winner"
        elif check ==9:
            msg = "Game is Tie"
        
        NOTI_TEXT = get_font(45).render(msg, True, "#5C7AEA")
        NOTI_RECT = NOTI_TEXT.get_rect(center=(300, 100))
        screen.blit(NOTI_TEXT, NOTI_RECT)
        
        SCORE_TEXT =  get_font(45).render(score, True, "#5C7AEA")
        SCORE_RECT = SCORE_TEXT.get_rect(center=(300, 200))
        screen.blit(SCORE_TEXT, SCORE_RECT)
        
        NOTI_BACK = Button(image=None, pos=(300, 450), 
                        text_input="BACK", font=get_font(45), base_color="Black", hovering_color="#F32424")

        NOTI_BACK.changeColor(NOTI_MOUSE_POS)
        NOTI_BACK.update(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if NOTI_BACK.checkForInput(NOTI_MOUSE_POS):
                    stop_music()
                    audio_music("Letgo_music")
                    play(x_score,o_score,mode)

        pygame.display.update()
        
def gamemode():
    audio_music("Are you ready")
    while True:
        MODE_MOUSE_POS = pygame.mouse.get_pos()
        screen.fill(BG_COLOR)
        
        PLAY_TEXT = get_font(50).render("ARE YOU READY ?",True ,"#FFFF00")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(300,100))
        screen.blit(PLAY_TEXT, PLAY_RECT)

        # PLAY_PVP = Button(image=pygame.image.load("image/Play Rect.png"), pos =(300,200), 
        #                     text_input="PVP", font = get_font(40), base_color = "#F0D9FF", hovering_color ="#BFA2DB")
        
        PLAY_PVB = Button(image=pygame.image.load("image/Play Rect.png"), pos =(300,300), 
                            text_input="YES", font = get_font(40), base_color = "#F0D9FF", hovering_color ="#77D970")
        
        PLAY_BACK = Button(image=pygame.image.load("image/Play Rect.png"), pos=(300, 450), 
                            text_input="NO", font=get_font(40), base_color="#F0D9FF", hovering_color="#77D970")
        for button in [ PLAY_PVB, PLAY_BACK]: 
            button.changeColor(MODE_MOUSE_POS)
            button.update(screen)
        x_score = 0
        o_score = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # if PLAY_PVP.checkForInput(MODE_MOUSE_POS):
                #     play(x_score,o_score,'pvp')
                if PLAY_PVB.checkForInput(MODE_MOUSE_POS):
                    audio_music("Letgo_music")
                    play(x_score,o_score,'ai')
                if PLAY_BACK.checkForInput(MODE_MOUSE_POS):
                    main()

        pygame.display.update()

def play(x_score,o_score,mode):
    game = Game()
    board = game.board
    ai = game.ai
    # --- MAINLOOP ---

    while True:
        # pygame events
        check = 0
        for event in pygame.event.get():

            # quit event
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # keydown event
            if event.type == pygame.KEYDOWN:
                #b-back 
                if event.key == pygame.K_b:
                    gamemode()

                # 0-random ai
                if event.key == pygame.K_0:
                    ai.level = 0
                
                # 1-random ai
                if event.key == pygame.K_1:
                    ai.level = 1

            # click event
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                row = pos[1] // SQSIZE
                col = pos[0] // SQSIZE
                
                # human mark sqr
                if board.empty_sqr(row, col) and game.running:
                    game.make_move(row, col)
                    if game.isover() == 1 :
                        check = 1
                        x_score = x_score + 1
                        game.running = False
                    elif game.isover()== 2:
                        check = 2
                        o_score = o_score + 1
                        game.running = False
                    elif game.isover()== 9 :
                        check = 9
                        o_score = o_score + 1
                        x_score = x_score + 1
                        game.running = False


        # AI initial call
        if mode == 'ai' and game.player == ai.player and game.running:

            # update the screen
            pygame.display.update()

            # eval
            row, col = ai.eval(board)
            game.make_move(row, col)
            if game.isover() == 1 :
                check = 1
                x_score = x_score + 1
                game.running = False
            elif game.isover() == 2:
                check = 2
                o_score = o_score + 1
                game.running = False
            elif game.isover()== 9 :
                check = 9
                o_score = o_score + 1
                x_score = x_score + 1
                game.running = False
        pygame.display.update()
        if check != 0:
            notification(check,x_score,o_score,mode)


main()
