export function isVietnameseStockMarketOpen(date = new Date()): boolean {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Ho_Chi_Minh",
    weekday: "short",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(date);
  const value = Object.fromEntries(
    parts.map((part) => [part.type, part.value]),
  );
  if (value.weekday === "Sat" || value.weekday === "Sun") return false;
  const minutes = Number(value.hour) * 60 + Number(value.minute);
  return (minutes >= 9 * 60 && minutes <= 11 * 60 + 30) ||
    (minutes >= 13 * 60 && minutes <= 15 * 60);
}
