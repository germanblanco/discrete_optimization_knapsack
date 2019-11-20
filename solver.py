#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import operator
from fractions import gcd
from functools import reduce

Item = namedtuple("Item", ['index', 'value', 'weight'])

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
    new_items = [Item(item.index, item.value, int(item.weight/factor)) for item in items]
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
    for column in reversed(range(len(items)+1)):
        if the_matrix[row][column] == the_matrix[row][column-1]:
            taken[column-1] = 0
        else:
            taken[column-1] = 1
            row = row - items[column-1].weight
    return taken

def _branch_and_bound(items, capacity, taken, index=0, value=0):
    item = items[index]
    if index == len(items)-1:
        if capacity >= item.weight:
            taken_copy = taken.copy()
            taken_copy[index] = 1
            return value + item.value, taken_copy
        else:
            return value, taken
    else:
        value_without, taken_without = _branch_and_bound(items, capacity, taken, index+1, value)
        if capacity >= item.weight:
            taken_copy = taken.copy()
            taken_copy[index] = 1
            value_with, taken_with = _branch_and_bound(items, capacity-item.weight, taken_copy, index+1, value+item.value)
            if value_with > value_without:
                return value_with, taken_with
            else:
                return value_without, taken_without
        else:
            return value_without, taken_without

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
        items.append(Item(i-1, int(parts[0]), int(parts[1])))

    value = 0
    weight = 0
    taken = [0]*len(items)
    optimal = 0

    if (len(items) * capacity) < 1000000000:
        taken = _dynamic_programming(items, capacity, taken)
        optimal = 1

    if optimal == 0:
        taken = _density_greedy(items, capacity, taken)

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

