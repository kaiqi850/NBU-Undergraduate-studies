import random
import sys
import pygame

to_be_selected = []
random_selectB = []
path_list = []
ROWS = 50
COLUMNS = 50
x = [0, 2, 0, -2]
y = [2, 0, -2, 0]
px = [0, 1, 0, -1]
py = [1, 0, -1, 0]
isvisit = [[0 for i in range(COLUMNS)] for j in range(ROWS)]
isvisit[1][1] = 1


def matrix_init(r, c):
    matrix = [[1 for i in range(c)] for j in range(r)]
    matrix[1][1] = 0
    return matrix


def put_node_in_to_be_selected(node):
    for i in range(4):
        xx = node[0] + x[i]
        yy = node[1] + y[i]
        if xx > 0 and xx < ROWS and yy > 0 and yy < COLUMNS and ([xx, yy] not in to_be_selected) and matrix[xx][
            yy] == 1:
            to_be_selected.append([xx, yy])


matrix = matrix_init(ROWS, COLUMNS)


def random_B(node):
    random_selectB.clear()
    for i in range(4):
        xx = node[0] + x[i]
        yy = node[1] + y[i]
        if xx > 0 and xx < ROWS and yy > 0 and yy < COLUMNS and matrix[xx][yy] == 0:
            random_selectB.append([xx, yy])
    rand_B = random.randint(0, len(random_selectB) - 1)
    return random_selectB[rand_B]


start = [1, 1]
put_node_in_to_be_selected(start)
path_list.append([1, 1])


def matrix_generate():
    if len(to_be_selected) > 0:
        rand_s = random.randint(0, len(to_be_selected) - 1)
        select_nodeA = to_be_selected[rand_s]
        selectB = random_B(select_nodeA)
        matrix[select_nodeA[0]][select_nodeA[1]] = 0
        mid_x = int((select_nodeA[0] + selectB[0]) / 2)
        mid_y = int((select_nodeA[1] + selectB[1]) / 2)
        matrix[mid_x][mid_y] = 0
        put_node_in_to_be_selected(select_nodeA)
        to_be_selected.remove(select_nodeA)
    elif len(path_list) > 0:
        matrix[ROWS - 2][COLUMNS - 2] = 3
        l = len(path_list) - 1
        n = path_list[l]
        if n[0] == ROWS - 2 and n[1] == COLUMNS - 2:
            return
        for i in range(4):
            xx = n[0] + px[i]
            yy = n[1] + py[i]
            if xx > 0 and xx < ROWS - 1 and yy > 0 and yy < COLUMNS - 1 and (
                    matrix[xx][yy] == 0 or matrix[xx][yy] == 3) and isvisit[xx][yy] == 0:
                isvisit[xx][yy] = 1
                matrix[n[0]][n[1]] = 2
                tmp = [xx, yy]
                path_list.append(tmp)
                break
            elif i == 3:
                matrix[n[0]][n[1]] = 0
                path_list.pop()


pygame.init()
screen = pygame.display.set_mode((COLUMNS * 15, ROWS * 15))
pygame.display.set_caption("生成迷宫地图")


def draw_rect(x, y, color):
    pygame.draw.rect(screen, color, ((y * 15, x * 15, 15, 15)))


def draw_maze():
    for i in range(ROWS):
        for j in range(COLUMNS):
            if matrix[i][j] == 1:
                draw_rect(i, j, "grey")
            if matrix[i][j] == 2:
                draw_rect(i, j, "green")
            if matrix[i][j] == 3:
                draw_rect(i, j, "red")


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill("white")
    matrix_generate()
    draw_maze()
    pygame.display.flip()
    pygame.time.Clock().tick(60)