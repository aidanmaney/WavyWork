import random
import datetime

# References hw5 start code (Credit: Luca de Alfaro)
from py4web.utils.populate import FIRST_NAMES, LAST_NAMES
from dateutil.relativedelta import relativedelta
from .common import db, Field, auth


def get_today():
    dt = datetime.datetime.utcnow().today()
    return datetime.datetime(dt.year, dt.month, dt.day)


sample_tasks = [
    {
        "task_label": "finish my history essay",
        "task_category": "school",
        "task_subtasks": [
            "read chapter 5",
            "find good quotes",
            "sharpen my pencil",
            "write the paper",
            "turn in the essay",
        ],
    },
    {
        "task_label": "find a slug",
        "task_category": "school",
        "task_subtasks": [
            "get my boots on",
            "find an umbrella",
            "find my camera",
            "go on a hike",
        ],
    },
    {
        "task_label": "submit those TPS reports",
        "task_category": "work",
        "task_subtasks": [
            "go to work",
            "open my computer",
            "email people",
            "shred those documents",
            "submit garbage",
        ],
    },
    {
        "task_label": "prep for the accounting interview",
        "task_category": "work",
        "task_subtasks": [
            "email my boss",
            "email the potential new hire",
            "review resumes",
        ],
    },
    {
        "task_label": "do a grocery run",
        "task_category": "personal",
        "task_subtasks": ["buy apples", "buy oranges", "buy milk", "buy bread"],
    },
    {
        "task_label": "open an ice-cream shop",
        "task_category": "personal",
        "task_subtasks": [
            "get a restaurant license",
            "find lease",
            "buy ice",
            "buy cream",
            "make ice cream",
            "open store",
        ],
    },
    {
        "task_label": "pack for the camping trip",
        "task_category": "personal",
        "task_subtasks": [
            "find boots",
            "find fishing pole",
            "find tent",
            "load stuff into car",
            "leave before sunup",
        ],
    },
]

group_tasks = [
    {
        "task_label": "working on personal group project",
        "task_category": "personal",
        "task_subtasks": [
            "read chapter 5",
            "find good quotes",
            "sharpen my pencil",
            "write the paper",
            "turn in the essay",
        ],
    },
    {
        "task_label": "working on work group project",
        "task_category": "work",
        "task_subtasks": [
            "read chapter 5",
            "find good quotes",
            "sharpen my pencil",
            "write the paper",
            "turn in the essay",
        ],
    },
    {
        "task_label": "working on school group project",
        "task_category": "school",
        "task_subtasks": [
            "read chapter 5",
            "find good quotes",
            "sharpen my pencil",
            "write the paper",
            "turn in the essay",
        ],
    },
]


# References hw5 starter code (Credit: Luca de Alfaro)
def add_users_for_testing(num_users):
    # Test user names begin with "_".
    # Counts how many users we need to add.
    db(db.auth_user.email.startswith("_")).delete()
    for k in range(0, num_users):
        first_name = random.choice(FIRST_NAMES)
        last_name = first_name = random.choice(LAST_NAMES)
        username = "_%s%.2i" % (first_name.lower(), k)
        user = dict(
            email=username + "@ucsc.edu",
            first_name=first_name,
            last_name=last_name,
            password=username,  # To facilitate testing.
        )
        auth.register(user, send=False)
    # Add *consistent* dummy users

    user_1 = dict(
        email="_johndoe" + "@ucsc.edu",
        first_name="John",
        last_name="Doe",
        password="johndoe",
    )
    user_2 = dict(
        email="_matjos" + "@ucsc.edu",
        first_name="Mat",
        last_name="Jos",
        password="matjos",
    )
    user_3 = dict(
        email="_alexaidan" + "@ucsc.edu",
        first_name="Alex",
        last_name="Aidan",
        password="alexaidan",
    )

    user_1_id = auth.register(user_1, send=False)
    user_2_id = auth.register(user_2, send=False)
    user_3_id = auth.register(user_3, send=False)
    db.commit()

    return [
        user_1_id,
        user_2_id,
        user_3_id,
    ]


def add_group_tasks_for_testing():
    db(db.groups).delete()

    id_user_1 = (
        db(db.auth_user.email.startswith("_johndoe@ucsc.edu")).select("id").first()
    )
    id_user_2 = (
        db(db.auth_user.email.startswith("_matjos@ucsc.edu")).select("id").first()
    )
    id_user_3 = (
        db(db.auth_user.email.startswith("_alexaidan@ucsc.edu")).select("id").first()
    )

    group_id = db.groups.insert(
        group_name="test_group", members=[id_user_1, id_user_2, id_user_3]
    )

    inserted_tasks = []
    for t in group_tasks:
        task_id = db.tasks.insert(
            label=t["task_label"],
            description="I need to " + t["task_label"],
            end_time=datetime.datetime.today() + datetime.timedelta(days=1),
            categorization=t["task_category"],
            is_group=True,
            group_id=group_id,
            created_by=id_user_2,
        )
        inserted_tasks.append(task_id)
    db.commit()
    return inserted_tasks


