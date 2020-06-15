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


# for every machine, this yields a list of all operations to be done in order
class SchedulingSolution:
    
    def __init__(self, machines_plans, nr_jobs):
        self.machines_plans = machines_plans
        self.nr_jobs = nr_jobs

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
            for start, op in machine:
                result |= start < last
                last = start + op.time

        return result


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
                    plan[machine_nr].append((start_time, operation))

                    # TODO: +1 on time?
                    memory[job] = (next_op + 1, next_time + operation.time)
                    changed = True

            is_done = not changed
        return plan


prob = SchedulingProblem.from_file('test_problem_1.txt')
initial_plan = SchedulingSolution.generate_initial(prob)
exe = ExecutionPlan(initial_plan)


print('Calculated Cost:', exe.cost())
print('Total Sum:', sum(sum(operation.time for operation in job.operations) for job in prob.jobs))
print('Detected collisions:', exe.has_collisions())

schedule_to_gantt(exe.plan, prob.jobs)
