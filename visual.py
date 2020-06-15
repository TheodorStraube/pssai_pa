import plotly.figure_factory as ff
import random

def schedule_to_gantt(schedule, jobs):
    data = []

    job_by_op = dict()
    for job in jobs:
        for op in job.operations:
            job_by_op[op] = str(job)

    for n, machines_plan in enumerate(schedule):
        for start, operation in machines_plan:
            data.append({
                'Task': 'Machine {}'.format(n),
                'Resource': str(job_by_op[operation]),
                'Start': start,
                'Finish': start + operation.time
             })

    colors = {str(job): (random.random(), random.random(), random.random()) for job in jobs}
    fig = ff.create_gantt(data, group_tasks=True, show_colorbar=True, colors=colors, index_col='Resource')
    fig['layout']['xaxis'].update({'type': None})
    fig.show()
