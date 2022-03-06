table = [
    ['name1', 3, 4, 2, 1, 'b'],
    ['name2', 0, 0, 0, 0, 'b'],
    ['name3', 10, 11, 1, 5, 'b'],
    ['name4', 5, 0, 0, 5, 'b']
]
total = [sum(table[i][j] for i in range(len(table))) for j in range(1, 5)]
print(total)