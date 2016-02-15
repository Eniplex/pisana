import asana
from dateutil import parser
import re
import matplotlib.pyplot as plt
import collections
import numpy as np
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('pisana.cfg')
ACCESS_TOKEN = config.get('Asana', 'UserToken')
SPRINT_ID = config.getint('Asana', 'Sprint')


def get_story_points(task):
    task_name = task['name']
    match = re.match(r"^\[(\d*)\]", task_name)
    return int(match.group(1))


def create_burdown_table():
    # connect to asana
    client = asana.Client.access_token(ACCESS_TOKEN)

    # get the project
    project = client.projects.find_by_id(SPRINT_ID)
    project_created_at = parser.parse(project['created_at']).replace(tzinfo=None).date()
    project_due_on = parser.parse(project['due_date']).date()

    days = {}
    sum_points = 0
    tasks = client.tasks.find_all({ 'project': SPRINT_ID }, page_size=100)
    for task in tasks:
        fullTask = client.tasks.find_by_id(task['id'])

        task_completed_at = parser.parse(fullTask['due_on']).date()
        points = get_story_points(fullTask)
        sum_points += points

        if fullTask['completed'] == True:
            day = (task_completed_at - project_created_at).days + 1
            if days.has_key(day) == False:
                days.update({day: points})
            else:
                days[day] += points

    days[0] = 0
    burndown_data = collections.OrderedDict(sorted(days.items()))
    remaining_points = sum_points
    for i in range(0, len(burndown_data)):
        remaining_points -= burndown_data[i]
        burndown_data[i] = remaining_points

    predicted_days = (project_due_on - project_created_at).days + 1

    return (predicted_days, sum_points, burndown_data)

(predicted_days, sum_points, days) = create_burdown_table()
plt.xlabel("Days")
plt.ylabel("Doints")
plt.plot(days.keys(), days.values())

plt.plot(range(0, predicted_days), np.linspace(start=sum_points, stop=0, num=predicted_days))
plt.show()



