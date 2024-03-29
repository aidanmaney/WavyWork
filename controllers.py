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
import yatl.helpers
from yatl.helpers import *
from .common import (
    db,
    session,
    T,
    cache,
    auth,
    logger,
    authenticated,
    unauthenticated,
    flash,
)
from py4web.utils.url_signer import URLSigner
import datetime
from .models import get_user_email, get_user_id, get_time, get_today
from py4web.utils.form import Form, FormStyleBulma
from itertools import groupby

from dateutil.relativedelta import relativedelta

url_signer = URLSigner(session)


@action("index")
@action.uses("index.html", auth.user, url_signer)
def index():
    return dict(
        add_task_url=URL("add_task", signer=url_signer),
        get_active_tasks_url=URL("get_active_tasks", signer=url_signer),
        submit_task_reflection_url=URL("submit_task_reflection", signer=url_signer),
        get_users_url=URL("get_users", signer=url_signer),
        check_for_submitted_reflections_url=URL(
            "check_for_submitted_reflections", signer=url_signer
        ),
        submit_journal_entry_url=URL("submit_journal_entry", signer=url_signer),
        get_all_users_tasks_url=URL("get_all_users_tasks", signer=url_signer),

        get_task_subtasks_url=URL("get_task_subtasks", signer=url_signer),
        get_group_members_url=URL("get_group_members", signer=url_signer),
        toggle_task_complete_url = URL("toggle_task_complete", signer=url_signer),
        toggle_subtask_complete_url=URL("toggle_subtask_complete", signer=url_signer),
        add_new_subtask_url=URL("add_new_subtask", signer=url_signer),
    )


@action("get_users")
@action.uses(auth.user, url_signer.verify())
def get_users():
    all_users = (
        db(db.auth_user.id != get_user_id())
        .select(orderby=db.auth_user.first_name)
        .as_list()
    )
    return dict(all_users=all_users)


@action("add_task", method=["GET", "POST"])
@action.uses(url_signer.verify(), auth.user)
def add_task():
    group_id = None
    if request.json.get("is_group") and len(request.json.get("members")) > 0:
        members = request.json.get("members") + [get_user_id()]
        group_id = db.groups.insert(
            group_name=request.json.get("group_name"), members=members
        )

    date_str_start_time = request.json.get("start_time")
    datetime_start_time = datetime.datetime.strptime(date_str_start_time, "%Y-%m-%d")

    date_str_end_time = request.json.get("end_time")
    datetime_end_time = datetime.datetime.strptime(date_str_end_time, "%Y-%m-%d")

    id = db.tasks.insert(
        label=request.json.get("label"),
        description=request.json.get("description"),
        categorization=request.json.get("categorization"),
        is_group=request.json.get("is_group"),
        start_time=datetime_start_time,
        end_time=datetime_end_time,
        group_id=group_id,
    )
    db.kanban_cards.insert(
        task_id=id,
    )
    return dict(id=id, created_by=get_user_id())


