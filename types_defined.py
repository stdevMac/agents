import random
from utils import *


class Cell:
    def __init__(self, allowed_move, x, y):
        self.allowed_to_move = allowed_move
        self.x = x
        self.y = y

    def can_be_moved(self, cell):
        return type(cell) in self.allowed_to_move

    def move(self, board):
        pass

    def __str__(self):
        return 'Cell'

    def swap(self, board, cell_to_swap):
        x, y = self.x, self.y
        self.x = cell_to_swap.x
        self.y = cell_to_swap.y
        board.board[cell_to_swap.x][cell_to_swap.y] = self
        cell_to_swap.x = x
        cell_to_swap.y = y
        board.board[x][y] = cell_to_swap


class Blank(Cell):
    def __str__(self):
        return '\N{white large square}'


class Obstacle(Cell):
    def __str__(self):
        return '\N{pine decoration}'

    pass


class Dirt(Cell):
    def __str__(self):
        return '\N{pile of poo}'


class Corral(Cell):
    def __init__(self, allowed_move, x, y):
        super().__init__(allowed_move, x, y)
        self.contains_child = False
        self.child = None
        self.contains_robot = False
        self.robot = None

    def move(self, board):
        if self.contains_robot:
            if self.robot.has_child_inside:
                board.board[self.x][self.y].robot.contains_child = False
                board.board[self.x][self.y].robot.child = None
            board.board[self.x][self.y].robot.move(board)
            self.contains_robot = False
            self.robot = None

    def __str__(self):
        if self.contains_child and self.contains_robot:
            return '\N{family}'
        if self.contains_robot:
            return '\N{ghost}'
        if self.contains_child:
            return '\N{baby symbol}'
        return '\N{bell}'

    def set_only_child(self, child):
        self.contains_child = True
        self.child = child
        self.contains_robot = False
        self.robot = None

    def set_robot(self, robot):
        self.contains_robot = True
        self.robot = robot
        if self.robot.contains_child:
            self.contains_child = True
            self.child = self.robot.child

    def clear(self):
        pass


class Child(Cell):
    def __init__(self, allowed_moves, x, y):
        super().__init__(allowed_moves, x, y)
        self.inside_corral = False
        self.walk_last_move = False

    def __str__(self):
        return '\N{baby}'

    def move(self, board):
        self.walk_last_move = False
        move_this_turn = random.randint(0, 150)
        if move_this_turn % 2 == 0:
            return
        rnd_dir = random.randint(0, len(DIRECTION) - 1)
        cell = board.get_cell(self.x + DIRECTION[rnd_dir][0], self.y + DIRECTION[rnd_dir][1])
        if isinstance(cell, Blank):
            self.swap(board, cell)
            self.walk_last_move = True
        if isinstance(cell, Obstacle):
            self.walk_last_move = self.move_with_obstacles(board, DIRECTION[rnd_dir], cell)

    def move_with_obstacles(self, board, direction, cell):
        obstacles = [self, cell]

        while True:
            cell = board.get_cell(self.x + direction[0], self.y + direction[1])
            if not isinstance(cell, Blank) or not isinstance(cell, Obstacle):
                return False
            if isinstance(cell, Obstacle):
                obstacles.append(cell)
            if isinstance(cell, Blank):
                while len(obstacles) > 0:
                    obstacles[len(obstacles) - 1].swap(board, cell)
                    obstacles.pop()
                return True

    def create_trash(self, board):
        dirs_child = []
        dirs_blanks = []
        for direction in FULL_DIRECTION:
            cell = board.get_cell(self.x + direction[0], self.y + direction[1])
            if isinstance(cell, Child):
                dirs_child.append((cell.x, cell.y))
            elif isinstance(cell, Blank):
                dirs_blanks.append((cell.x, cell.y))
        random.shuffle(dirs_blanks)
        max_trash_number = 0

        if len(dirs_child) == 0:
            max_trash_number = 1
        if len(dirs_child) == 1:
            max_trash_number = 3
        if len(dirs_child) >= 2:
            max_trash_number = 6
        trash_number = random.randint(0, max_trash_number)

        for i_blanks, _ in zip(dirs_blanks, [_ for _ in range(trash_number)]):
            x = i_blanks[0]
            y = i_blanks[1]
            board.board[x][y] = Dirt([], x, y)
        return min(len(dirs_blanks), trash_number)


