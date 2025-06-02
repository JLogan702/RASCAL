import pandas as pd
from jinja2 import Environment, FileSystemLoader

# Constants
CSV_PATH = "docs/jira_data.csv"  # <- Rename your uploaded file to match this
TEMPLATE_FILE = "program_summary_template.html"
OUTPUT_FILE = "docs/index.html"

SPRINT_FIELD = "Sprint"
TEAM_FIELD = "Components"
STATUS_FIELD = "Status"
ISSUE_TYPE_FIELD = "Issue Type"

READINESS_STATUSES = ["Ready for Development", "To Do"]
BACKLOG_STATUSES = ["New", "Grooming", "Backlog"]

THRESHOLDS = {
    "green": 80,
    "yellow": 50
}

TEAM_ORDER = [
    "Data Science",
    "Design",
    "Engineering - AI Ops",
    "Engineering - Platform",
    "Engineering - Product"
]

def calculate_scores(df):
    readiness_scores = []
    backlog_scores = []

    for team in TEAM_ORDER:
        team_df = df[df[TEAM_FIELD] == team]

        # Sprint Readiness: assume any non-null sprint means "future"
        future_sprint_df = team_df[team_df[SPRINT_FIELD].notnull()]
        if not future_sprint_df.empty:
            readiness_total = len(future_sprint_df)
            readiness_ready = future_sprint_df[future_sprint_df[STATUS_FIELD].isin(READINESS_STATUSES)]
            readiness_score = round((len(readiness_ready) / readiness_total) * 100, 1)
        else:
            readiness_score = 0.0
        readiness_scores.append(readiness_score)

        # Backlog Health: story tickets NOT assigned to a sprint
        backlog_df = team_df[team_df[SPRINT_FIELD].isnull()]
        backlog_total = len(backlog_df)
        backlog_relevant = backlog_df[backlog_df[STATUS_FIELD].isin(BACKLOG_STATUSES)]
        if backlog_total > 0:
            backlog_score = round((len(backlog_relevant) / backlog_total) * 100, 1)
        else:
            backlog_score = 0.0
        backlog_scores.append(backlog_score)

    avg_readiness = round(sum(readiness_scores) / len(readiness_scores), 1)
    avg_backlog = round(sum(backlog_scores) / len(backlog_scores), 1)
    overall_score = round((avg_readiness + avg_backlog) / 2, 1)

    if overall_score >= THRESHOLDS["green"]:
        stoplight = "blinking_green.gif"
    elif overall_score >= THRESHOLDS["yellow"]:
        stoplight = "blinking_yellow.gif"
    else:
        stoplight = "blinking_red.gif"

    return {
        "readiness": avg_readiness,
        "backlog": avg_backlog,
        "overall": overall_score,
        "stoplight": stoplight
    }

def render_html(data):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(TEMPLATE_FILE)
    output = template.render(data=data)
    with open(OUTPUT_FILE, "w") as f:
        f.write(output)
    print("✅ index.html (Program Summary) generated")

def main():
    df = pd.read_csv(CSV_PATH)
    df = df[(df[ISSUE_TYPE_FIELD] == "Story") & (df[STATUS_FIELD] != "Done")]
    summary_data = calculate_scores(df)
    render_html(summary_data)

if __name__ == "__main__":
    main()