@action("get_reflections")
@action.uses(auth.user, url_signer.verify())
def get_reflections():
    prev_month_offset = int(request.params.get("pmo"))

    def day_n_months_ago(day, n):
        return day + relativedelta(months=(-1 * n))

    def productivity_metric(ref):
        # Sum across constituents
        productivity_level = ref["attentiveness"] + ref["efficiency"] + ref["emotion"]
        # Normalize to percentage
        productivity_level /= 30

        # Range from [0, 4]
        productivity_level *= 4

        # First quartile
        if productivity_level < 1:
            productivity_level = 1
        # Second quartile
        elif productivity_level >= 1 and productivity_level < 2:
            productivity_level = 2
        # Third and fourth quartile
        else:
            productivity_level = 3

        return productivity_level

    def calendar_day_in_month(day):
        return int(day.strftime("%d"))

    today = datetime.datetime.today()
    arbitrary_day_in_month = day_n_months_ago(day=today, n=prev_month_offset)
    # The plus (+) denotes an update operation rather than summing
    first_of_month = arbitrary_day_in_month + relativedelta(day=1)
    last_of_month = arbitrary_day_in_month + relativedelta(day=31)

    month = arbitrary_day_in_month.month
    year = arbitrary_day_in_month.year

    month_str = arbitrary_day_in_month.strftime("%B")
    year_str = arbitrary_day_in_month.strftime("%Y")

    if last_of_month > today:
        last_of_month = today

    n_days_in_month = 1 + (
        calendar_day_in_month(last_of_month) - calendar_day_in_month(first_of_month)
    )

    first_ref_day = (
        db(db.task_reflections)
        .select(db.task_reflections.day, orderby=db.task_reflections.day)
        .first()
    )

    first_journal_day = (
        db(db.daily_journal)
        .select(db.daily_journal.day, orderby=db.daily_journal.day)
        .first()
    )

    first_log = min(first_journal_day.day, first_ref_day.day)
    max_pmo = relativedelta(get_today(), first_log).months

    reflections_in_month_rows = (
        db(
            (db.task_reflections.day >= first_of_month)
            & (db.task_reflections.day <= last_of_month)
            & (
                (db.tasks.created_by == get_user_id())
                | (
                    db.tasks.created_by
                    != get_user_id()
                    & (db.groups.members.contains(get_user_id()))
                    & (db.groups.id == db.tasks.group_id)
                )
            )
            & (db.task_reflections.task_id == db.tasks.id)
        )
        .select(
            db.task_reflections.id,
            db.task_reflections.day,
            db.task_reflections.attentiveness,
            db.task_reflections.emotion,
            db.task_reflections.efficiency,
            orderby=db.task_reflections.day,
        )
        .as_list()
    )

    reflections_in_month = [
        dict(
            day=i + 1,
            prod_lvl=0,
            # Interpolate dates
            day_datetime=datetime.date(year=year, month=month, day=i + 1),
        )
        for i in range(n_days_in_month)
    ]

    groups = groupby(
        reflections_in_month_rows, lambda x: calendar_day_in_month(x["day"])
    )

    for group in groups:
        day_idx = group[0] - 1

        prod_metrics_for_day = [productivity_metric(x) for x in group[1]]
        day_avg_productivity = round(
            sum(prod_metrics_for_day) / len(prod_metrics_for_day)
        )
        reflections_in_month[day_idx]["prod_lvl"] = day_avg_productivity

    start_of_month_offset = first_of_month.weekday()

    print(reflections_in_month)

    return dict(
        reflections=reflections_in_month,
        start_of_month_offset=start_of_month_offset,
        month=month_str,
        year=year_str,
        max_pmo=max_pmo,
    )


@action("profile", method=["GET", "POST"])
@action.uses("profile.html", url_signer, auth.user)
def profile():
    get_reflections_url = URL("get_reflections", signer=url_signer)
    get_journal_entry_by_day_url = URL("get_journal_entry_by_day", signer=url_signer)

    user_goals_record = (
        db(db.high_level_goals.user == get_user_id()).select().first() or None
    )

    form = Form(
        db.high_level_goals,
        record=user_goals_record,
        deletable=False,
        keep_values=True,
        csrf_session=session,
        formstyle=FormStyleBulma,
        submit_value="Save",
        show_id=False,
    )

    form.structure.find("[class=label]")[0]["_class"] = "is-hidden"
    form.structure.find("[class=label]")[0]["_class"] = "is-hidden"
    form.structure.find("[class=label]")[0]["_class"] = "is-hidden"

    return dict(
        get_reflections_url=get_reflections_url,
        get_journal_entry_by_day_url=get_journal_entry_by_day_url,
        form=form,
    )


@action("submit_task_reflection", method=["POST"])
@action.uses(auth.user, url_signer.verify())
def submit_task_reflection():
    id = db.task_reflections.update_or_insert(
        task_id=request.json.get("task_id"),
        attentiveness=request.json.get("attentiveness"),
        emotion=request.json.get("emotion"),
        efficiency=request.json.get("efficiency"),
    )
    return dict(
        id=id,
    )


@action("submit_journal_entry", method=["POST"])
@action.uses(auth.user, url_signer.verify())
def submit_journal_entry():
    id = db.daily_journal.insert(entry=request.json.get("entry"))
    return dict(id=id)


