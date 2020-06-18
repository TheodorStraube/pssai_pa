import re
import numpy as np


m = 2147483647
a = 16807
b = 127773
c = 2836


def unif(seed, low, high):
    k = int(seed / b)
    seed = a * (seed % b) - k * c

    seed = seed + m if seed < 0 else seed
    value_0_1 = seed / m
    
    return seed, low + int(value_0_1 * (high - low + 1))


def generate_job_shop(time_seed, machine_seed, nb_jobs, nb_machines):

    d = np.asarray([[unif(time_seed, 1, 99) for j in range(nb_machines)] for i in range(nb_jobs)])

    d = np.zeros((nb_jobs, nb_machines))
    for i in  range(nb_jobs):
        for j in range(nb_machines):
            time_seed, unif_value = unif(time_seed, 1, 99)
            d[i, j] = unif_value

    M = np.asarray([[j for j in range(nb_machines)] for i in range(nb_jobs)])

    for i in range(nb_jobs):
        for j in range(nb_machines):
            machine_seed, unif_index = unif(machine_seed, j, nb_machines -1)
            M[i, j], M[i, unif_index] = M[i, unif_index], M[i, j] 

    return M + 1, d.astype(int)


def load_seeds(filename='job_seeds.txt'):
    with open(filename) as textfile:
        text = textfile.read()

    head_regexp = re.compile(r'(\d+) jobs  (\d+) machines.*')
    tail_regexp = re.compile(r'\s+(\d+)\s+(\d+)\s+(\S+)')

    heads = [(match.groups(), match.start()) for match in head_regexp.finditer(text)]
    tails = [(match.groups(), match.start()) for match in tail_regexp.finditer(text)]

    seeds = [(groups, next(head for head, head_start in reversed(heads) if head_start < start)) for groups, start in tails]

    seeds = {name: (int(t_seed), int(m_seed), int(nr_j), int(nr_m)) for (t_seed, m_seed, name), (nr_j, nr_m) in seeds}
    return seeds



def n_pairs(iterable, n=2):
    # return n-pairs of elements of the iterator:
    # n_pairs(range(5), 2) = ((0, 1), (2, 3))

    iterator = iter(iterable)
    return zip(*[iterator] * n)