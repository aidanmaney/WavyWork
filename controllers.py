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

session, db, T, auth, and templates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

import datetime  # TODO
import random
from .dateutil.relativedelta import relativedelta

from py4web import action, request, abort, redirect, URL
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
from .models import get_user_email

url_signer = URLSigner(session)


@action("index")
@action.uses("index.html", db, auth, url_signer)
def index():
    print("User:", get_user_email())
    return dict()


@action("get_reflections")
@action.uses(db, auth.user, session, url_signer.verify())
def get_reflections():
    prev_month_offset = int(request.params.get("pmo"))

    def day_n_months_ago(day, n):
        return day + relativedelta(months=(-1 * n))

    def productivity_metric(attentiveness, efficiency, emotion):
        # TODO implement
        return random.randint(0, 4)

    today = datetime.datetime.today()
    day_in_month = day_n_months_ago(day=today, n=prev_month_offset)
    first_of_month = day_in_month + relativedelta(day=1)
    last_of_month = day_in_month + relativedelta(day=31)

    reflections_in_month_rows = db(
        (db.task_reflections.day >= first_of_month)
        & (db.task_reflections.day <= last_of_month)
    ).select(
        db.task_reflections.day,
        db.task_reflections.attentiveness,
        db.task_reflections.emotion,
        db.task_reflection.efficiency,
        orderby=db.task_reflections.day,
    )

    reflections_in_month = [
        (
            x["day"],
            productivity_metric(
                x["attentiveness"],
                x["emotion"],
                x["efficiency"],
            ),
        )
        for x in reflections_in_month_rows.as_list()
    ]
    print(reflections_in_month)

    print("REFLECTIONS_IN_MONTH:", reflections_in_month)

    return dict(reflections=reflections_in_month)


@action("profile")
@action.uses("profile.html", db, auth.user, session, url_signer)
def profile():
    get_reflections_url = URL("get_reflections", signer=url_signer)
    print(get_reflections_url)
    return dict(get_reflections_url=get_reflections_url)