@action("check_for_submitted_reflections")
@action.uses(auth.user, url_signer.verify())
def check_for_submitted_reflections():
    todays_reflections = (
        db(
            (db.tasks.created_by == get_user_id())
            & (db.task_reflections.task_id == db.tasks.id)
            & (db.task_reflections.day == get_today())
        )
        .select()
        .as_list()
    )

    print(todays_reflections)
    return dict(todays_reflections=todays_reflections)


@action("get_tasks")
@action.uses(auth.user, url_signer.verify())
def get_tasks():
    board_query = request.params.get("board")

    personal_todo_query = (
        (db.kanban_cards.task_id == db.tasks.id)
        & (db.tasks.categorization == board_query)
        & (db.tasks.is_complete == False)
        & (db.kanban_cards.column == "todo")
        & (db.tasks.created_by == get_user_id())
    )
    group_todo_query = (
        (db.kanban_cards.task_id == db.tasks.id)
        & (db.tasks.categorization == board_query)
        & (db.tasks.is_complete == False)
        & (db.kanban_cards.column == "todo")
        & (db.tasks.created_by != get_user_id())
        & (db.groups.members.contains(get_user_id()))
        & (db.groups.id == db.tasks.group_id)
    )
    todo_tasks = db(personal_todo_query | group_todo_query).select().as_list()

    personal_inprog_query = (
        (db.kanban_cards.task_id == db.tasks.id)
        & (db.tasks.categorization == board_query)
        & (db.tasks.is_complete == False)
        & (db.kanban_cards.column == "in_progress")
        & (db.tasks.created_by == get_user_id())
    )
    group_inprog_query = (
        (db.kanban_cards.task_id == db.tasks.id)
        & (db.tasks.categorization == board_query)
        & (db.tasks.is_complete == False)
        & (db.kanban_cards.column == "in_progress")
        & (db.tasks.created_by != get_user_id())
        & (db.groups.members.contains(get_user_id()))
        & (db.groups.id == db.tasks.group_id)
    )
    in_progress_tasks = (
        db(personal_inprog_query | group_inprog_query).select().as_list()
    )

    personal_stuck_query = (
        (db.kanban_cards.task_id == db.tasks.id)
        & (db.tasks.categorization == board_query)
        & (db.tasks.is_complete == False)
        & (db.kanban_cards.column == "stuck")
        & (db.tasks.created_by == get_user_id())
    )
    group_stuck_query = (
        (db.kanban_cards.task_id == db.tasks.id)
        & (db.tasks.categorization == board_query)
        & (db.tasks.is_complete == False)
        & (db.kanban_cards.column == "stuck")
        & (db.tasks.created_by != get_user_id())
        & (db.groups.members.contains(get_user_id()))
        & (db.groups.id == db.tasks.group_id)
    )
    stuck_tasks = db(personal_stuck_query | group_stuck_query).select().as_list()

    personal_done_query = (
        (db.kanban_cards.task_id == db.tasks.id)
        & (db.tasks.categorization == board_query)
        & (db.tasks.is_complete == False)
        & (db.kanban_cards.column == "done")
        & (db.tasks.created_by == get_user_id())
    )
    group_done_query = (
        (db.kanban_cards.task_id == db.tasks.id)
        & (db.tasks.categorization == board_query)
        & (db.tasks.is_complete == False)
        & (db.kanban_cards.column == "done")
        & (db.tasks.created_by != get_user_id())
        & (db.groups.members.contains(get_user_id()))
        & (db.groups.id == db.tasks.group_id)
    )
    done_tasks = db(personal_done_query | group_done_query).select().as_list()

    return dict(
        todo_tasks=todo_tasks,
        in_progress_tasks=in_progress_tasks,
        stuck_tasks=stuck_tasks,
        done_tasks=done_tasks,
    )


@action("kanban")
@action.uses("kanban.html", auth.user, url_signer)
def kanban():
    return dict(
        get_tasks_url=URL("get_tasks", signer=url_signer),
        update_kanban_url=URL("update_kanban", signer=url_signer),
    )


