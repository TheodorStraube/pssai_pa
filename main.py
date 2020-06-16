import copy

from collections import defaultdict


from utils import n_pairs
from visual import schedule_to_gantt

class SchedulingProblem:
    def __init__(self, jobs, nr_machines=None):
        self.jobs = jobs
        self.nr_machines = int(nr_machines) or len(jobs)

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

            jobs = [Job([Operation(machine, time) for machine, time in n_pairs(line.split())]) for line in rest]                
        
        return SchedulingProblem(jobs, nr_machines=nr_machines)


class Job:
    def __init__(self, operations):
        self.operations = operations

    def __iter__(self):
        return iter(self.operations)

    def __str__(self):
        return 'Job --> {}'.format(str(self.operations))

class Operation:
    def __init__(self, machine, time):
        self.machine = int(machine)
        self.time = int(time)

    def __repr__(self):
        return 'OP [{} - {}]'.format(self.machine, self.time)

    def __iter__(self):
        return iter((self.machine, self.time))

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __hash__(self):
        return hash(tuple(self))


# for every machine, this yields a list of all operations to be done in order
class SchedulingSolution:
    
    def __init__(self, machines_plans, nr_jobs):
        self.machines_plans = machines_plans
        self.nr_jobs = nr_jobs

    def get_operations(self):
        ops = set()
        for n_plan_a, plan in enumerate(self.machines_plans):
            print(len(ops))
            for n_a, (job_a, operation_a) in enumerate(plan):
                for n_plan_b, plan_b in enumerate(self.machines_plans):
                    for n_b, (job_b, operation_b) in enumerate(plan_b):
                        if operation_a != operation_b:
                            # insert op_a before op_b
                            if job_a != job_b or job_a.operations.index(operation_a) > job_a.operations.index(operation_b) and not (n_a != n_b + 1 and n_plan_a == n_plan_b):
                                ops.add((n_plan_a, n_a, n_plan_b, n_b))
                                return ops
        return ops

    def apply(self, operation):
        n_plan_a, n_a, n_plan_b, n_b = operation
        plans_mod = copy.deepcopy(self.machines_plans)

        value = plans_mod[n_plan_a].pop(n_a)
        plans_mod[n_plan_b].insert(n_b, value)

        return SchedulingSolution(plans_mod, self.nr_jobs)

    def get_neighborhood(self):
        operations = self.get_operations()
        return [self.apply(operation) for operation in operations]

    # schedule by order of jobs --> all operations of job0 first, all of job1, ...
    @staticmethod
    def generate_initial(scheduling_problem):
        machines_plans = [[] for _ in range(scheduling_problem.nr_machines)]

        for job in scheduling_problem.jobs:
            for operation in job.operations:
                machines_plans[operation.machine].append((job, operation)) 
        return SchedulingSolution(machines_plans, len(scheduling_problem.jobs))

# a SchedulingSolution mapped to specific times
class ExecutionPlan:
    def __init__(self, schedule):
        self.plan = ExecutionPlan.from_schedule(schedule)

    def cost(self):
        return max(machine[-1][0] + machine[-1][1].time for machine in self.plan)

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
                    if next_op == len(job.operations) or next_op != job.operations.index(operation):
                        break

                    # starting time is 0 or after the last operation on this machine
                    machine_ready = 0 if not plan[machine_nr] else plan[machine_nr][-1][0] + plan[machine_nr][-1][1].time
                    start_time = max(next_time, machine_ready)
                    plan[machine_nr].append((start_time, operation, job))

                    # TODO: +1 on time?
                    memory[job] = (next_op + 1, start_time + operation.time)
                    changed = True

            is_done = not changed
        return plan
