import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

# Load the Jira data
df = pd.read_csv("docs/jira_data.csv")

# Define relevant fields
component_column = "Components"
key_column = "Issue key"
summary_column = "Summary" if "Summary" in df.columns else None  # Fallback if not present

# Filter to only story-level rows with real dependencies
df = df[df[component_column].notna()]

# Combine all dependency columns into one long list
link_columns = [col for col in df.columns if "issue link" in col.lower()]
dependency_rows = []

for _, row in df.iterrows():
    for col in link_columns:
        linked_issue = row[col]
        if pd.notna(linked_issue):
            dependency_rows.append({
                "Component": row[component_column],
                "IssueKey": row[key_column],
                "Summary": row[summary_column] if summary_column else "N/A",
                "LinkedIssue": linked_issue,
                "LinkType": col
            })

# Convert to DataFrame
dependency_df = pd.DataFrame(dependency_rows)

# Group by team/component
grouped = dependency_df.groupby("Component")

# Render using Jinja2
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("dependencies_template.html")

output = template.render(groups=grouped)

with open("docs/dependencies.html", "w") as f:
    f.write(output)

print("✅ dependencies.html regenerated with summaries and keys.")

