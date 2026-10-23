import random
import sys
from datetime import datetime, timedelta

from sqlalchemy import func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.config import app_settings
from app.database import Base, SessionLocal
from app.models import (
    Comment,
    Project,
    Task,
    TaskPriority,
    TaskStatus,
    User,
    Workspace,
    WorkspaceMember,
    WorkspaceMemberRole,
)
from app.security import hash_password

SEED_PASSWORD = "password123"
SEED_DOMAIN = "teamflow.test"
BULK_WORKSPACE = "Bright Labs"
BULK_TASK_COUNT = 5000

OWNER = WorkspaceMemberRole.OWNER
ADMIN = WorkspaceMemberRole.ADMIN
MEMBER = WorkspaceMemberRole.MEMBER

USER_NAMES: list[tuple[str, str]] = [
    ("Aarav", "Mehta"),
    ("Priya", "Nair"),
    ("Rohan", "Verma"),
    ("Sneha", "Iyer"),
    ("Karan", "Malhotra"),
    ("Ananya", "Reddy"),
    ("Dev", "Patel"),
    ("Meera", "Krishnan"),
    ("Arjun", "Singh"),
    ("Isha", "Kapoor"),
    ("Emily", "Carter"),
    ("Lucas", "Meyer"),
]

WORKSPACE_MEMBERS: dict[str, list[tuple[str, WorkspaceMemberRole]]] = {
    "Northwind Studio": [
        ("Aarav", OWNER),
        ("Priya", ADMIN),
        ("Rohan", MEMBER),
        ("Sneha", MEMBER),
        ("Karan", MEMBER),
        ("Ananya", MEMBER),
        ("Dev", MEMBER),
    ],
    "Bright Labs": [
        ("Meera", OWNER),
        ("Arjun", ADMIN),
        ("Isha", MEMBER),
        ("Emily", MEMBER),
        ("Lucas", MEMBER),
        ("Priya", MEMBER),
        ("Aarav", MEMBER),
    ],
    "Weekend Hacks": [
        ("Aarav", OWNER),
        ("Dev", MEMBER),
    ],
}

PROJECTS: dict[str, list[tuple[str, str]]] = {
    "Northwind Studio": [
        ("Website Redesign", "Fresh look and faster pages for the agency website."),
        ("Mobile App Launch", "Everything needed to ship version 1.0 to both app stores."),
        ("Brand Guidelines", "One shared source for logos, colours, fonts and tone of voice."),
        ("Client Portal", "A place where clients can follow progress and share files."),
    ],
    "Bright Labs": [
        ("Onboarding Flow", "Help new users reach their first success in under five minutes."),
        ("Payments Integration", "Accept payments, handle failures and give support a refund tool."),
        ("Analytics Dashboard", "Product metrics the whole team can check without asking for a report."),
    ],
    "Weekend Hacks": [
        ("Budget Tracker", "A small app to track monthly spending."),
        ("Recipe Finder", "Search recipes by ingredients and dietary needs."),
    ],
}

TASK_NAMES: dict[str, list[str]] = {
    "Website Redesign": [
        "Audit current site navigation",
        "Design new homepage hero section",
        "Build responsive pricing page",
        "Migrate blog posts to new CMS",
        "Fix broken footer links on mobile",
        "Add dark mode toggle",
        "Optimise image loading for Lighthouse score",
        "Write copy for About page",
        "Set up 301 redirects for old URLs",
        "Run accessibility review with screen reader",
        "Add cookie consent banner",
        "Review analytics events with marketing",
    ],
    "Mobile App Launch": [
        "Finalise app store screenshots",
        "Fix crash on Android 12 when opening settings",
        "Add push notification opt-in screen",
        "Prepare release notes for v1.0",
        "Set up crash reporting",
        "Implement offline mode for saved items",
        "Test sign in with Apple on iOS 17",
        "Submit build to TestFlight",
        "Write privacy policy summary for store listing",
        "Speed up cold start time",
        "Add in-app feedback form",
    ],
    "Brand Guidelines": [
        "Collect existing logo variations",
        "Define primary and secondary colour palette",
        "Choose typography pairing",
        "Write voice and tone guide",
        "Design social media templates",
        "Create icon set in SVG",
        "Review guidelines with leadership",
        "Publish brand kit to shared drive",
    ],
    "Client Portal": [
        "Design invoice list screen",
        "Add file upload with progress bar",
        "Build project status timeline",
        "Set up email notifications for new comments",
        "Fix PDF download on Safari",
        "Add two-factor login option",
        "Write onboarding guide for clients",
        "Load test the dashboard with 500 users",
        "Add search to the documents page",
    ],
    "Onboarding Flow": [
        "Map the current sign up funnel",
        "Design three step welcome checklist",
        "Add progress indicator to setup wizard",
        "Send welcome email after verification",
        "Track drop off per onboarding step",
        "A/B test shorter sign up form",
        "Fix duplicate emails on resend verification",
        "Write tooltips for first dashboard visit",
        "Add skip option for team invite step",
    ],
    "Payments Integration": [
        "Compare payment gateway fees",
        "Integrate checkout session API",
        "Handle failed payment webhooks",
        "Add invoice PDF generation",
        "Store only gateway tokens, never card numbers",
        "Build refund flow for support team",
        "Test subscription upgrade proration",
        "Add retry logic for webhook delivery",
        "Write runbook for payment incidents",
        "Set up sandbox accounts for QA",
    ],
    "Analytics Dashboard": [
        "Define the five key product metrics",
        "Build weekly active users chart",
        "Add date range filter",
        "Export report as CSV",
        "Cache slow queries for the overview page",
        "Fix timezone offset in daily charts",
        "Add retention cohort table",
        "Review chart colours for colour blind users",
        "Set up scheduled email report",
    ],
    "Budget Tracker": [
        "Sketch main screens on paper",
        "Set up expense categories",
        "Add monthly budget limit",
        "Import transactions from CSV",
        "Show spending by category as a pie chart",
        "Add recurring expenses",
        "Write tests for currency rounding",
        "Deploy to a small VPS",
    ],
    "Recipe Finder": [
        "Collect twenty sample recipes",
        "Build ingredient search",
        "Add vegetarian and vegan filters",
        "Save favourite recipes",
        "Show cooking time on recipe cards",
        "Scale servings automatically",
        "Fix fractions display for quantities",
        "Add shopping list export",
    ],
}

