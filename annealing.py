import math
import random
from tqdm import tqdm, trange

from main import ExecutionPlan, SchedulingProblem, SchedulingSolution

from visual import schedule_to_gantt


INITIAL_TEMPERATURE = 100
FROZEN_TEMPERATURE = 0.2

COOLING_RATIO = 0.05

NUMBER_OF_ITERATIONS = 100


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

    not_feasable_score = sum(op.time for machine in config.machines_plans for (_, op) in machine)

    last_score = not_feasable_score

    best_solution = None
    best_score = not_feasable_score

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
                neighbor_score = (neighbor_score if neighbor_score != -1 else not_feasable_score)

                my_score = ExecutionPlan(config).cost()
                my_score = (my_score if my_score != -1 else not_feasable_score)

                if my_score < best_score:
                    best_solution = config
                    best_score = my_score

                delta_eval = neighbor_score - my_score

                if cost_lt(neighbor_score, my_score):
                    config = neighbor
                    operations = list(config.get_operations())
                elif random_take(delta_eval, temperature):
                    config = neighbor
                    operations = list(config.get_operations())

                last_increase = (last_score - my_score) / last_score * 100
                tqdm_status.set_postfix({'eff': not_feasable_score / (ExecutionPlan(best_solution).cost() * len(config.machines_plans)),
                                         'score': my_score, 'T': temperature, 'Δ':'{:.3f}%'.format(last_increase or 0)})
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
initial_plan = SchedulingSolution.generate_seq_initial(problem)
print('Seq cost:', ExecutionPlan(initial_plan).cost())
print('Random cost:', ExecutionPlan(SchedulingSolution.generate_random_initial(problem)).cost())
print('Random cost:', ExecutionPlan(SchedulingSolution.generate_random_initial(problem)).cost())

best = run(initial_plan)

execution = ExecutionPlan(best)
schedule_to_gantt(execution.plan, problem.jobs)
