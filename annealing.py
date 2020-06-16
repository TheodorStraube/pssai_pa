import math
import random
from tqdm import tqdm, trange

from main import ExecutionPlan, SchedulingProblem, SchedulingSolution

from visual import schedule_to_gantt


INITIAL_TEMPERATURE = 1
FROZEN_TEMPERATURE = 0.1

COOLING_RATIO = 0.01

NUMBER_OF_ITERATIONS = 2000

# for this problem only, sum of all times
NOT_FEASABLE_SCORE = 7773


prob = SchedulingProblem.from_file('test_problem_1.txt')

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


def run(initial_configuration):

    config = initial_configuration

    last_score = NOT_FEASABLE_SCORE
    last_increase = None

    try:

        temperature = INITIAL_TEMPERATURE

        j = 0
        while temperature > FROZEN_TEMPERATURE:
            operations = list(config.get_operations())

            tqdm_status = trange(NUMBER_OF_ITERATIONS)
            for _ in tqdm_status:
                chosen = random.choice(operations)

                neighbor = config.apply(chosen)
                neighbor_exe = ExecutionPlan(neighbor)
                neighbor_score = neighbor_exe.cost()
                neighbor_score = (neighbor_score if neighbor_score != -1 else NOT_FEASABLE_SCORE)

                my_score = ExecutionPlan(config).cost()
                my_score = (my_score if my_score != -1 else NOT_FEASABLE_SCORE)

                delta_eval = neighbor_score - my_score

                if cost_lt(neighbor_score, my_score):
                    config = neighbor
                    operations = list(config.get_operations())
                elif random_take(delta_eval, temperature):
                    config = neighbor
                    operations = list(config.get_operations())

                last_increase = (last_score - my_score) / last_score * 100
                tqdm_status.set_postfix({'score': my_score, 'T': temperature, 'Δ':'{:.3f}%'.format(last_increase or 0)})
            last_score = my_score
            j += 1
            temperature = INITIAL_TEMPERATURE * math.exp(- j * COOLING_RATIO)

            #print('T = {} score = {}'.format(temperature, my_score))
    except:
        pass
    return config

initial_plan = SchedulingSolution.generate_initial(prob)
best = run(initial_plan)

execution = ExecutionPlan(best)
schedule_to_gantt(execution.plan, prob.jobs)