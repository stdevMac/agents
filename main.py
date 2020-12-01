import copy
import sys

from board import Board


def main():
    # args
    if 10 < len(sys.argv) or len(sys.argv) < 7:
        print('Unused number of params')
        s = 'Arguments:\n' \
            'Number of Rows: m\n' \
            'Number of Columns: n\n' \
            'Percent of Dirty Cells: x%\n' \
            'Percent of Obstacles: x%\n' \
            'Number of Child: x\n' \
            'Run x times simulation: n\n' \
            '[Run With second bot] x [any] => Default 30\n' \
            '[timelapse] : x [any] => Default true'
        print(s)
        exit(1)

    m = int(sys.argv[1])
    n = int(sys.argv[2])
    percent_dirty_cells = int(sys.argv[3])
    percent_obstacle_cells = int(sys.argv[4])
    child_number = int(sys.argv[5])
    change_time = int(sys.argv[6])
    second_robot = 0
    timelapse = False
    if len(sys.argv) > 7:
        second_robot = 0 if int(sys.argv[7]) == 0 else 1
    if len(sys.argv) > 8:
        timelapse = True
    sim_number = 30
    environment = 10

    while environment > 0:
        board = Board(m, n, percent_dirty_cells, percent_obstacle_cells, child_number, change_time, second_robot,
                      timelapse)
        dirty_cells = []
        won = 0
        lose = 0
        if board.valid:
            new_board = copy.copy(board)
            while sim_number > 0:
                end_state, cells = new_board.simulate()
                won += 1 if end_state else 0
                lose += 1 if not end_state else 0
                dirty_cells.append(cells)
                sim_number -= 1
            sim_number = 30
            print(f'Environment {10 - environment}:')
            print(f'Won {won} times')
            print(f'Lose {lose} times')
            print(f'Dirty cells {sum(dirty_cells) / len(dirty_cells)}')
        else:
            print('Invalid board')
        environment -= 1


if __name__ == '__main__':
    main()
