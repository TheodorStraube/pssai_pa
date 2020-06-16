import plotly.figure_factory as ff
import random

def schedule_to_gantt(schedule, jobs):
    data = []

    for n, machines_plan in enumerate(schedule):
        for start, operation, job in machines_plan:
            data.append({
                'Task': 'Machine {}'.format(n),
                'Resource': str(job),
                'Start': start,
                'Finish': start + operation.time
             })

    colors = {str(job): (random.random(), random.random(), random.random()) for job in jobs}
    fig = ff.create_gantt(data, group_tasks=True, show_colorbar=True, colors=colors, index_col='Resource')
    fig['layout']['xaxis'].update({'type': None})
    fig.show()
