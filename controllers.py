"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
import datetime
from .models import get_user_email, get_user_id, get_time, get_today

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth, auth.user, url_signer)
def index():
    return dict(
        add_task_url = URL('add_task', signer=url_signer),
        get_active_tasks_url = URL('get_active_tasks', signer=url_signer),
        submit_task_reflection_url = URL('submit_task_reflection', signer=url_signer),
        get_users_url = URL('get_users', signer=url_signer),
        check_for_submitted_reflections_url = URL('check_for_submitted_reflections', signer=url_signer)
    )


@action('get_users')
@action.uses(db, auth.user, url_signer.verify())
def get_users():
    all_users = db(db.auth_user.id != get_user_id()).select(orderby=db.auth_user.first_name).as_list()
    return dict(all_users=all_users)


@action('add_task', method=["GET", "POST"])
@action.uses(db, url_signer.verify(), auth.user)
def add_task():
    if request.json.get("is_group") and len(request.json.get("members")) > 0:
        members = request.json.get("members") + [get_user_id()]
        group_id = db.groups.insert(
            group_name = request.json.get("group_name"),
            members = members
        )

    date_str_start_time = request.json.get('start_time')
    datetime_start_time = datetime.datetime.strptime(date_str_start_time, '%Y-%m-%d')

    date_str_end_time = request.json.get('end_time')
    datetime_end_time = datetime.datetime.strptime(date_str_end_time, '%Y-%m-%d')

    id = db.tasks.insert(
        label = request.json.get("label"),
        description = request.json.get("description"),
        categorization = request.json.get("categorization"),
        is_group = request.json.get("is_group"),
        start_time = datetime_start_time,
        end_time = datetime_end_time,
        group_id = group_id
    )
    return dict(id=id, created_by=get_user_id())


@action('get_active_tasks')
@action.uses(db, url_signer.verify(), auth.user)
def get_active_tasks():
    active_tasks = db((db.tasks.start_time <= get_today()) &
                      (db.tasks.end_time >= get_today()) & 
                      (db.tasks.created_by == get_user_id())).select().as_list()
    
    return dict(active_tasks=active_tasks)


@action('submit_task_reflection', method=["POST"])
@action.uses(db, auth.user, url_signer.verify())
def submit_task_reflection():
    id = db.task_reflections.insert(
        task_id = request.json.get("task_id"),
        attentiveness = request.json.get("attentiveness"),
        emotion = request.json.get("emotion"),
        efficiency = request.json.get("efficiency")
    )
    return dict(id=id)


@action('check_for_submitted_reflections')
@action.uses(db, auth.user, url_signer.verify())
def check_for_submitted_reflections():
    todays_reflections = db((db.tasks.created_by == get_user_id()) & 
                            (db.task_reflections.task_id == db.tasks.id) &
                            (db.task_reflections.day == get_today())).select().as_list()

    print(todays_reflections)
    return dict(todays_reflections=todays_reflections)

# NOTES ON JOIN QUERIES (like above)
# This is technically a query on two separate db tables, so rows will have the data from both tables include
# This means that, in this case, each element in todays_reflections will have access to all task attributes and all task_reflection attributes
# For example, if I wanted the creator, that is stored in the tasks db, so I would write row.tasks.created_by
# If instead I wanted to access the time the reflection was created, is ask for row.task_reflections.day
# Below is another example that gets all in progress kanban cards that are associated with the logged in user

#test_query = db((db.tasks.created_by == get_user_id()) &
#                (db.kanban_cards.task_id == db.tasks.id) &
#                (db.kanban_cards.column == "in_progress")).select()

@action('timeline_stage')
@action.uses(db, auth.user)
def timeline_stage():
    print('timeline controller')
    
    users_tasks = db(db.tasks.created_by == get_user_id()).select().as_list()


    subtasks_list = []
    for task in users_tasks:
        subtask = db(db.subtasks.task_id == task['id']).select().as_list()
        # print(subtask[0]['is_complete'])
        print('SUB', subtask)
        # if (subtask[0]['is_complete']):
        #     subtasks_list.append(subtask)
        #     print('True')
        # else:
        #     subtasks_list.insert(0, subtask)
        #     print("False")

        sorted_list = sorted(subtask, key=lambda sub: not sub['is_complete'])
        print('SORTED', sorted_list)
        subtasks_list.append(sorted_list)
        
        # print('TASK',task)
    
    # print('DB', task_list)

    # for task in task_list:
    #     print(task)

    print('DEBUG')
    print(subtasks_list)
    return dict(subtasks_list=subtasks_list)
