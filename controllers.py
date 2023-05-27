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
from .models import get_user_email, get_user_id
import random

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth)
def index():
    print("User:", get_user_email())
    return dict(
        # get_tasks_url = URL("get_tasks")
    )

@action("get_tasks")
@action.uses(db)
def get_tasks():
    board_query = "personal"
    print('HELLO')
    # user_tasks = db(db.tasks.created_by == 6  and db.kanban_cards.task_id == db.tasks.id).select(db.tasks.id).as_list() # HARD CODING THE USER ID # and db.tasks.categorization == board_query
    # user_tasks = db(db.tasks.created_by == 6  and db.kanban_cards.task_id == db.tasks.id).select()
    uncategorized = db.executesql("SELECT 'tasks'.'id' FROM 'tasks' WHERE 'tasks'.'id' NOT IN (SELECT 'kanban_cards'.'task_id' FROM 'kanban_cards')", as_dict=True)
    # print("uncategorized", uncategorized)
    # kanban_categories = ["backlog", "todo", "in_progress", "stuck", "done"]
    # i = 2
    # for task_id in uncategorized:
    #     task_id = task_id["id"]
    #     db.kanban_cards.insert(task_id=task_id, column=kanban_categories[i])
    #     i = (i+1)%5

    todo_tasks =  db((db.kanban_cards.task_id == db.tasks.id) & (db.tasks.categorization == board_query) & (db.kanban_cards.column == "todo")).select().as_list()
    in_progress_tasks = db((db.kanban_cards.task_id == db.tasks.id) & (db.tasks.categorization == board_query) & (db.kanban_cards.column == "in_progress")).select().as_list()
    stuck_tasks = db((db.kanban_cards.task_id == db.tasks.id) & (db.tasks.categorization == board_query) & (db.kanban_cards.column == "stuck")).select().as_list()
    done_tasks = db( (db.kanban_cards.task_id == db.tasks.id) & (db.tasks.categorization == board_query) & (db.kanban_cards.column == "done")).select().as_list() #  (db.tasks.created_by == 108) & 
        # print(id)
    # print("USER TASKS", user_tasks)
    # print("SQL", db._lastsql)
    print("DONE")
    return dict(todo_tasks=todo_tasks, in_progress_tasks=in_progress_tasks, stuck_tasks=stuck_tasks, done_tasks=done_tasks)


@action('kanban')
@action.uses('kanban.html', db, auth.user)
def kanban():
    print("HI")
    return dict(
        get_tasks_url = URL("get_tasks")
    )

