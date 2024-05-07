import pygame, sys
from pygame.locals import *

WINDOW_SIZE = (256, 256)

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
pygame.display.set_caption("Levels Maker")


clock = pygame.time.Clock()

w, h = 16, 16

game_map = [[0 for x in range(w)] for y in range(h)]

def draw_cell_rect(cell_x, cell_y):
    x = cell_x * 16
    y = cell_y * 16
    rect = pygame.Rect(x, y, 16, 16)
    pygame.draw.rect(screen, (255, 0, 0), rect)

while True:
    screen.fill((146,244,255))
    
    #Draw Tile map
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == 1:
                pygame.draw.rect(screen, (0,0,0),pygame.Rect(x*16,y*16,16,16))
            x += 1
        y += 1
    #Mouse
    mx,my = pygame.mouse.get_pos()
    cell_x = mx // 16
    cell_y = my // 16
    draw_cell_rect(cell_x, cell_y)
    #----------------
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                game_map[cell_y][cell_x] = 1
            if event.button == 3:
                game_map[cell_y][cell_x] = 0
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_s:
                with open('level.dat','w') as file:
                    for row in game_map:
                        row_str = [str(element) for element in row]
                        row_txt = ''.join(row_str)
                        file.write(row_txt+'\n')
    pygame.display.update()
    clock.tick(60)
