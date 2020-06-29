import math
import random
import json
from tqdm import tqdm, trange

from jobshop import ExecutionPlan, SchedulingProblem, SchedulingSolution

from visual import schedule_to_gantt


params = {}

with open('params.json') as param_file:
    params = json.load(param_file)

INITIAL_TEMPERATURE = params.get('initial_temperature', 10)
FROZEN_TEMPERATURE = params.get('frozen_temperature', 0.2)
COOLING_RATIO = params.get('cooling_ratio', 0.1)
NUMBER_OF_ITERATIONS = params.get('iterations', 100)
INITIAL_METHOD = params.get('initial_method', 'random')
NEIGHBOR_METHOD = params.get('neighbor_method', 'near')

print('Initial temperature:', INITIAL_TEMPERATURE)
print('Frozen temperature:', FROZEN_TEMPERATURE)
print('Cooling ratio:', COOLING_RATIO)
print('Iterations:', NUMBER_OF_ITERATIONS)
print('Method of generating initial solution:', INITIAL_METHOD)
print('Neighborhood type', NEIGHBOR_METHOD)

def cost_lt(a, b):
    if a == b or a == -1:
        return False
    if b == -1:
        return True
    return a < b

def random_take(delta_eval, temperature):
    try:
        return random.random() < math.exp(-delta_eval / temperature)
    except OverflowError:
        return True

def get_operations(config):
    return (list(config.get_near_operations()) if NEIGHBOR_METHOD == 'near'
            else list(config.get_far_operations()))

def run(initial_configuration):

    config = initial_configuration

    not_feasable_score = sum(op.time for machine in config.machines_plans for (_, op) in machine)

    last_score = not_feasable_score

    best_solution = None
    best_score = not_feasable_score

    try:

        temperature = INITIAL_TEMPERATURE

        j = 0
        while temperature > FROZEN_TEMPERATURE:

            operations = get_operations(config)

            tqdm_status = trange(NUMBER_OF_ITERATIONS)
            for _ in tqdm_status:
                chosen = random.choice(operations)

                neighbor = config.apply(chosen)
                neighbor_exe = ExecutionPlan(neighbor)
                neighbor_score = neighbor_exe.cost()
                neighbor_score = (neighbor_score if neighbor_score != -1 else not_feasable_score)

                my_score = ExecutionPlan(config).cost()
                my_score = (my_score if my_score != -1 else not_feasable_score)

                if my_score < best_score:
                    best_solution = config
                    best_score = my_score

                delta_eval = neighbor_score - my_score

                if cost_lt(neighbor_score, my_score) or random_take(delta_eval, temperature):
                    config = neighbor
                    operations = get_operations(config)

                last_increase = (my_score - last_score) / last_score * 100
                tqdm_status.set_postfix({'eff': not_feasable_score /
                                         (ExecutionPlan(best_solution).cost() * len(config.machines_plans)),
                                         'cost': my_score, 'T':'{:.3f}%'.format(temperature),
                                         'Δ':'{:+.3f}'.format(last_increase or 0)})
            last_score = my_score
            j += 1
            temperature = INITIAL_TEMPERATURE * math.exp(- j * COOLING_RATIO)

            #print('T = {} score = {}'.format(temperature, my_score))
    except KeyboardInterrupt:
        # display the latest solution when stopped
        pass
    return best_solution

problems = SchedulingProblem.from_seed_file()

problem = problems['ta01']
problem = SchedulingProblem.from_file('test_problem_1.txt')

initial_plan = (SchedulingSolution.generate_seq_initial(problem) if INITIAL_METHOD == 'seq'
                else SchedulingSolution.generate_random_initial(problem))

print('Initial cost:', ExecutionPlan(initial_plan).cost())
best = run(initial_plan)
print('Result cost:', ExecutionPlan(best).cost())

execution = ExecutionPlan(best)
schedule_to_gantt(execution.plan, problem.jobs)
