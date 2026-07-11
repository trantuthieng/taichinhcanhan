import { getSupabaseAdmin } from "../_shared/supabaseAdminClient.ts";
import { filterChangedSnapshots } from "../_shared/dedupe.ts";

// Nguồn giá vàng: vang.today (HTTPS, miễn phí, không cần key, sau Cloudflare nên
// gọi được từ Supabase Edge — khác api.btmc.vn chặn IP nước ngoài).
const VANG_TODAY_URL = "https://www.vang.today/api/prices";

// type_code của vang.today -> asset_key của app. Giữ đúng các nhóm mà app dùng.
const CODE_TO_ASSET_KEY: Record<string, string> = {
  SJL1L10: "gold_bar_sjc", // SJC 9999 (vàng miếng SJC)
  SJ9999: "gold_ring_9999", // nhẫn tròn 9999
  DOHCML: "gold_bar_other_brand", // DOJI HCM (vàng thương hiệu khác)
  DOJINHTV: "gold_jewelry", // trang sức DOJI
  PQHN24NTT: "gold_24k", // PNJ 24K
};

// vang.today báo giá VND/lượng; app (và bản BTMC trước đây) dùng VND/chỉ.
const LUONG_TO_CHI = 10;

export interface VangTodayPrice {
  name?: string;
  buy?: number;
  sell?: number;
  currency?: string;
}

export function parseVangTodayPrices(
  prices: Record<string, VangTodayPrice>,
  fetchedAt = new Date().toISOString(),
) {
  return Object.entries(prices ?? {}).flatMap(([code, value]) => {
    const assetKey = CODE_TO_ASSET_KEY[code];
    if (!assetKey || value?.currency !== "VND") return [];
    const buyPrice = Number(value.buy) / LUONG_TO_CHI;
    const sellPrice = Number(value.sell) / LUONG_TO_CHI;
    if (!Number.isFinite(buyPrice) || buyPrice <= 0) return [];
    return [{
      asset_key: assetKey,
      asset_type: "gold",
      buy_price: buyPrice,
      sell_price: Number.isFinite(sellPrice) && sellPrice > 0 ? sellPrice : null,
      source: "vang.today",
      fetched_at: fetchedAt,
    }];
  });
}

if (import.meta.main) {
  Deno.serve(async () => {
    try {
      const response = await fetch(VANG_TODAY_URL, {
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        return Response.json(
          { error: `vang.today returned ${response.status}` },
          { status: 502 },
        );
      }
      const json = await response.json();
      const prices: Record<string, VangTodayPrice> = json?.prices ?? {};
      const snapshots = parseVangTodayPrices(prices);
      if (snapshots.length === 0) {
        return Response.json({
          inserted: 0,
          warning: "No mapped gold products",
        });
      }
      const admin = getSupabaseAdmin();
      const changed = await filterChangedSnapshots(admin, "gold", snapshots);
      if (changed.length) {
        const { error } = await admin.from("price_snapshots").insert(changed);
        if (error) throw error;
      }
      return Response.json({
        inserted: changed.length,
        skipped: snapshots.length - changed.length,
      });
    } catch (error) {
      console.error("fetch-gold-price failed", error);
      return Response.json({
        error: error instanceof Error ? error.message : "Unknown error",
      }, { status: 500 });
    }
  });
}