@action("update_kanban", method="POST")
@action.uses(auth.user, url_signer.verify())
def update_kanban():
    task_id = request.params.get("task_id")
    new_column = request.params.get("new_column")

    kanban_task = db.kanban_cards[task_id]
    db(db.kanban_cards.task_id == task_id).validate_and_update(column=new_column)

    return dict()


@action("get_journal_entry_by_day", method=["POST"])
@action.uses(auth.user)
def get_journal_entry_by_day():
    print(request.json.get("day"))
    journal_day = request.json.get("day")
    journal_datetime = datetime.datetime.strptime(journal_day, "%Y-%m-%d")
    print(f"**********journal_datetime: {journal_datetime} **********")
    entries = (
        db(
            (db.daily_journal.user == get_user_id())
            & (db.daily_journal.day == journal_datetime)
        )
        .select(db.daily_journal.entry)
        .as_list()
    )

    print(f"*********{entries}*********")
    entry = "" if len(entries) <= 0 else entries[0]["entry"]
    return dict(entry=entry)


@action("get_active_tasks")
@action.uses(url_signer.verify(), auth.user)
def get_active_tasks():
    active_user_tasks = (
        db(
            (db.tasks.start_time <= get_today())
            & (db.tasks.end_time >= get_today())
            & (db.tasks.created_by == get_user_id())
        )
        .select()
        .as_list()
    )

    active_group_tasks_tuple = (
        db(
            (db.tasks.created_by != get_user_id())
            & (db.groups.members.contains(get_user_id()))
            & (db.groups.id == db.tasks.group_id)
            & (db.tasks.start_time <= get_today())
            & (db.tasks.end_time >= get_today())
        )
        .select()
        .as_list()
    )

    active_group_tasks = [row["tasks"] for row in active_group_tasks_tuple]
    active_tasks = active_user_tasks + active_group_tasks

    return dict(active_tasks=active_tasks)


@action("get_all_users_tasks")
@action.uses(url_signer.verify())
def get_all_users_tasks():
    tasks_by_user = db(db.tasks.created_by == get_user_id()).select().as_list()

    tasks_from_groups_tuple = (
        db(
            (db.tasks.created_by != get_user_id())
            & (db.groups.members.contains(get_user_id()))
            & (db.groups.id == db.tasks.group_id)
        )
        .select()
        .as_list()
    )

    tasks_from_group = [row["tasks"] for row in tasks_from_groups_tuple]
    all_users_tasks = tasks_by_user + tasks_from_group

    # Filter out any tasks that are not complete
    all_users_tasks = [t for t in all_users_tasks if not t.get('is_complete', True)]

    return dict(all_users_tasks=all_users_tasks)


@action("get_task_subtasks")
@action.uses(auth.user, url_signer.verify())
def get_task_subtasks():
    task_id = request.params.get("task_id")
    subtasks = db(db.subtasks.task_id == task_id).select().as_list()

    return dict(subtasks=subtasks)


@action("get_group_members")
@action.uses(auth.user, url_signer.verify())
def get_group_members():
    group_members_ids = (
        db(db.groups.id == request.params.get("group_id"))
        .select(db.groups.members)
        .as_list()[0]["members"]
    )
    group_members = db(db.auth_user.id.belongs(group_members_ids)).select().as_list()

    return dict(group_members=group_members)


@action("toggle_subtask_complete", method=["POST"])
@action.uses(auth.user, url_signer.verify())
def toggle_substask_complete():
    subtask = db.subtasks[request.json.get("subtask_id")]
    print(request.json.get("subtask_id"))
    print(subtask)
    new_complete = not subtask.is_complete
    db(db.subtasks.id == request.json.get("subtask_id")).update(
        is_complete=new_complete
    )


@action("toggle_task_complete", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def toggle_task_complete():
    task_id = request.json.get("task_id")
    db(db.tasks.id == task_id).update(is_complete=True)


@action("add_new_subtask", method=["POST"])
@action.uses(auth.user, url_signer.verify())
def add_new_subtask():
    id = db.subtasks.insert(
        task_id=request.json.get("task_id"), description=request.json.get("description")
    )

    return dict(id=id)


@action("about")
@action.uses("about.html", auth, session)
def add_new_subtask():
    return dict()
