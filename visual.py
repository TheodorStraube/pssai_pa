import plotly.figure_factory as ff
import random

def schedule_to_gantt(schedule, jobs):
    data = []

    jobs_names = {job: 'Job {}'.format(n) for n, job in enumerate(jobs)}

    for n, machines_plan in enumerate(schedule):
        for start, operation, job in machines_plan:
            data.append({
                'Task': 'Machine {}'.format(n),
                'Resource': jobs_names[job],
                'Start': start,
                'Finish': start + operation.time
             })

    colors = {jobs_names[job]: (random.random(), random.random(), random.random()) for job in jobs}
    fig = ff.create_gantt(data, group_tasks=True, show_colorbar=True, colors=colors, index_col='Resource')
    fig['layout']['xaxis'].update({'type': None})
    fig.show()
