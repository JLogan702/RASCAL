import pandas as pd
import json
import numpy as np

# Load Jira CSV
df = pd.read_csv("jira_data.csv")

# Normalize column names
df.columns = df.columns.str.strip()

# Rename fields for ease
df.rename(columns={
    "Issue key": "Key",
    "Summary": "Summary",
    "Status": "Status",
    "Issue Type": "Issue Type",
    "Components": "Team",
    "Sprint": "Sprint",
    "Inward issue link (Blocks)": "Inward",
    "Outward issue link (Blocks)": "Outward"
}, inplace=True)

# Only Story tickets
df = df[df["Issue Type"].str.lower() == "story"]

# Known Teams
teams = df["Team"].dropna().unique()

# Readiness criteria
readiness_statuses = ["To Do", "Ready for Development"]
backlog_statuses = ["New", "Grooming"]
ignore_statuses = ["Done", "Blocked", "Cancelled", "In Progress"]

# Helper: is future sprint
def is_future_sprint(val):
    if pd.isna(val):
        return False
    return "state=active" not in str(val).lower() and "state=closed" not in str(val).lower()

# Prep containers
sprint_readiness = {}
backlog_health = {}
dependencies = {}

for team in teams:
    team_df = df[df["Team"] == team]

    # Sprint Readiness
    future_df = team_df[team_df["Sprint"].apply(is_future_sprint)]
    total_ready = len(future_df)
    ready_status_count = future_df[future_df["Status"].isin(readiness_statuses)].shape[0]

    readiness_pct = round((ready_status_count / total_ready) * 100, 1) if total_ready > 0 else 0
    sprint_readiness[team] = {
        "readiness": readiness_pct,
        "total": total_ready,
        "statuses": future_df["Status"].value_counts().to_dict()
    }

    # Backlog Health
    backlog_df = team_df[
        (team_df["Sprint"].isna() | ~team_df["Sprint"].apply(lambda x: "state=active" in str(x)))
        & ~team_df["Status"].isin(ignore_statuses)
    ]

    total_backlog = len(backlog_df)
    healthy_count = backlog_df[backlog_df["Status"].isin(backlog_statuses)].shape[0]
    health_pct = round((healthy_count / total_backlog) * 100, 1) if total_backlog > 0 else 0

    backlog_health[team] = {
        "health": health_pct,
        "total": total_backlog,
        "statuses": backlog_df["Status"].value_counts().to_dict()
    }

# Dependencies
for _, row in df.iterrows():
    key = row["Key"]
    summary = row["Summary"]
    inward = row.get("Inward", "")
    outward = row.get("Outward", "")
    blocks = []

    if pd.notna(inward):
        blocks += [x.strip() for x in str(inward).split(",") if x.strip()]
    if pd.notna(outward):
        blocks += [x.strip() for x in str(outward).split(",") if x.strip()]

    if blocks:
        dependencies[key] = {"summary": summary, "blocks": blocks}

# Program Summary — average across teams
avg_readiness = np.mean([v["readiness"] for v in sprint_readiness.values()])
avg_health = np.mean([v["health"] for v in backlog_health.values()])
overall_score = round((avg_readiness + avg_health) / 2, 1)

stoplight = "green" if overall_score >= 80 else "yellow" if overall_score >= 50 else "red"

program_summary = {
    "score": overall_score,
    "stoplight": stoplight
}

# Save output
with open("docs/render_data.json", "w") as f:
    json.dump({
        "sprint_readiness": sprint_readiness,
        "backlog_health": backlog_health,
        "dependencies": dependencies,
        "program_summary": program_summary
    }, f, indent=2)

