function loadDashboard(page) {
  fetch("render_data.json")
    .then(response => response.json())
    .then(data => {
      if (page === "sprint_readiness") renderSprintReadiness(data.sprint_readiness);
      else if (page === "backlog_health") renderBacklogHealth(data.backlog_health);
      else if (page === "dependencies") loadDependencies(data.dependencies);
      else if (page === "program_summary") renderProgramSummary(data.program_summary);
    })
    .catch(error => {
      console.error("Failed to load dashboard data:", error);
    });
}

// Utility: Format date
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString(undefined, { dateStyle: "long", timeStyle: "short" });
}

