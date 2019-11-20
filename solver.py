#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import operator
from fractions import gcd
from functools import reduce

Item = namedtuple("Item", ['index', 'value', 'weight', 'density'])

def _density_greedy(items, capacity, taken):
    # a second trivial greedy algorithm for filling the knapsack
    # it takes items with maximum value density first
    remaining_capacity = capacity
    def compare_remaining_items(idx_item):
        index, item = idx_item
        if item.weight <= remaining_capacity and taken[item.index] == 0:
            return item.density
        else:
            return 0

    while remaining_capacity > min([item.weight for item in items if taken[item.index] == 0]):
        index, item = max(enumerate(items), key=compare_remaining_items)
        taken[item.index] = 1
        remaining_capacity -= item.weight

    return taken

def find_gcd(list):
    x = reduce(gcd, list)
    return x

def _normalize_capacity(items, capacity):
    item_weights = [item.weight for item in items]
    factor = find_gcd(item_weights)
    new_items = [Item(item.index, item.value, int(item.weight/factor), item.density) for item in items]
    new_capacity = int(capacity/factor)
    return new_items, new_capacity, factor

def _dynamic_programming(items, capacity, taken):
    the_matrix = [[0 for x in range(len(items)+1)] for y in range(capacity+1)] 
    for column in range(len(items)+1):
        for row in range(capacity+1):
            if column == 0:
                the_matrix[row][column] = 0
            else:
                value_without = the_matrix[row][column-1]
                item = items[column-1]
                if item.weight > row:
                    the_matrix[row][column] = value_without
                else:
                    value_with = the_matrix[row-item.weight][column-1] + item.value
                    if value_with < value_without:
                        the_matrix[row][column] = value_without
                    else:
                        the_matrix[row][column] = value_with
    row = capacity
    for column in reversed(range(1, len(items)+1)):
        if the_matrix[row][column] == the_matrix[row][column-1]:
            taken[column-1] = 0
        else:
            taken[column-1] = 1
            row = row - items[column-1].weight
    return taken

def _branch_and_bound(items, capacity, taken, index=0, value=0, node_limit=1000000):
    item = items[index]
    if node_limit != 0:
         _branch_and_bound.current_node_counter = node_limit
         _branch_and_bound.current_solution = None
         _branch_and_bound.current_value = None
    else:
        current_counter = _branch_and_bound.current_node_counter - 1
        current_solution = _branch_and_bound.current_solution
        current_value = _branch_and_bound.current_value
        if current_counter is None or current_counter == 0:
            return current_solution, current_value, 0
        else:
            _branch_and_bound.current_node_counter = current_counter

    result_taken = None
    result_value = None
    result_optimal = None
    if index == len(items)-1:
        if capacity >= item.weight:
            taken_copy = taken.copy()
            taken_copy[index] = 1
            result_taken = taken_copy
            result_value = value + item.value
            result_optimal = 1
        else:
            result_taken = taken
            result_value = value
            result_optimal = 1
    else:
        taken_without, value_without, optimal = _branch_and_bound(items,
                                                                  capacity,
                                                                  taken,
                                                                  index+1,
                                                                  value,
                                                                  0)
        if capacity >= item.weight and optimal == 1:
            taken_copy = taken.copy()
            taken_copy[index] = 1
            taken_with, value_with, optimal = _branch_and_bound(items,
                                                                capacity-item.weight,
                                                                taken_copy,
                                                                index+1,
                                                                value+item.value,
                                                                0)
            if value_with > value_without:
                result_taken = taken_with
                result_value = value_with
            else:
                result_taken = taken_without
                result_value = value_without
        else:
            result_taken = taken_without
            result_value = value_without
        result_optimal = optimal
    current_solution = _branch_and_bound.current_solution
    current_value = _branch_and_bound.current_value
    if current_value is None or result_value > current_value:
        _branch_and_bound.current_solution = result_taken
        _branch_and_bound.current_value = result_value
    return result_taken, result_value, result_optimal

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1]), float(int(parts[0])/int(parts[1]))))

    value = 0
    weight = 0
    taken = [0]*len(items)
    optimal = 0

    new_items, new_capacity, _ = _normalize_capacity(items, capacity)
    if (len(items) * new_capacity) < 1000000000:
        taken = _dynamic_programming(new_items, new_capacity, taken)
        value = sum([item.value for item in items if taken[item.index] == 1])
        optimal = 1

    if optimal == 0:
        taken = _density_greedy(items, capacity, taken)
        value = sum([item.value for item in items if taken[item.index] == 1])

    if optimal == 0:
        taken_copy = taken.copy()
        taken_copy, new_value, optimal = _branch_and_bound(items, capacity, taken_copy)
        if (new_value > value):
            taken = taken_copy
            value = new_value

    value = sum([item.value for item in items if taken[item.index] == 1])
    
    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(optimal) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

