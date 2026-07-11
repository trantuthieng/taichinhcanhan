import { getSupabaseAdmin } from "../_shared/supabaseAdminClient.ts";

const NAME_TO_ASSET_KEY: Record<string, string> = {
  "VÀNG MIẾNG SJC (Vàng SJC)": "gold_bar_sjc",
  "NHẪN TRÒN TRƠN (Vàng Rồng Thăng Long)": "gold_ring_9999",
  "VÀNG THƯƠNG HIỆU DOJI, PNJ, PHÚ QUÝ... (Vàng Đối Tác)":
    "gold_bar_other_brand",
  "TRANG SỨC VÀNG RỒNG THĂNG LONG 999.9 (Vàng BTMC)": "gold_jewelry",
  "TRANG SỨC VÀNG RỒNG THĂNG LONG 99.9 (Vàng BTMC)": "gold_jewelry",
};

export function parseBtmcRows(
  rows: Record<string, string>[],
  fetchedAt = new Date().toISOString(),
) {
  return rows.flatMap((row) => {
    const idx = row["@row"];
    if (!idx) return [];
    const assetKey = NAME_TO_ASSET_KEY[row[`@n_${idx}`]];
    const buyPrice = Number(row[`@pb_${idx}`]);
    const sellPrice = Number(row[`@ps_${idx}`]);
    if (!assetKey || !Number.isFinite(buyPrice) || buyPrice <= 0) return [];
    return [{
      asset_key: assetKey,
      asset_type: "gold",
      buy_price: buyPrice,
      sell_price: Number.isFinite(sellPrice) ? sellPrice : null,
      source: "BTMC",
      fetched_at: fetchedAt,
    }];
  });
}

if (import.meta.main) {
  Deno.serve(async () => {
    try {
      const key = Deno.env.get("BTMC_API_KEY");
      if (!key) {
        return Response.json({ error: "BTMC_API_KEY is not configured" }, {
          status: 500,
        });
      }
      const response = await fetch(
        `http://api.btmc.vn/api/BTMCAPI/getpricebtmc?key=${
          encodeURIComponent(key)
        }`,
      );
      if (!response.ok) {
        return Response.json({ error: `BTMC returned ${response.status}` }, {
          status: 502,
        });
      }
      const json = await response.json();
      const rows: Record<string, string>[] = json?.DataList?.Data ?? [];
      const snapshots = parseBtmcRows(rows);
      if (snapshots.length === 0) {
        return Response.json({
          inserted: 0,
          warning: "No mapped gold products",
        });
      }
      const { error } = await getSupabaseAdmin().from("price_snapshots").insert(
        snapshots,
      );
      if (error) throw error;
      return Response.json({ inserted: snapshots.length });
    } catch (error) {
      console.error("fetch-gold-price failed", error);
      return Response.json({
        error: error instanceof Error ? error.message : "Unknown error",
      }, { status: 500 });
    }
  });
}
