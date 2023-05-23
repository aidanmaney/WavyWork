import random
import datetime

# References hw5 start code (Credit: Luca de Alfaro)
from py4web.utils.populate import FIRST_NAMES, LAST_NAMES
from .common import db, Field, auth

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
    # Add *consistent* dummy user
    user = dict(
        email="_johndoe" + "@ucsc.edu",
        first_name="John",
        last_name="Doe",
        password="johndoe",
    )
    auth.register(user, send=False)
    db.commit()


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
            end_time=datetime.datetime.today() + datetime.timedelta(days=1),
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


# def add_subtasks_for_testing():
#     db(db.subtasks).delete()
#     for t in sample_tasks:
#         task_label = t[0]
#         task_subtasks = t[2]
#         for st in task_subtasks:
#             task_id = task_id_from_label(task_label)
#             db.subtasks.insert(task_id=task_id, description=st)
#     db.commit()


# def task_id_from_label(task_label):
#     task_id = int(db(db.tasks.label.startswith(task_label)).select("id").first())
#     return task_id


def add_task_reflections_for_testing(task_id_list):
    db(db.task_reflections).delete()

    inserted_task_reflections = []

    # Arbitrary subset of tasks
    reflecting_task_ids = task_id_list[:3]

    for task_id in reflecting_task_ids:
        db(db.tasks.id == task_id).update(is_complete=True)
        task_reflection_id = db.task_reflections.insert(
            task_id=task_id,
            attentiveness=random.randint(1, 10),
            emotion=random.randint(1, 10),
            efficiency=random.randint(1, 10),
        )
        inserted_task_reflections = task_reflection_id

    db.commit()
    return inserted_task_reflections


def add_kanban_cards_for_testing(task_id_list):
    db(db.kanban_cards).delete()

    kanban_categories = ["backlog", "todo", "in_progress", "stuck", "done"]

    # Arbitrary subset of tasks
    kanban_tasks = task_id_list[2:5]

    inserted_kanban_card_ids = []

    for task_id in kanban_tasks:
        kanban_task_id = db.kanban_cards.insert(
            task_id=task_id, column=kanban_categories[random.randint(0, 4)]
        )
        inserted_kanban_card_ids.append(kanban_task_id)

    db.commit()
    return inserted_kanban_card_ids


def populate_sample_DB():
    add_users_for_testing(5)

    added_tasks = add_tasks_for_testing()

    add_subtasks_for_testing(added_tasks)
    add_task_reflections_for_testing(added_tasks)
    add_kanban_cards_for_testing(added_tasks)

    db.commit()
