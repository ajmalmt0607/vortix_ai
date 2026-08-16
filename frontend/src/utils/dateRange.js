const BUSINESS_TZ = "Asia/Dubai";

function getBusinessToday() {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: BUSINESS_TZ,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(new Date());
  const map = Object.fromEntries(parts.map((p) => [p.type, p.value]));
  return `${map.year}-${map.month}-${map.day}`;
}

function addDays(dateStr, days) {
  const [y, m, d] = dateStr.split("-").map(Number);
  const date = new Date(Date.UTC(y, m - 1, d));
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

export function getPresetRange(preset) {
  const today = getBusinessToday();
  switch (preset) {
    case "today":
      return { start_date: today, end_date: today };
    case "yesterday": {
      const y = addDays(today, -1);
      return { start_date: y, end_date: y };
    }
    case "7d":
      return { start_date: addDays(today, -6), end_date: today };
    case "30d":
      return { start_date: addDays(today, -29), end_date: today };
    default:
      return { start_date: addDays(today, -29), end_date: today };
  }
}
