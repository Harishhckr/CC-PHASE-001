const layoutStyles = {
  minHeight: "100vh",
  background: "#f2f5ff",
  color: "#0f172a",
  fontFamily:
    "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
};

const topBarStyles = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "28px 48px",
};

const pageStyles = {
  display: "grid",
  gridTemplateColumns: "minmax(260px, 320px) 1fr",
  gap: "32px",
  padding: "0 48px 48px",
};

const panelStyles = {
  background: "#ffffff",
  borderRadius: "24px",
  boxShadow: "0 20px 50px rgba(15, 23, 42, 0.08)",
  padding: "28px",
  display: "flex",
  flexDirection: "column",
  gap: "24px",
};

const badgeStyles = {
  display: "inline-flex",
  alignItems: "center",
  gap: "8px",
  padding: "6px 12px",
  borderRadius: "999px",
  background: "#eef2ff",
  fontSize: "12px",
  letterSpacing: "0.08em",
  textTransform: "uppercase",
  color: "#4338ca",
  fontWeight: 600,
};

const navButtonStyles = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  padding: "12px 14px",
  borderRadius: "14px",
  background: "#f1f5f9",
  border: "1px solid #e2e8f0",
  fontSize: "14px",
  fontWeight: 500,
};

const cardStyles = {
  background: "#ffffff",
  borderRadius: "18px",
  border: "1px solid #e2e8f0",
  padding: "20px",
  display: "flex",
  flexDirection: "column",
  gap: "16px",
};

const metricStyles = {
  display: "flex",
  flexDirection: "column",
  gap: "6px",
  padding: "16px",
  borderRadius: "16px",
  background: "#f8fafc",
  border: "1px solid #e2e8f0",
};

const listStyles = {
  display: "flex",
  flexDirection: "column",
  gap: "14px",
};

export const sampleInterface = () => `
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sample UI</title>
  </head>
  <body style="margin: 0;">
    <main style="${styleString(layoutStyles)}">
      <header style="${styleString(topBarStyles)}">
        <div>
          <div style="${styleString(badgeStyles)}">Studio Board</div>
          <h1 style="margin: 10px 0 0; font-size: 30px;">Lumina Campaign</h1>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
          <button
            style="padding: 10px 16px; border-radius: 999px; border: 1px solid #c7d2fe; background: #eef2ff; color: #4338ca; font-weight: 600; cursor: pointer;"
          >
            Export
          </button>
          <button
            style="padding: 10px 18px; border-radius: 999px; border: none; background: #4f46e5; color: #ffffff; font-weight: 600; cursor: pointer;"
          >
            New Brief
          </button>
        </div>
      </header>
      <section style="${styleString(pageStyles)}">
        <aside style="${styleString(panelStyles)}">
          <div>
            <h2 style="margin: 0; font-size: 20px;">Brand overview</h2>
            <p style="margin: 8px 0 0; color: #64748b; font-size: 14px;">
              Keep the launch aligned across every team touchpoint.
            </p>
          </div>
          <div style="display: flex; flex-direction: column; gap: 10px;">
            ${renderNavItem("Dashboard", "07")}
            ${renderNavItem("Assets", "32")}
            ${renderNavItem("Campaigns", "04")}
            ${renderNavItem("Approvals", "11")}
          </div>
          <div style="${styleString(cardStyles)}">
            <span style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em;">
              Next review
            </span>
            <strong style="font-size: 18px;">Thursday 2:30 PM</strong>
            <div style="display: flex; gap: 8px;">
              ${renderMiniTag("Design", "#c7d2fe", "#4338ca")}
              ${renderMiniTag("Media", "#bae6fd", "#0369a1")}
            </div>
          </div>
          <div>
            <div style="font-size: 12px; color: #64748b;">Last synced</div>
            <div style="font-weight: 600;">12 minutes ago</div>
          </div>
        </aside>
        <div style="display: flex; flex-direction: column; gap: 20px;">
          <section style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px;">
            ${renderMetric("Engagement", "82%", "+9% vs last week")}
            ${renderMetric("Spend", "$48.2k", "On track")}
            ${renderMetric("Deliverables", "14", "3 pending")}
          </section>
          <section style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px;">
            <article style="${styleString(panelStyles)}">
              <header style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; font-size: 18px;">Active sprints</h3>
                ${renderChip("Live", "#dcfce7", "#16a34a")}
              </header>
              <div style="${styleString(listStyles)}">
                ${renderSprint("Social rollout", "Assets delivery", "Due in 2 days")}
                ${renderSprint("OOH refresh", "Concept review", "Due tomorrow")}
                ${renderSprint("Email nurture", "Copy polish", "Due Friday")}
              </div>
            </article>
            <article style="${styleString(panelStyles)}">
              <h3 style="margin: 0; font-size: 18px;">Team status</h3>
              <div style="display: flex; flex-direction: column; gap: 16px;">
                ${renderPulse("Creative", "4 online", "#4f46e5")}
                ${renderPulse("Strategy", "2 online", "#f97316")}
                ${renderPulse("Production", "5 online", "#0ea5e9")}
              </div>
              <div style="${styleString(cardStyles)}">
                <span style="font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em;">
                  Hours logged
                </span>
                <strong style="font-size: 22px;">128 hrs</strong>
                <div style="font-size: 12px; color: #22c55e;">+14% this week</div>
              </div>
            </article>
          </section>
        </div>
      </section>
    </main>
  </body>
</html>
`;

