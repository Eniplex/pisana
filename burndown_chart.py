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

    if match is None:
        return 0

    return int(match.group(1))


def create_burdown_table():
    # connect to asana
    client = asana.Client.access_token(ACCESS_TOKEN)

    # get the project
    project = client.projects.find_by_id(SPRINT_ID)

    # calculate dates
    project_created_at = parser.parse(project['created_at']).replace(tzinfo=None).date()
    project_due_on = parser.parse(project['due_date']).date()
    predicted_days = (project_due_on - project_created_at).days + 1

    days = {}
    sum_points = 0
    tasks = client.tasks.find_all({ 'project': SPRINT_ID }, page_size=100)
    for task in tasks:
        full_task = client.tasks.find_by_id(task['id'])

        points = get_story_points(full_task)
        sum_points += points

        if full_task['completed'] == True:
            task_completed_at = parser.parse(full_task['completed_at']).date()

            # +1 because task completed during the day is counted as work belong to end of the day
            day = (task_completed_at - project_created_at).days + 1
            if not days.has_key(day):
                days.update({day: points})
            else:
                days[day] += points

    burndown_data = collections.OrderedDict(sorted(days.items()))
    burndown_chart = collections.OrderedDict()
    burndown_chart[0] = sum_points

    print('Burndown: ')
    for i in range(1, predicted_days+1):
        burned =  burndown_data[i] if burndown_data.has_key(i) else 0
        burndown_chart[i] = burndown_chart[i-1] - burned
        print('Day %s: %i (%i)' % (i, burned,  burndown_chart[i]))

    return predicted_days, sum_points, burndown_chart


if __name__ == "__main__":
    (predicted_days, sum_points, days) = create_burdown_table()
    plt.xlabel("Days")
    plt.ylabel("Points")
    plt.plot(days.keys(), days.values())

    plt.plot(range(0, predicted_days+1), np.linspace(start=sum_points, stop=0, num=(predicted_days+1)))
    plt.show()



