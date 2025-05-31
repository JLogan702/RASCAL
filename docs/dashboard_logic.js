// dashboard_logic.js
fetch("render_data.json")
  .then((response) => response.json())
  .then((data) => {
    renderSprintReadiness(data.sprint_readiness);
    renderBacklogHealth(data.backlog_health);
    renderProgramSummary(data.program_summary);
    loadDependencies(data.dependencies);
  })
  .catch((error) => {
    console.error("Error loading render_data.json:", error);
  });

// --- Dashboard Rendering Functions ---

function renderSprintReadiness(data) {
  const container = document.getElementById("readinessContainer");
  if (!container) return;

  container.innerHTML = "";
  for (const [team, statuses] of Object.entries(data.teams)) {
    const total = statuses.total;
    const ready = statuses.ready;
    const readiness = total === 0 ? 0 : Math.round((ready / total) * 100);

    const stoplight = getStoplight(readiness);
    const detail = Object.entries(statuses.status_counts)
      .map(([status, count]) => `${status}: ${count}`)
      .join("<br>");

    const card = `
      <div class="card">
        <h3>${team.replace(/_/g, " ")}</h3>
        <img src="${stoplight}" alt="stoplight" class="stoplight">
        <p>Readiness: ${readiness}%</p>
        <p>${detail}</p>
        <small>Tickets must be in a future sprint + 'To Do' or 'Ready for Development'.</small>
      </div>
    `;
    container.innerHTML += card;
  }
}

function renderBacklogHealth(data) {
  const container = document.getElementById("backlogContainer");
  if (!container) return;

  container.innerHTML = "";
  for (const [team, statuses] of Object.entries(data.teams)) {
    const total = statuses.total;
    const groomed = statuses.groomed;
    const health = total === 0 ? 0 : Math.round((groomed / total) * 100);

    const stoplight = getStoplight(health);
    const detail = Object.entries(statuses.status_counts)
      .map(([status, count]) => `${status}: ${count}`)
      .join("<br>");

    const card = `
      <div class="card">
        <h3>${team.replace(/_/g, " ")}</h3>
        <img src="${stoplight}" alt="stoplight" class="stoplight">
        <p>Backlog Health: ${health}%</p>
        <p>${detail}</p>
        <small>Includes only stories not in active sprints + in 'New' or 'Grooming'.</small>
      </div>
    `;
    container.innerHTML += card;
  }
}

function renderProgramSummary(data) {
  const container = document.getElementById("programStoplight");
  if (!container) return;

  const score = Math.round(data.score);
  const stoplight = getStoplight(score);

  container.innerHTML = `<img src="${stoplight}" alt="Program Stoplight" class="stoplight">`;
}

function loadDependencies(data) {
  const container = document.getElementById("dependency-summary");
  if (!container) return;

  const rows = Object.entries(data).map(([key, info]) => {
    const blocks = info.blocks.join(", ");
    return `
      <tr>
        <td><strong>${key}</strong></td>
        <td>${info.summary}</td>
        <td>${blocks}</td>
      </tr>
    `;
  });

  container.innerHTML = `
    <table class="dependency-table">
      <thead>
        <tr><th>Ticket</th><th>Summary</th><th>Blocks / Blocked By</th></tr>
      </thead>
      <tbody>${rows.join("")}</tbody>
    </table>
  `;
}

function getStoplight(percent) {
  if (percent >= 80) return "blinking_green.gif";
  if (percent >= 50) return "blinking_yellow.gif";
  return "blinking_red.gif";
}

