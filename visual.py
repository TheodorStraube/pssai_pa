import plotly.figure_factory as ff
import random

def schedule_to_gantt(execution_plan, jobs):
    plan = execution_plan.plan
    cost = execution_plan.cost()

    data = []

    jobs_names = {job: 'Job {}'.format(n) for n, job in enumerate(jobs)}

    for n, machines_plan in enumerate(plan):
        for start, operation, job in machines_plan:
            data.append({
                'Task': 'Machine {}'.format(n),
                'Resource': jobs_names[job],
                'Start': start,
                'Finish': start + operation.time,
                'Description': '{}, Operation {}. {} - {}'.format(jobs_names[job], job.operations.index(operation), start, start + operation.time)
             })

    colors = {jobs_names[job]: (random.random(), random.random(), random.random()) for job in jobs}
    fig = ff.create_gantt(data, title='Cost: {}'.format(cost), group_tasks=True, show_colorbar=True, colors=colors, index_col='Resource')
    fig['layout']['xaxis'].update({'type': None})
    for d in fig['data']:
        d.update(hoverinfo='text')
    fig.show()
