from itertools import izip, product, permutations
from pprint import pprint


if __name__ == '__main__':
    dict([(1,2), (3,4)])
    for variation in variations({1:[2,3], 4:[5], 6:[7,8,9]}):
        print dict(variation)