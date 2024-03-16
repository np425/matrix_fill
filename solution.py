import time

import numpy as np
from termcolor import COLORS, colored


def first_spot(grid, start_pos, value):
    grid = grid.flatten()
    length = grid.shape[0]

    for idx in range(start_pos, length):
        if grid[idx] == value:
            return idx

    return -1


def delete_duplicate_arrays(array_3d):
    i = 0

    while i < len(array_3d):
        array_2d = array_3d[i]

        x = i + 1
        while x < len(array_3d):
            cur_array = array_3d[x]

            if np.array_equal(array_2d, cur_array):
                del array_3d[x]
            else:
                x = x + 1

        i = i + 1


def gen_rotations(mask):
    rotations = [mask]

    for _ in range(3):
        rotations.append(np.rot90(rotations[-1], 1))

    return rotations


def display_array(array, transform_f):
    array_text = '\n'.join(
        ' '.join(map(transform_f, row)) for row in array
    )
    print(array_text)


def insert_shape(grid, pos, shape):
    pos_y = pos // grid.shape[1]
    pos_x = pos % grid.shape[1]

    sliced = grid[pos_y:shape.shape[0] + pos_y, pos_x:shape.shape[1] + pos_x]

    if sliced.shape != shape.shape or not np.all(shape & ~sliced == shape):
        return False

    grid[pos_y:shape.shape[0] + pos_y, pos_x:shape.shape[1] + pos_x] = sliced | shape
    return True


def remove_shape(grid, pos, mask):
    pos_y = pos // grid.shape[1]
    pos_x = pos % grid.shape[1]

    sliced = grid[pos_y:mask.shape[0] + pos_y, pos_x:mask.shape[1] + pos_x]
    grid[pos_y:mask.shape[0] + pos_y, pos_x:mask.shape[1] + pos_x] = sliced ^ mask


def visualise_solution(grid, rotations, shape_offsets, solution, colors):
    result_grid = np.zeros(grid.shape, int)

    for pos, shape_idx in solution:

        # for visuals
        shape = rotations[shape_idx]
        pos = pos - shape_offsets[shape_idx]

        pos_y = pos // grid.shape[1]
        pos_x = pos % grid.shape[1]

        sliced = result_grid[pos_y:pos_y + shape.shape[0], pos_x:pos_x + shape.shape[1]]
        for coord, val in np.ndenumerate(shape):
            if val:
                sliced[coord] = shape_idx + 1

    display_array(result_grid, transform_f=lambda x: colored(str(x) if x != 0 else ' ', color=colors[x-1]))


def solve(grid, shapes, shape_offsets):
    next_pos = first_spot(grid, 0, 0)

    check_stack = [(next_pos, shape_idx) for shape_idx in range(len(shapes))]

    trace_back = []

    while check_stack:
        pos, shape_idx = check_stack.pop()

        # remove previous shapes
        while trace_back:
            prev_pos, prev_shape_idx = trace_back[-1]

            if prev_pos >= pos:
                trace_back.pop()
                remove_shape(grid, prev_pos - shape_offsets[prev_shape_idx], shapes[prev_shape_idx])
            else:
                break

        # insert new shape
        if insert_shape(grid, pos - shape_offsets[shape_idx], shapes[shape_idx]):
            trace_back.append((pos, shape_idx))

            next_pos = first_spot(grid, pos, 0)
            if next_pos != -1:
                check_stack.extend((next_pos, shape_idx) for shape_idx in range(len(shapes)))
            elif np.all(grid):
                yield trace_back


def solve_and_display(grid, shapes, colors):
    # generate shape rotations
    rotations = [rot for shape in shapes for rot in gen_rotations(shape)]
    delete_duplicate_arrays(rotations)

    shape_offsets = [first_spot(shape, 0, 1) for shape in rotations]

    t_start = time.time()
    sol_n = 0

    # find solutions
    for sol in solve(grid.copy(), rotations, shape_offsets):
        sol_n = sol_n + 1
        print(colored(f'Solution {sol_n}', 'green'))
        visualise_solution(grid, rotations, shape_offsets, sol, colors)
        print()

    t_stop = time.time()

    print(colored(f'Elapsed time {t_stop - t_start} seconds', 'yellow'))
    print(colored(f'Found {sol_n} solutions', 'yellow'))
    print()

    # visualise used shapes
    for idx, shape in enumerate(rotations):
        # for visuals
        print(colored(f'Shape {idx + 1}', color=colors[idx]))
        display_array(shape, lambda x: str(x) if x != 0 else ' ')
        print()

    print(colored('Grid', 'green'))
    display_array(grid, lambda x: str(x) if x != 1 else ' ')


def pad_array(array_2d, padding):
    if not array_2d:
        return array_2d

    max_width = max(map(len, array_2d))

    for row in array_2d:
        row.extend((padding,) * (max_width - len(row)))

    return array_2d


def read_np_array(prompt, padding):
    print(prompt)

    array = []

    while True:
        row = input().strip().lower()

        if not row:
            break

        row = [int(x) for x in row.split(' ')]
        array.append(row)

    pad_array(array, padding)
    return np.asarray(array, int)


def main():
    colors = list(COLORS.keys())[2:]

    grid = read_np_array(colored('Enter 2d grid (0s empty spaces, 1 holes, empty line to finish)', 'green'), padding=0)

    shapes = []

    shape_idx = 0
    while True:
        shape = read_np_array(
            colored(f'Enter shape {shape_idx + 1} (0 for space, 1 for occupying space, empty line to finish)',
                    color=colors[shape_idx]), padding=0)
        if shape.size == 0:
            break

        shapes.append(shape)
        shape_idx = shape_idx + 1

    solve_and_display(grid, shapes, colors)


if __name__ == "__main__":
    main()
