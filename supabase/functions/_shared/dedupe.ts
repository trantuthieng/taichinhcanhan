// Chỉ giữ lại các snapshot có buy_price khác dòng mới nhất cùng asset_key,
// để không ghi trùng khi hàm được gọi nhiều lần (app mở lại, cron...).
type Snapshot = { asset_key: string; buy_price: number };

export async function filterChangedSnapshots<T extends Snapshot>(
  admin: { from: (table: string) => { select: (cols: string) => any } },
  assetType: string,
  snapshots: T[],
): Promise<T[]> {
  if (snapshots.length === 0) return [];
  const keys = [...new Set(snapshots.map((s) => s.asset_key))];
  const { data } = await admin
    .from("price_snapshots")
    .select("asset_key, buy_price, fetched_at")
    .eq("asset_type", assetType)
    .in("asset_key", keys)
    .order("fetched_at", { ascending: false });

  const latest = new Map<string, number>();
  for (const row of (data ?? []) as { asset_key: string; buy_price: number }[]) {
    if (!latest.has(row.asset_key)) latest.set(row.asset_key, Number(row.buy_price));
  }
  return snapshots.filter((s) => latest.get(s.asset_key) !== Number(s.buy_price));
}
