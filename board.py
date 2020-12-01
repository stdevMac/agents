from types_defined import *
import utils
import random
import time


class Board:
    def __init__(self, m, n, percent_dirty_cells, percent_obstacle_cells, child_number, change_time, robot_type=0,
                 simulate_timelapse=False):
        self.valid = True
        self.board = [[]] * m
        self.m = m
        self.n = n
        self.number_of_dirty_cells = int(percent_dirty_cells * m * n / 100)
        self.number_of_obstacle_cells = int(percent_obstacle_cells * m * n / 100)
        self.child_number = child_number
        self.change_time = change_time
        self.iteration = 0
        self.number_of_changes = 0
        self.free_children = child_number
        self.simulate_timelapse = simulate_timelapse
        self.robot = None
        self.valid = m * n > self.number_of_dirty_cells + self.number_of_obstacle_cells + (self.child_number * 2) + 1
        if not self.valid:
            return

        for i in range(m):
            row = [Blank([], i, y) for y in range(n)]
            self.board[i] = row

        self.set_corral()
        self.set_child()
        self.set_trash()
        self.set_obstacle()
        self.set_robot(robot_type)

        if self.simulate_timelapse:
            self.print()
            time.sleep(1)

    def set_robot(self, robot_type):
        while True:
            rnd_x = random.randint(0, self.m)
            rnd_y = random.randint(0, self.n)

            cell = self.get_cell(rnd_x, rnd_y)
            if isinstance(cell, Blank):
                self.robot = RobotOne([], cell.x, cell.y) if robot_type == 0 else \
                    RobotTwo({}, cell.x, cell.y)
                self.board[cell.x][cell.y] = self.robot
                break

    def set_child(self):
        child_number = self.child_number

        while child_number != 0:
            rnd_x = random.randint(0, self.m)
            rnd_y = random.randint(0, self.n)

            cell = self.get_cell(rnd_x, rnd_y)
            if isinstance(cell, Blank):
                child = Child([Robot], cell.x, cell.y)
                self.board[cell.x][cell.y] = child
                child_number -= 1

    def set_trash(self):
        trash_number = self.number_of_dirty_cells

        while trash_number != 0:
            rnd_x = random.randint(0, self.m)
            rnd_y = random.randint(0, self.n)

            cell = self.get_cell(rnd_x, rnd_y)
            if isinstance(cell, Blank):
                self.board[cell.x][cell.y] = Dirt([Robot, Child], cell.x, cell.y)
                trash_number -= 1

    def set_obstacle(self):
        obstacle_number = self.number_of_obstacle_cells

        while obstacle_number != 0:
            rnd_x = random.randint(0, self.m)
            rnd_y = random.randint(0, self.n)

            cell = self.get_cell(rnd_x, rnd_y)
            if isinstance(cell, Blank):
                self.board[cell.x][cell.y] = Obstacle([Child], cell.x, cell.y)
                obstacle_number -= 1

    def set_corral(self):
        self.number_of_corrals = self.child_number

        rnd_x = random.randint(0, self.m)
        rnd_y = random.randint(0, self.n)
        self.set_corral_from_point(rnd_x, rnd_y)

    def set_corral_from_point(self, x, y):
        if self.number_of_corrals == 0:
            return True
        range_directions = [x for x in range(len(utils.DIRECTION) - 1)]
        random.shuffle(range_directions)

        for direction in range_directions:
            move_direction = utils.DIRECTION[direction]
            cell = self.get_cell(x + move_direction[0], y + move_direction[1])
            if not isinstance(cell, Blank):
                continue
            self.board[cell.x][cell.y] = Corral([], cell.x, cell.y)
            self.number_of_corrals -= 1
            if self.set_corral_from_point(cell.x, cell.y):
                return True
        return False

    def get_cell(self, x, y):
        if 0 > x or x > self.m - 1:
            return None
        if 0 > y or y > self.m - 1:
            return None
        return self.board[x][y]

    def simulate(self):
        value_iterations = self.change_time
        while self.change_time != 0:
            for i in range(100 * value_iterations):
                self.board[self.robot.x][self.robot.y].move(self)
                for x in range(self.m):
                    for y in range(self.n):
                        if isinstance(self.board[x][y], Robot) or isinstance(self.board[x][y], Corral):
                            continue
                        self.board[x][y].move(self)
                for x in range(self.m):
                    for y in range(self.n):
                        t = random.randint(0, 100)
                        if isinstance(self.board[x][y], Child) and t < 60:
                            self.number_of_dirty_cells += self.board[x][y].create_trash(self)

                if self.simulate_timelapse:
                    self.print()
                    time.sleep(0.3)
                end_state, cells = self.evaluate_board()
                if end_state is not None:
                    if end_state:
                        # print('Robot finish his objective')
                        return True, cells
                    # print('Robot lost, must be replaced')
                    return False, cells
            self.refresh_board()
        return False, self.number_of_dirty_cells

    def evaluate_board(self):
        self.free_children = 0
        self.number_of_dirty_cells = 0
        for x in range(self.m):
            for y in range(self.n):
                if isinstance(self.board[x][y], Child):
                    return None, None
                if isinstance(self.board[x][y], Dirt):
                    self.number_of_dirty_cells += 1

        percent_dirty_cells = (self.number_of_dirty_cells * 100) / (self.m * self.n)
        self.number_of_dirty_cells = percent_dirty_cells
        if percent_dirty_cells > 60:
            return False, percent_dirty_cells
        return (True, 0) if self.number_of_dirty_cells == 0 else (False, percent_dirty_cells)

    def refresh_board(self):
        self.change_time -= 1
        corrals = []
        trash = []
        children = []
        obstacles = []
        for x in range(self.m):
            for y in range(self.n):
                if isinstance(self.board[x][y], Corral):
                    corrals.append(self.board[x][y])
                if isinstance(self.board[x][y], Dirt):
                    trash.append(self.board[x][y])
                if isinstance(self.board[x][y], Child):
                    children.append(self.board[x][y])
                if isinstance(self.board[x][y], Obstacle):
                    obstacles.append(self.board[x][y])
                self.board[x][y] = Blank([], x, y)

        self.set_by_list(corrals)
        self.set_by_list(trash)
        self.set_by_list(children)
        self.set_by_list(obstacles)
        self.set_by_list([self.robot])

    def set_by_list(self, list_to_add):
        while len(list_to_add) > 0:
            rnd_m = random.randint(0, self.m - 1)
            rnd_n = random.randint(0, self.n - 1)

            if isinstance(self.board[rnd_m][rnd_n], Blank):
                self.board[rnd_m][rnd_n] = list_to_add.pop()
                self.board[rnd_m][rnd_n].x = rnd_m
                self.board[rnd_m][rnd_n].y = rnd_n

    def get_adjacent(self, x, y):
        adj = []
        for direction in utils.DIRECTION:
            cell = self.get_cell(x + direction[0], y + direction[1])
            if cell is not None:
                adj.append(cell)
        return adj

    def print(self):
        board = ''
        for i in range(self.m):
            for j in range(self.n):
                board += str(self.board[i][j])
            board += '\n'
        print(board)