DESCRIPTIONS: list[str | None] = [
    None,
    None,
    None,
    "Needs review before it can move to testing.",
    "Follow up with the design team if anything is unclear.",
    "See the linked discussion for the agreed approach.",
    "Keep the change small and add a short note in the release log.",
    "A customer reported this twice last week.",
    "Part of the next sprint goal.",
    "Estimate is rough, please update it once you start.",
]

COMMENT_TEXTS: list[str] = [
    "Looks good to me, moving this forward.",
    "I am blocked on the API change, will pick this up tomorrow.",
    "Can we add a short note about this in the release log?",
    "Tested on staging and it works as expected.",
    "I found one edge case, adding the details to the description.",
    "Thanks for picking this up!",
    "Let's discuss this in tomorrow's standup.",
    "Updated the design, please have another look.",
    "This is higher priority than we thought, bumping it.",
    "Done on my side, ready for review.",
]

TASK_VERBS: list[str] = [
    "Fix", "Add", "Refactor", "Update", "Investigate", "Improve",
    "Remove", "Document", "Review", "Optimise", "Migrate", "Test",
]

TASK_OBJECTS: list[str] = [
    "login redirect", "checkout summary", "search results", "profile photo upload",
    "email templates", "notification settings", "dashboard filters", "password reset link",
    "invoice export", "API rate limits", "user permissions", "mobile navigation",
    "date picker", "loading spinner", "audit log",
]

TASK_PLACES: list[str] = [
    "on Safari", "for new users", "in the admin panel", "on slow connections",
    "after the last release", "for enterprise accounts", "on the mobile app",
    "in staging", "for large workspaces", "in the weekly report",
]

STATUSES = list(TaskStatus)
STATUS_WEIGHTS = [30, 25, 15, 25, 5]
PRIORITIES = list(TaskPriority)
PRIORITY_WEIGHTS = [3, 7, 25, 45, 20]
STORY_POINTS = [1, 2, 3, 5, 8, 13]


def database_is_local() -> bool:
    host = make_url(app_settings.DATABASE_URL).host
    return host in ("localhost", "127.0.0.1")


def truncate_all_tables(db: Session) -> None:
    table_names: list[str] = []
    for table in Base.metadata.sorted_tables:
        table_names.append(f'"{table.name}"')
    joined_names = ", ".join(table_names)
    db.execute(text(f"TRUNCATE TABLE {joined_names} RESTART IDENTITY CASCADE"))
    db.commit()


def random_past_time(max_days_ago: int) -> datetime:
    seconds_ago = random.randint(0, max_days_ago * 24 * 60 * 60)
    return datetime.now() - timedelta(seconds=seconds_ago)


def people_in_workspace(workspace_name: str, users: dict[str, User]) -> list[User]:
    people: list[User] = []
    for first_name, _role in WORKSPACE_MEMBERS[workspace_name]:
        people.append(users[first_name])
    return people


def create_users(db: Session) -> dict[str, User]:
    password_hash = hash_password(SEED_PASSWORD)
    users: dict[str, User] = {}
    for first_name, last_name in USER_NAMES:
        email = f"{first_name.lower()}.{last_name.lower()}@{SEED_DOMAIN}"
        user = User(first_name=first_name, last_name=last_name, email=email, password_hash=password_hash)
        db.add(user)
        users[first_name] = user
    db.flush()
    return users


def create_workspaces(db: Session, users: dict[str, User]) -> dict[str, Workspace]:
    workspaces: dict[str, Workspace] = {}
    for workspace_name, members in WORKSPACE_MEMBERS.items():
        workspace = Workspace(name=workspace_name, created_at=datetime.now() - timedelta(days=120))
        db.add(workspace)
        db.flush()
        for first_name, role in members:
            db.add(WorkspaceMember(user_id=users[first_name].id, workspace_id=workspace.id, role=role))
        workspaces[workspace_name] = workspace
    db.flush()
    return workspaces


