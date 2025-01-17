
import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* PathFinding Algorithm")

RED = (255, 0, 0)          # already checked
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (0, 255, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)          # barrier
PURPLE = (128, 0, 128)     # choosen path
ORANGE = (255, 165, 0)     # start_node
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208) # end_node


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.width = width
        self.color = WHITE
        self.neighbors = []
        self.total_rows = total_rows
    
    def get_pos(self):
        return self.row, self.col
    
    def is_closed(self):
        return self.color == RED
    
    def is_open(self):
        return self.color == GREEN    

    def is_barrier(self):
        return self.color == BLACK  

    def is_start(self):
        return self.color == ORANGE    
    
    def is_end(self):
        return self.color == TURQUOISE    
    
    def reset(self):
        self.color = WHITE
    
    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE        

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))        

    def update_neighbors(self, grid):
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])                    
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])        
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])                  

    def __lt__(self, other):
        return False
    
# Heuristic function getting Manhattan Distance
# F[n] = G[n] + H[n]
# G[n] --> actual score of this node (cost to get to it)
# H[n] --> projected score to get from this node to end node
def h(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    return abs(x1 - x2) + abs(y1 - y2)

def make_grid(rows, width):
    grid = []
    gap = width // rows    
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap), (width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))        


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)

    pygame.display.update()

def get_clicked_position(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col

def reconstruct_path(came_from, start, current, draw):
    while current != start:
        current = came_from[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))   # f_score, count(tie breaker), starting point
    came_from = {}

    g_score = {spot : float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot : float("inf") for row in grid for spot in row}
    f_score[start] = g_score[start] + h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)
        
        if current == end:
            reconstruct_path(came_from, start, end, lambda: draw)
            start.make_start()
            end.make_end()
            return True
            #pass # track back path from came_from

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                count += 1
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = g_score[neighbor] + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
                    came_from[neighbor] = current

        draw()

        if current != start:
            neighbor.make_closed()

    return False

def main(win, width):
    ROWS = 50
    start = None
    end = None

    grid = make_grid(ROWS, width)
    started = False
    finished = True
    running = True
    while running:
        draw(WIN, grid, ROWS, width)
        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                start = None
                end = None
                grid = make_grid(ROWS, width)
            
            if started:
                continue

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, ROWS, width)
                spot = grid[row][col]
                if start == None and end == None:
                    start = spot
                    spot.make_start()
                elif end == None and start != None and spot != start:
                    end = spot
                    spot.make_end()
                else:
                    # check if this square in not start or destination,
                    # if not then can be selected as barrier
                    if spot != start and spot != end: 
                        spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    if end != None:
                        start = end
                        end.make_start()
                        end = None
                    else: 
                        start = None
                elif spot == end:
                    end = None
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start != None and end != None:
                    started = True
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    found_path = algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
                    print(found_path)
                    finished = True


    pygame.quit()

main(WIN, WIDTH)