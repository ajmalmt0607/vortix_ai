const BUSINESS_TZ = "Asia/Dubai";

export function formatMoney(value, { withCurrency = true } = {}) {
  const amount = Number(value ?? 0);
  const formatted = amount.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return withCurrency ? `AED ${formatted}` : formatted;
}

export function formatNumber(value) {
  return Number(value ?? 0).toLocaleString("en-US");
}

export function formatPercent(value) {
  if (value === null || value === undefined) return "—";
  const n = Number(value);
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(1)}%`;
}

export function formatDateTime(isoString) {
  if (!isoString) return "—";
  const date = new Date(isoString);
  return date.toLocaleString("en-GB", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
    timeZone: BUSINESS_TZ,
  });
}

export function formatDateShort(dateStr) {
  // dateStr is "YYYY-MM-DD" from the backend's sales_trend.
  const date = new Date(`${dateStr}T00:00:00`);
  return date.toLocaleDateString("en-GB", { day: "2-digit", month: "short" });
}