const renderNavItem = (label, count) =>
  `<div style="${styleString(navButtonStyles)}"><span>${label}</span><span style="font-weight: 600;">${count}</span></div>`;

const renderChip = (label, background, color) =>
  `<span style="display: inline-flex; align-items: center; padding: 6px 12px; border-radius: 999px; background: ${background}; color: ${color}; font-size: 12px; font-weight: 600;">${label}</span>`;

const renderStat = (label, value, trend) =>
  `<div style="${styleString(metricStyles)}"><span style="font-size: 12px; color: #64748b;">${label}</span><strong style="font-size: 22px;">${value}</strong><span style="font-size: 12px; color: #10b981;">${trend}</span></div>`;

const renderTimelineItem = (title, date, status) =>
  `<div style="display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; border-radius: 14px; background: #f8fafc; border: 1px solid #e2e8f0;">
    <div>
      <div style="font-weight: 600;">${title}</div>
      <div style="font-size: 12px; color: #64748b;">${date}</div>
    </div>
    <span style="font-size: 12px; font-weight: 600; color: #0f172a;">${status}</span>
  </div>`;

const renderPulse = (label, meta, color) =>
  `<div style="display: flex; align-items: center; justify-content: space-between;">
    <div>
      <div style="font-weight: 600;">${label}</div>
      <div style="font-size: 12px; color: #64748b;">${meta}</div>
    </div>
    <div style="width: 36px; height: 36px; border-radius: 12px; background: ${color}; opacity: 0.18;"></div>
  </div>`;

const renderMetric = (label, value, meta) =>
  `<div style="${styleString(metricStyles)}"><span style="font-size: 12px; color: #64748b;">${label}</span><strong style="font-size: 22px;">${value}</strong><span style="font-size: 12px; color: #64748b;">${meta}</span></div>`;

const renderSprint = (title, phase, due) =>
  `<div style="display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; border-radius: 16px; background: #f8fafc; border: 1px solid #e2e8f0;">
    <div>
      <div style="font-weight: 600;">${title}</div>
      <div style="font-size: 12px; color: #64748b;">${phase}</div>
    </div>
    <span style="font-size: 12px; font-weight: 600; color: #4f46e5;">${due}</span>
  </div>`;

const renderMiniTag = (label, background, color) =>
  `<span style="display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 999px; background: ${background}; color: ${color}; font-size: 11px; font-weight: 600;">${label}</span>`;

const styleString = (styles) =>
  Object.entries(styles)
    .map(([key, value]) => `${toKebabCase(key)}: ${value}`)
    .join("; ");

const toKebabCase = (value) =>
  value.replace(/[A-Z]/g, (match) => `-${match.toLowerCase()}`);
