def n_pairs(iterable, n=2):
    # return n-pairs of elements of the iterator:
    # n_pairs(range(5), 2) = ((0, 1), (2, 3))

    iterator = iter(iterable)
    return zip(*[iterator] * n)