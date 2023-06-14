"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *
from .sample_DB import populate_sample_DB


def get_user_email():
    return auth.current_user.get("email") if auth.current_user else None


def get_user_id():
    return auth.current_user.get("id") if auth.current_user else None


def get_time():
    return datetime.datetime.utcnow()


def get_today():
    dt = datetime.datetime.utcnow().today()
    return datetime.datetime(dt.year, dt.month, dt.day)


db.define_table(
    "groups",
    Field("group_name", required=True),
    Field("members", "list:reference auth_user"),
)

db.define_table(
    "tasks",
    Field(
        "created_by", "integer", "reference auth_user", default=lambda: get_user_id()
    ),
    Field("start_time", "datetime", default=get_today()),
    Field("end_time", "datetime", default=get_today()),
    Field("label"),
    Field("description"),
    Field(
        "categorization",
        requires=[
            IS_IN_SET(
                ["personal", "school", "work"],
                # Ensures field atomicity
                multiple=False,
            ),
        ],
    ),
    Field("is_complete", "boolean", label="Completion status", default=False),
    Field("is_group", "boolean", required=True),
    Field("group_id", "reference groups", required=False),
)

db.define_table(
    "kanban_cards",
    Field("task_id", "integer", "reference tasks"),
    Field(
        "column",
        requires=IS_IN_SET(
            ["backlog", "todo", "in_progress", "stuck", "done"],
            # Ensures field atomicity
            multiple=False,
        ),
        default="todo",
    ),
)

db.define_table(
    "task_comments",
    Field("task_id", "reference tasks"),
    Field("comment", required=True),
)

db.define_table(
    "subtasks",
    Field("task_id", "reference tasks"),
    Field("description"),
    Field(
        "is_complete",
        "boolean",
        label="Completion status",
        default=False,
    ),
)

db.define_table(
    "task_reflections",
    Field("task_id", "integer", "reference tasks"),
    # Personal performance metrics, graded on a scale of 1-10 given by slider input
    Field(
        "attentiveness",
        "integer",
        IS_INT_IN_RANGE(1, 11),
        required=True,
    ),
    Field(
        "emotion",
        "integer",
        IS_INT_IN_RANGE(1, 11),
        required=True,
    ),
    Field(
        "efficiency",
        "integer",
        IS_INT_IN_RANGE(1, 11),
        required=True,
    ),
    # Calendar page displays task performance aggregated for each day
    Field(
        "day",
        "datetime",
        default=get_today(),
        label="Date of reflection",
    ),
)

db.define_table(
    "daily_journal",
    Field(
        "user",
        "integer",
        "reference auth_user",
        default=lambda: get_user_id(),
    ),
    Field(
        "day",
        "datetime",
        default=get_today(),
    ),
    Field("entry"),
)

populate_sample_DB()

db.commit()