def add_tasks_for_testing():
    db(db.tasks).delete()

    id_user_johndoe = (
        db(db.auth_user.email.startswith("_johndoe@ucsc.edu")).select("id").first()
    )

    inserted_tasks = []

    for t in sample_tasks:
        label = t["task_label"]
        task_category = t["task_category"]

        task_id = db.tasks.insert(
            label=label,
            description="I need to " + label,
            end_time=get_today() + relativedelta(day=random.randrange(1, 32)),
            categorization=task_category,
            is_group=False,
            created_by=id_user_johndoe,
        )
        inserted_tasks.append(task_id)

    db.commit()
    return inserted_tasks


def add_subtasks_for_testing(task_id_list):
    db(db.subtasks).delete()

    inserted_subtasks = []

    for i, task_id in enumerate(task_id_list):
        subtasks_list = sample_tasks[i]["task_subtasks"]
        for st in subtasks_list:
            subtask_id = db.subtasks.insert(
                task_id=task_id,
                description=st,
                is_complete=bool(random.randint(0, 1)),
            )
            inserted_subtasks.append(subtask_id)

    db.commit()
    return inserted_subtasks


def add_task_reflections_for_testing(task_id_list):
    db(db.task_reflections).delete()

    inserted_task_reflections = []

    # Arbitrary subset of tasks
    reflecting_task_ids = task_id_list[0 : len(task_id_list) // 2]

    for task_id in reflecting_task_ids:
        db(db.tasks.id == task_id).update(is_complete=True)
        for _ in range(0, 40):
            task_reflection_id = db.task_reflections.insert(
                task_id=task_id,
                attentiveness=random.randint(-2, 10),
                emotion=random.randint(-2, 10),
                efficiency=random.randint(-2, 10),
                day=get_today()
                + relativedelta(
                    day=(random.randrange(1, 32)), month=(random.randrange(4, 7))
                ),
            )
            inserted_task_reflections = task_reflection_id

    db.commit()
    return inserted_task_reflections


def add_kanban_cards_for_testing(task_id_list, delete=True):
    if delete:
        db(db.kanban_cards).delete()

    kanban_categories = ["todo", "in_progress", "stuck", "done"]
    i = 0

    # Arbitrary subset of tasks
    kanban_tasks = task_id_list

    inserted_kanban_card_ids = []

    for task_id in kanban_tasks:
        kanban_task_id = db.kanban_cards.insert(
            task_id=task_id, column=kanban_categories[i]
        )
        inserted_kanban_card_ids.append(kanban_task_id)
        i = (i + 1) % 4

    db.commit()
    return inserted_kanban_card_ids


def add_journal_entries_for_testing(user_ids):
    db(db.daily_journal).delete()

    # Generated by ChatGPT for *flavor*
    entry = """
June 13, 2023

Dear Journal,

Today as a software engineer, I was immersed in an exciting project that presented several challenges. Our team made substantial progress, and it was rewarding to witness the code taking shape. We started the day with a productive stand-up meeting, emphasizing collaboration and communication.

My focus was on integrating a third-party API into our web application, enabling real-time data updates for our users. After thorough research, I delved into the code, configuring API endpoints and addressing authentication and security protocols. Overcoming these challenges brought a sense of accomplishment.

Throughout the day, I collaborated closely with my team, engaging in code reviews and discussions. By the end, I had completed the initial implementation of the feature, conducted testing, and identified areas for refinement. Tomorrow, I aim to further polish the feature and conduct extensive testing to ensure its stability.

Overall, it was a rewarding day as a software engineer, filled with problem-solving, collaboration, and the satisfaction of seeing tangible progress.    """

    reflected_days = (
        db(db.task_reflections)
        .select(
            db.task_reflections.day,
        )
        .as_list()
    )

    for day in reflected_days:
        db.daily_journal.insert(
            user=user_ids[0]["id"],
            day=day["day"],
            entry=entry,
        )


def populate_sample_DB():
    stock_user_ids = add_users_for_testing(5)

    added_tasks = add_tasks_for_testing()
    group_added_tasks = add_group_tasks_for_testing()

    add_subtasks_for_testing(added_tasks)
    add_task_reflections_for_testing(added_tasks)
    add_kanban_cards_for_testing(added_tasks)
    add_kanban_cards_for_testing(group_added_tasks, False)
    add_journal_entries_for_testing(user_ids=stock_user_ids)

    db.commit()
