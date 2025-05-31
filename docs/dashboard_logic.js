document.addEventListener("DOMContentLoaded", () => {
  fetch("jira_data.csv")
    .then(response => response.text())
    .then(data => {
      const rows = data.trim().split("\n").slice(1); // skip header
      const parsedData = rows.map(row => {
        const cols = row.split(",");
        return {
          component: cols[24].trim(), // Components (column Y, index 24)
          status: cols[7].trim(),     // Status (assumed)
          sprint: cols[165].trim(),   // Sprint (column FK, index 165)
          summary: cols[3].trim(),    // Summary (column D, index 3)
          key: cols[0].trim(),        // Issue Key (column A)
          inward: cols[50].trim(),    // Inward link (AY, index 50)
          outward: cols[51].trim()    // Outward link (AZ, index 51)
        };
      });

      const teams = [
        "Engineering - Product",
        "Engineering - Platform",
        "Engineering - AI Ops",
        "Design",
        "Data Science"
      ];

      teams.forEach(team => {
        const teamData = parsedData.filter(d => d.component === team);
        const total = teamData.length;

        const statuses = {};
        teamData.forEach(d => {
          if (!statuses[d.status]) statuses[d.status] = 0;
          statuses[d.status]++;
        });

        // Insert into the DOM
        const container = document.getElementById(team.replaceAll(" ", "_"));
        if (container) {
          const breakdown = document.createElement("div");
          breakdown.className = "status-breakdown";

          breakdown.innerHTML = `<h4>Story Ticket Status Breakdown (${total} total)</h4><ul>` +
            Object.entries(statuses).map(([status, count]) =>
              `<li><strong>${status}</strong>: ${count}</li>`).join("") +
            `</ul>`;
          container.appendChild(breakdown);
        }
      });
    });
});

