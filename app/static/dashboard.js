const toggle = document.getElementById("themeToggle");
const body = document.body;
const themeKey = "tip-theme";

function applyTheme(theme) {
  if (theme === "light") {
    body.classList.remove("theme-dark");
    body.classList.add("theme-light");
    toggle.textContent = "Dark mode";
  } else {
    body.classList.remove("theme-light");
    body.classList.add("theme-dark");
    toggle.textContent = "Light mode";
  }
}

const savedTheme = localStorage.getItem(themeKey) || "dark";
applyTheme(savedTheme);

toggle.addEventListener("click", () => {
  const nextTheme = body.classList.contains("theme-light") ? "dark" : "light";
  localStorage.setItem(themeKey, nextTheme);
  applyTheme(nextTheme);
});

fetch("/api/analytics")
  .then((response) => response.json())
  .then((data) => {
    document.getElementById("metricTotal").textContent = data.total;
    document.getElementById("metricAverage").textContent = `${data.average_score}%`;
    document.getElementById("metricRecent").textContent = data.recent;
    document.getElementById("metricSources").textContent = data.sources.length;

    const logs = document.getElementById("scrapeLogs");
    logs.innerHTML = "";
    data.logs.forEach((log) => {
      const li = document.createElement("li");
      li.textContent = `${log.source}: ${log.status}`;
      logs.appendChild(li);
    });

    const sources = document.getElementById("sourceList");
    sources.innerHTML = "";
    data.sources.forEach((source) => {
      const li = document.createElement("li");
      li.textContent = `${source.source} (${source.count})`;
      sources.appendChild(li);
    });

    const ctx = document.getElementById("scoreChart");
    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: [">= 70%", "40-70%", "< 40%"],
        datasets: [
          {
            data: [
              data.score_buckets.high,
              data.score_buckets.mid,
              data.score_buckets.low,
            ],
            backgroundColor: ["#38bdf8", "#a5b4fc", "#f97316"],
          },
        ],
      },
      options: {
        plugins: { legend: { position: "bottom" } },
      },
    });
  })
  .catch(() => {
    console.warn("Analytics fetch failed");
  });