class Robot(Cell):
    def __init__(self, allowed_move, x, y):
        super().__init__(allowed_move, x, y)
        self.contains_child = False
        self.child = None
        self.trash = None
        self.time_waiting = 0
        self.trash_eliminated = 0
        self.dfs_board = [[]]
        self.move_with_child = 0

    def drop_child(self):
        child = self.child
        self.child = None
        self.contains_child = False
        return child

    def has_child_inside(self):
        return self.contains_child

    def charge_child(self, child):
        if self.has_child_inside():
            return False
        self.contains_child = True
        self.child = child
        return True

    def clean_trash(self):
        self.trash_eliminated = 0
        if self.trash is None:
            return
        if self.time_waiting == 0:
            self.trash_eliminated = 1
            self.trash = None
            return
        self.time_waiting -= 1

    def __str__(self):
        return '\N{alien monster}'

    @staticmethod
    def bfs_without_search(board, node):
        queue = [board.board[node[0]][node[1]]]
        visited = [node]
        father = [[]] * board.m
        bot = board.board[node[0]][node[1]]
        for i in range(board.m):
            father[i] = [None] * board.n

        while queue:
            cell = queue.pop()

            if isinstance(cell, Dirt):
                x = cell.x
                y = cell.y
                while True:
                    f = father[x][y]
                    if f[0] == node[0] and f[1] == node[1]:
                        return x, y
                    x = f[0]
                    y = f[1]
            if isinstance(cell, Obstacle):
                continue
            if isinstance(cell, Corral):
                if cell.contains_child and bot.contains_child and cell.x != bot.x and cell.y != bot.y:
                    continue
            if isinstance(cell, Child):
                x = cell.x
                y = cell.y
                while True:
                    f = father[x][y]
                    if f[0] == node[0] and f[1] == node[1]:
                        return x, y
                    x = f[0]
                    y = f[1]
            for neighbour in board.get_adjacent(cell.x, cell.y):
                if (neighbour.x, neighbour.y) not in visited:
                    visited.append((neighbour.x, neighbour.y))
                    queue.insert(0, neighbour)
                    father[neighbour.x][neighbour.y] = (cell.x, cell.y)
        return None

    @staticmethod
    def bfs(board, node, search_type):
        queue = [board.board[node[0]][node[1]]]
        visited = [node]
        father = [[]] * board.m
        bot = board.robot
        for i in range(board.m):
            father[i] = [None] * board.n

        while queue:
            cell = queue.pop()

            if isinstance(cell, Dirt) and search_type != Dirt:
                continue
            if search_type != Child and isinstance(cell, Child):
                continue
            if isinstance(cell, Obstacle):
                continue
            if isinstance(cell, Corral):
                if Corral != search_type and (bot.contains_child or cell.contains_child):
                    continue
                if Corral == search_type and cell.contains_child:
                    continue

            if isinstance(cell, search_type):
                x = cell.x
                y = cell.y
                while True:
                    f = father[x][y]
                    if f is None:
                        return None
                    if f[0] == node[0] and f[1] == node[1]:
                        return x, y
                    x = f[0]
                    y = f[1]
            for neighbour in board.get_adjacent(cell.x, cell.y):
                if (neighbour.x, neighbour.y) not in visited:
                    visited.append((neighbour.x, neighbour.y))
                    queue.insert(0, neighbour)
                    father[neighbour.x][neighbour.y] = (cell.x, cell.y)
        return None

    def find_type(self, board, search_type):

        return Robot.bfs(board, (self.x, self.y), search_type)

    def find(self, board):

        return Robot.bfs_without_search(board, (self.x, self.y))


class RobotOne(Robot):
    def move(self, board):
        if self.trash is not None:
            self.clean_trash()
            board.robot = self
            board.board[self.x][self.y] = self
            return
        if self.contains_child:
            find_corral = self.find_type(board, Corral)
            if find_corral is not None:
                cell = board.board[find_corral[0]][find_corral[1]]
                if isinstance(cell, Corral):
                    board.board[find_corral[0]][find_corral[1]].set_robot(self)
                    board.board[self.x][self.y] = Blank([], self.x, self.y)
                    self.x = find_corral[0]
                    self.y = find_corral[1]
                    board.robot = self
                    return
                self.swap(board, cell)
                board.robot = self
                board.board[self.x][self.y] = self
                move_in_two = random.randint(0, 1)
                if self.move_with_child > 0 and move_in_two > 0:
                    self.move_with_child = 0
                    self.move(board)
                self.move_with_child = 1
                return
            find_trash_or_baby = self.find_type(board, Dirt)
        else:
            find_trash_or_baby = self.find(board)

        if find_trash_or_baby is not None:
            cell = board.board[find_trash_or_baby[0]][find_trash_or_baby[1]]
            if isinstance(cell, Child):
                self.contains_child = True
                self.child = cell
                self.move_with_child = 1
                board.board[find_trash_or_baby[0]][find_trash_or_baby[1]] = self
                if isinstance(board.board[self.x][self.y], Corral):
                    self.x = find_trash_or_baby[0]
                    self.y = find_trash_or_baby[1]
                    board.robot = self
                    board.board[self.x][self.y] = self
                    return
                board.board[self.x][self.y] = Blank([], self.x, self.y)
                self.x = find_trash_or_baby[0]
                self.y = find_trash_or_baby[1]
                board.robot = self
                board.board[self.x][self.y] = self
                return
            if isinstance(cell, Corral):
                board.board[find_trash_or_baby[0]][find_trash_or_baby[1]].set_robot(self)
                if isinstance(board.board[self.x][self.y], Corral):
                    self.x = find_trash_or_baby[0]
                    self.y = find_trash_or_baby[1]
                    board.robot = self
                    # board.board[self.x][self.y] = self
                    return
                board.board[self.x][self.y] = Blank([], self.x, self.y)
                self.x = find_trash_or_baby[0]
                self.y = find_trash_or_baby[1]
                board.robot = self
                return
            if isinstance(cell, Dirt):
                self.time_waiting = 0
                self.trash = cell
                board.board[find_trash_or_baby[0]][find_trash_or_baby[1]] = self
                if isinstance(board.board[self.x][self.y], Corral):
                    self.x = find_trash_or_baby[0]
                    self.y = find_trash_or_baby[1]
                    board.robot = self
                    board.board[self.x][self.y] = self
                    return
                board.board[self.x][self.y] = Blank([], self.x, self.y)
                self.x = find_trash_or_baby[0]
                self.y = find_trash_or_baby[1]
                board.robot = self
                board.board[self.x][self.y] = self
                return
            if isinstance(cell, Blank):
                if isinstance(board.board[self.x][self.y], Corral):
                    self.x = find_trash_or_baby[0]
                    self.y = find_trash_or_baby[1]
                    board.robot = self
                    board.board[self.x][self.y] = self
                    return

            self.swap(board, cell)

        board.robot = self


