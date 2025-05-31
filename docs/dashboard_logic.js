async function loadDashboard(type) {
  const response = await fetch("render_data.json");
  const data = await response.json();
  const containerId = {
    sprint_readiness: "readinessContainer",
    backlog_health: "backlogContainer",
    dependencies: "dependencyContainer"
  }[type];

  const container = document.getElementById(containerId);
  const readinessStatuses = ["Ready for Development", "To Do"];

  const statusColors = {
    "Ready for Development": "ready",
    "To Do": "ready"
  };

  data[type].forEach(team => {
    const stoplightSrc = `blinking_${team.stoplight.toLowerCase()}.gif`;

    const card = document.createElement("div");
    card.className = "team-box";

    const title = document.createElement("h3");
    title.textContent = team.team;

    const stoplight = document.createElement("div");
    stoplight.className = "stoplight";
    stoplight.innerHTML = `<img src="${stoplightSrc}" alt="${team.stoplight} light" />`;

    const score = document.createElement("div");
    score.className = "metric-score";
    score.textContent = `${type === "sprint_readiness" ? "Readiness" : "Backlog Health"}: ${team.percentage}%`;

    const statusTable = document.createElement("div");
    statusTable.className = "status-summary";

    const allStatuses = Object.entries(team.statuses || {}).sort((a, b) => {
      return b[1] - a[1]; // sort by count desc
    });

    let tableHTML = `<table><thead><tr><th>Status</th><th>Story Tickets</th></tr></thead><tbody>`;
    allStatuses.forEach(([status, count]) => {
      const className = readinessStatuses.includes(status) ? "ready" : "not-ready";
      tableHTML += `<tr class="${className}"><td>${status}</td><td>${count}</td></tr>`;
    });
    tableHTML += `</tbody></table>`;
    statusTable.innerHTML = tableHTML;

    card.appendChild(title);
    card.appendChild(stoplight);
    card.appendChild(score);
    card.appendChild(statusTable);

    container.appendChild(card);
  });

  const now = new Date();
  document.getElementById("lastUpdated").textContent = now.toLocaleString();
}