def create_projects(db: Session, workspaces: dict[str, Workspace]) -> dict[str, Project]:
    projects: dict[str, Project] = {}
    for workspace_name, project_list in PROJECTS.items():
        for project_name, description in project_list:
            created_at = random_past_time(100)
            project = Project(
                workspace_id=workspaces[workspace_name].id,
                name=project_name,
                description=description,
                created_at=created_at,
                updated_at=created_at,
            )
            db.add(project)
            projects[project_name] = project
    db.flush()
    return projects


def make_task(project: Project, name: str, people: list[User]) -> Task:
    now = datetime.now()
    created_at = random_past_time(60)
    seconds_since_created = int((now - created_at).total_seconds())
    updated_at = created_at + timedelta(seconds=random.randint(0, seconds_since_created))

    assignee_choices: list[User | None] = []
    for person in people:
        assignee_choices.append(person)
    assignee_choices.append(None)

    assignee = random.choice(assignee_choices)
    reporter = random.choice(people)

    due_date: datetime | None = None
    if random.random() < 0.8:
        due_date = now + timedelta(days=random.randint(-7, 30))

    return Task(
        project_id=project.id,
        name=name,
        description=random.choice(DESCRIPTIONS),
        assignee_id=assignee.id if assignee is not None else None,
        reporter_id=reporter.id,
        status=random.choices(STATUSES, weights=STATUS_WEIGHTS)[0],
        priority=random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS)[0],
        story_points=random.choice(STORY_POINTS),
        due_date=due_date,
        created_at=created_at,
        updated_at=updated_at,
    )


def make_comments(task: Task, people: list[User]) -> list[Comment]:
    comments: list[Comment] = []
    comment_count = random.choice([0, 0, 0, 1, 1, 2, 3])
    seconds_available = int((datetime.now() - task.created_at).total_seconds())
    for _ in range(comment_count):
        author = random.choice(people)
        created_at = task.created_at + timedelta(seconds=random.randint(0, seconds_available))
        comments.append(
            Comment(
                task_id=task.id,
                user_id=author.id,
                description=random.choice(COMMENT_TEXTS),
                created_at=created_at,
                updated_at=created_at,
            )
        )
    return comments


def create_tasks_and_comments(db: Session, users: dict[str, User], projects: dict[str, Project]) -> None:
    for workspace_name, project_list in PROJECTS.items():
        people = people_in_workspace(workspace_name, users)
        for project_name, _description in project_list:
            project = projects[project_name]
            tasks: list[Task] = []
            for task_name in TASK_NAMES[project_name]:
                tasks.append(make_task(project, task_name, people))
            db.add_all(tasks)
            db.flush()
            for task in tasks:
                db.add_all(make_comments(task, people))


def generated_task_name() -> str:
    verb = random.choice(TASK_VERBS)
    thing = random.choice(TASK_OBJECTS)
    place = random.choice(TASK_PLACES)
    return f"{verb} {thing} {place}"


def create_bulk_tasks(db: Session, users: dict[str, User], workspaces: dict[str, Workspace]) -> None:
    created_at = random_past_time(100)
    project = Project(
        workspace_id=workspaces[BULK_WORKSPACE].id,
        name="Platform Backlog",
        description="Long running list of engineering chores and fixes.",
        created_at=created_at,
        updated_at=created_at,
    )
    db.add(project)
    db.flush()

    people = people_in_workspace(BULK_WORKSPACE, users)
    tasks: list[Task] = []
    for _ in range(BULK_TASK_COUNT):
        tasks.append(make_task(project, generated_task_name(), people))
    db.add_all(tasks)


def print_summary(db: Session) -> None:
    for model in (User, Workspace, Project, Task, Comment):
        count = db.scalar(select(func.count()).select_from(model))
        print(f"{model.__tablename__}: {count}")
    print()
    print(f"Password for every user: {SEED_PASSWORD}")
    print(f"aarav.mehta@{SEED_DOMAIN}   owner of Northwind Studio and Weekend Hacks, member of Bright Labs")
    print(f"priya.nair@{SEED_DOMAIN}    admin of Northwind Studio, member of Bright Labs")
    print(f"rohan.verma@{SEED_DOMAIN}   member of Northwind Studio")
    print(f"meera.krishnan@{SEED_DOMAIN} owner of Bright Labs")
    print(f"arjun.singh@{SEED_DOMAIN}   admin of Bright Labs")


def main() -> None:
    if "--yes" not in sys.argv:
        print("This deletes ALL data in every table. Run again with --yes to continue.")
        return
    if not database_is_local():
        print("Refusing to run: DATABASE_URL is not a local database.")
        return

    random.seed(7)
    db = SessionLocal()
    try:
        truncate_all_tables(db)
        users = create_users(db)
        workspaces = create_workspaces(db, users)
        projects = create_projects(db, workspaces)
        create_tasks_and_comments(db, users, projects)
        if "--bulk" in sys.argv:
            create_bulk_tasks(db, users, workspaces)
        db.commit()
        print_summary(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()