class RobotTwo(Robot):
    def move(self, board):
        if self.trash is not None:
            self.clean_trash()
            board.robot = self
            board.board[self.x][self.y] = self
            return
        if self.contains_child:
            find_corral = self.find_type(board, Corral)
            if find_corral is not None:
                cell = board.board[find_corral[0]][find_corral[1]]
                if isinstance(cell, Corral):
                    board.board[find_corral[0]][find_corral[1]].set_robot(self)
                    board.board[self.x][self.y] = Blank([], self.x, self.y)
                    self.x = find_corral[0]
                    self.y = find_corral[1]
                    board.robot = self
                    return
                self.swap(board, cell)
                board.robot = self
                board.board[self.x][self.y] = self
                move_in_two = random.randint(0, 1)
                if self.move_with_child > 0 and move_in_two > 0:
                    self.move_with_child = 0
                    self.move(board)
                self.move_with_child = 1
                return

        move_to_random_cell = self.get_random_cell(board)

        if move_to_random_cell is not None:
            cell = board.board[move_to_random_cell[0]][move_to_random_cell[1]]
            if isinstance(cell, Child):
                self.contains_child = True
                self.child = cell
                self.move_with_child = 1
                board.board[move_to_random_cell[0]][move_to_random_cell[1]] = self
                if isinstance(board.board[self.x][self.y], Corral):
                    self.x = move_to_random_cell[0]
                    self.y = move_to_random_cell[1]
                    board.robot = self
                    board.board[self.x][self.y] = self
                    return
                board.board[self.x][self.y] = Blank([], self.x, self.y)
                self.x = move_to_random_cell[0]
                self.y = move_to_random_cell[1]
                board.robot = self
                board.board[self.x][self.y] = self
                return
            if isinstance(cell, Corral):
                board.board[move_to_random_cell[0]][move_to_random_cell[1]].set_robot(self)
                if isinstance(board.board[self.x][self.y], Corral):
                    self.x = move_to_random_cell[0]
                    self.y = move_to_random_cell[1]
                    board.robot = self
                    # board.board[self.x][self.y] = self
                    return
                board.board[self.x][self.y] = Blank([], self.x, self.y)
                self.x = move_to_random_cell[0]
                self.y = move_to_random_cell[1]
                board.robot = self
                return
            if isinstance(cell, Dirt):
                self.time_waiting = 0
                self.trash = cell
                board.board[move_to_random_cell[0]][move_to_random_cell[1]] = self
                if isinstance(board.board[self.x][self.y], Corral):
                    self.x = move_to_random_cell[0]
                    self.y = move_to_random_cell[1]
                    board.robot = self
                    board.board[self.x][self.y] = self
                    return
                board.board[self.x][self.y] = Blank([], self.x, self.y)
                self.x = move_to_random_cell[0]
                self.y = move_to_random_cell[1]
                board.robot = self
                board.board[self.x][self.y] = self
                return
            if isinstance(cell, Blank):
                if isinstance(board.board[self.x][self.y], Corral):
                    self.x = move_to_random_cell[0]
                    self.y = move_to_random_cell[1]
                    board.robot = self
                    board.board[self.x][self.y] = self
                    return

            self.swap(board, cell)

        board.robot = self
        pass

    def __str__(self):
        return '\N{ghost}'

    def get_random_cell(self, board):
        adj = board.get_adjacent(self.x, self.y)

        while len(adj) > 0:
            rnd_i = random.randint(0, len(adj) - 1)
            if isinstance(adj[rnd_i], Obstacle) or \
                    (isinstance(adj[rnd_i], Corral) and self.contains_child and adj[rnd_i].contains_child):
                continue
            return adj[rnd_i].x, adj[rnd_i].y
        return None
