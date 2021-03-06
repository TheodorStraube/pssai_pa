import copy
import random
from collections import defaultdict
from itertools import permutations

from utils import n_pairs, load_seeds, generate_job_shop


class SchedulingProblem:
    def __init__(self, jobs, nr_machines=None):
        self.jobs = jobs
        self.nr_machines = len(jobs)

    def __str__(self):
        lines = []

        for n, j in enumerate(self.jobs):
            lines.append('Job {}:\t{}'.format(n, ' '.join(str((o.machine, o.time)) for o in j.operations)))
        return '\n'.join(lines)

    def __iter__(self):
        return iter(self.jobs)

    @staticmethod
    def from_file(filename):
        with open(filename) as input_file:
            lines = input_file.readlines()

            nr_jobs, nr_machines = lines[0].split()
            rest = lines[1:]

            jobs = [Job([Operation(machine, time, n) for n, (machine, time) in enumerate(n_pairs(line.split()))], n) for
                    n, line in enumerate(rest)]

        return SchedulingProblem(jobs, nr_machines=nr_machines)

    @staticmethod
    def from_seed_file(filename='job_seeds.txt'):
        seed_data = load_seeds(filename=filename)
        job_shops = {name: generate_job_shop(*values) for name, values in seed_data.items()}

        job_shops = {name: SchedulingProblem(
            [Job([Operation(m - 1, t, n) for n, (m, t) in enumerate(zip(machines, times))], job_nr)
             for job_nr, (machines, times) in enumerate(zip(*values))])
                     for name, values in job_shops.items()}
        return job_shops


class Job:

    def __init__(self, operations, job_nr):
        self.operations = operations
        self.nr = job_nr

    def __iter__(self):
        return iter(self.operations)

    def __hash__(self):
        return self.nr

    def __eq__(self, other):
        if not isinstance(other, Job):
            return False

        return hash(self) == hash(other)

    """
    def __str__(self):
        return 'Job --> {}'.format(str(self.operations))
    """


class Operation:
    def __init__(self, machine, time, index):
        self.machine = int(machine)
        self.time = int(time)
        self.index = index

    def __repr__(self):
        return 'OP [{} - {}]'.format(self.machine, self.time)

    def __iter__(self):
        return iter((self.machine, self.time))

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __hash__(self):
        return hash(tuple(self))

    def __gt__(self, other):
        return tuple(self) > tuple(other)


# for every machine, this yields a list of all operations to be done in order
class SchedulingSolution:

    def __init__(self, machines_plans, nr_jobs):
        self.machines_plans = machines_plans
        self.nr_jobs = nr_jobs

    # generate swaps of any 2 operations
    # does not check for illegal configurations / deadlocks
    def get_far_operations(self):
        return [(machine, a, b)
                for machine, machines_ops in enumerate(self.machines_plans)
                for a, b in permutations(range(len(machines_ops)), r=2)]

    # generate swaps of 2 operations that immediately follow each other
    # does not check for illegal configurations / deadlocks
    def get_near_operations(self):
        return [(machine, a, a+1)
                for machine, machines_ops in enumerate(self.machines_plans)
                for a in range(len(machines_ops)-1)]

    def apply(self, operation):
        machine, a, b = operation
        plans_mod = copy.deepcopy(self.machines_plans)

        value = plans_mod[machine].pop(a)
        plans_mod[machine].insert(b, value)

        return SchedulingSolution(plans_mod, self.nr_jobs)

    def get_neighborhood(self):
        operations = self.get_operations()
        return [self.apply(operation) for operation in operations]

    # schedule by order of jobs --> all operations of job0 first, all of job1, ...
    @staticmethod
    def generate_seq_initial(scheduling_problem):
        machines_plans = [[] for _ in range(scheduling_problem.nr_machines)]

        for job in scheduling_problem.jobs:
            for operation in job.operations:
                machines_plans[operation.machine].append((job, operation))
        return SchedulingSolution(machines_plans, len(scheduling_problem.jobs))

    # generate schedule by iteratively adding random valid operations
    @staticmethod
    def generate_random_initial(scheduling_problem):
        machines_plans = [[] for _ in range(scheduling_problem.nr_machines)]

        num_jobs = len(scheduling_problem.jobs)
        # last operation added to the plan for each job
        last_ops = [-1 for _ in range(num_jobs)]
        # number of operations per job
        num_ops = [len(j.operations) for j in scheduling_problem.jobs]

        unfinished_jobs = [ n for n in range(len(scheduling_problem.jobs)) ]

        while len(unfinished_jobs):
            j = random.sample(unfinished_jobs, 1)[0]
            if last_ops[j] < (num_ops[j] - 1):
                job = scheduling_problem.jobs[j]
                op = job.operations[last_ops[j] + 1]
                machines_plans[op.machine].append((job, op))
                last_ops[j] += 1
            else:
                unfinished_jobs.remove(j)
        return SchedulingSolution(machines_plans, len(scheduling_problem.jobs))


# a SchedulingSolution mapped to specific times
class ExecutionPlan:
    def __init__(self, schedule):
        self.plan = ExecutionPlan.from_schedule(schedule)

    def cost(self):
        if not self.plan or self.has_collisions():
            return -1
        return max((machine[-1][0] + machine[-1][1].time) if machine else 0 for machine in self.plan)

    # basic check for constraints
    def has_collisions(self):
        result = False
        for machine in self.plan:
            last = 0
            for start, op, _ in machine:
                result |= start < last
                last = start + op.time

        return result

    # check if every op is started after previous op from same job completed
    def is_ordered(self):
        return False

    # generate an ExecutionPlan from a SchedulingSolution
    @staticmethod
    def from_schedule(schedule):

        # for every job, give id of next operation to plan and their lowest possible start time
        memory = defaultdict(lambda: (0, 0))

        # for every machine, list the operations: (starttime, operation)
        plan = [[] for _ in schedule.machines_plans]

        is_done = False

        while not is_done:
            # if nothing has been changed for one iteration, we are done
            changed = False

            # iterate over operations that have not yet been included in the plan
            for machine_nr, m_plans in enumerate(schedule.machines_plans):
                already_processed = len(plan[machine_nr])
                for todo in m_plans[already_processed:]:

                    job, operation = todo

                    next_op, next_time = memory[job]

                    # if next op for this job has not been started or the job is done, handle next machine
                    if next_op == len(job.operations) or next_op != operation.index:
                        break

                    # starting time is 0 or after the last operation on this machine
                    machine_ready = 0 if not plan[machine_nr] else plan[machine_nr][-1][0] + plan[machine_nr][-1][
                        1].time
                    start_time = max(next_time, machine_ready)
                    plan[machine_nr].append((start_time, operation, job))

                    # TODO: +1 on time?
                    memory[job] = (next_op + 1, start_time + operation.time)
                    changed = True
            is_done = not changed

        is_done = all(len(p) == len(s) for p, s in zip(plan, schedule.machines_plans))
        return plan if is_done else []
