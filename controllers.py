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
from .models import get_user_email
from .models import get_user_id

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth.user, url_signer)
def index():
    print("User is:", get_user_email())
    print('ID:', get_user_id())
    return dict(
        timeline_stage_url = URL('timeline_stage', signer=url_signer)
    )


@action('timeline_stage')
@action.uses(db, auth.user)
def timeline_stage():
    print('timeline controller')

    task_list = db(db.tasks.created_by == get_user_id()
                   and db.tasks.id == db.subtasks.task_id
                   ).select().as_list()
    
    tasks = db(db.tasks.created_by == get_user_id()).select().as_list()


    sub_tasks = []
    for task in tasks:
        subtask = db(db.subtasks.task_id == task['id']).select().as_list()
        print(subtask)
        sub_tasks.append(subtask)
        # print('TASK',task)
    
    # print('DB', task_list)

    # for task in task_list:
    #     print(task)

    print('DEBUG')
    print(sub_tasks)
    return dict(task_list=task_list)



    # task_list = db(db.tasks).select().as_list()
    # return(task_list=task_list)
