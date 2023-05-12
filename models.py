"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_user_id():
    return auth.current_user.get('id') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

# Profile
# Tasks

db.define_table(
    'groups',
    Field("group_name"),
    Field("assoc_user_1", "integer", "references auth_user"),
    Field("assoc_user_2", "integer", "references auth_user"),
    Field("assoc_user_3", "integer", "references auth_user"),
    Field("assoc_user_4", "integer", "references auth_user")
)

db.define_table(
    'tasks',
    Field("created_by", "integer", "reference auth_user", default=get_user_id),
    Field("start_time", "datetime"),
    Field("end_time", "datetime"),
    Field("label"),
    Field("description"),
    Field("categorization"),         # {"personal", "school", "work"}
    Field("is_complete", "boolean"),
    Field("is_group", "boolean"),
    Field("group_id", "reference groups")
)

db.define_table(
    'kanban_cards',
    Field("task_id", "integer", "reference tasks"),
    Field("column")              # {"backlog", "todo", "in_progress", "stuck", "done"}
)

db.define_table(
    'task_comments',
    Field("task_id", "reference tasks"),
    Field("comment")
)

db.define_table(
    'subtasks',
    Field("task_id", "reference tasks"),
    Field("desription"),
    Field("is_complete", "boolean")
)

db.define_table(
    'task_reflections',
    Field("task_id", "integer", "reference tasks"),
    Field("attentiveness", "integer"),       # 1-10 based on sliders
    Field("emotion", "integer"),             # 1-10 based on sliders
    Field("efficiency", "integer"),          # 1-10 based on sliders
    Field("day", "datetime")
)

db.define_table(
    'daily_journal',
    Field("user", "integer", "reference auth_user", default=get_user_id),
    Field("entry"),
    Field("day", "datetime")
)


db.commit()
