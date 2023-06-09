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
        get_tasks_url = URL("get_tasks")
    )

@action("get_tasks")
@action.uses(db, auth.user, url_signer.verify())
def get_tasks():
    board_query = request.params.get("board")
    
    personal_todo_query = (db.kanban_cards.task_id == db.tasks.id) & (db.tasks.categorization == board_query) & (db.kanban_cards.column == "todo") & (db.tasks.created_by == get_user_id())
    group_todo_query = (db.kanban_cards.task_id == db.tasks.id) & (db.tasks.categorization == board_query) & (db.kanban_cards.column == "todo") & (db.tasks.created_by != get_user_id()) & (db.groups.members.contains(get_user_id())) & (db.groups.id == db.tasks.group_id)
    todo_tasks =  db(personal_todo_query | group_todo_query).select().as_list()

    personal_inprog_query = (db.kanban_cards.task_id == db.tasks.id) & (db.tasks.categorization == board_query) & (db.kanban_cards.column == "in_progress") & (db.tasks.created_by == get_user_id())
    group_inprog_query = (db.kanban_cards.task_id == db.tasks.id) & (db.tasks.categorization == board_query) & (db.kanban_cards.column == "in_progress") & (db.tasks.created_by != get_user_id()) & (db.groups.members.contains(get_user_id())) & (db.groups.id == db.tasks.group_id)
    in_progress_tasks = db(personal_inprog_query | group_inprog_query).select().as_list()

    personal_stuck_query = (db.kanban_cards.task_id == db.tasks.id) & (db.tasks.categorization == board_query) & (db.kanban_cards.column == "stuck") & (db.tasks.created_by == get_user_id())
    group_stuck_query = (db.kanban_cards.task_id == db.tasks.id) & (db.tasks.categorization == board_query) & (db.kanban_cards.column == "stuck") & (db.tasks.created_by != get_user_id()) & (db.groups.members.contains(get_user_id())) & (db.groups.id == db.tasks.group_id)
    stuck_tasks = db(personal_stuck_query | group_stuck_query).select().as_list()

    personal_done_query = (db.kanban_cards.task_id == db.tasks.id) & (db.tasks.categorization == board_query) & (db.kanban_cards.column == "done") & (db.tasks.created_by == get_user_id())
    group_done_query = (db.kanban_cards.task_id == db.tasks.id) & (db.tasks.categorization == board_query) & (db.kanban_cards.column == "done") & (db.tasks.created_by != get_user_id()) & (db.groups.members.contains(get_user_id())) & (db.groups.id == db.tasks.group_id)
    done_tasks = db(personal_done_query | group_done_query).select().as_list()
    
    return dict(todo_tasks=todo_tasks, in_progress_tasks=in_progress_tasks, stuck_tasks=stuck_tasks, done_tasks=done_tasks)


@action('kanban')
@action.uses('kanban.html', db, auth.user, url_signer)
def kanban():
    return dict(
        get_tasks_url = URL("get_tasks", signer=url_signer),
        update_kanban_url = URL("update_kanban", signer=url_signer)
    )

   
@action("update_kanban", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def update_kanban():
    task_id = request.params.get("task_id")
    new_column = request.params.get("new_column")

    kanban_task = db.kanban_cards[task_id]
    db(db.kanban_cards.task_id == task_id).validate_and_update(column=new_column)

    return dict()