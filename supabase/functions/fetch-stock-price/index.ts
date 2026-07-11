/**
 * Verified against DNSE OpenAPI on 2026-07-11.
 * GET https://openapi.dnse.com.vn/price/GAS/trades/latest?boardId=G1 returned:
 * { "trades": [{ "symbol":"GAS", "boardId":"G1", "matchPrice":75.2,
 *   "time":"2026-07-10 14:45:03.269", ... }] }
 * DNSE equity prices are exchange quote values in thousands of VND, so 75.2 is
 * persisted as 75,200 VND to match AssetTracker's VND monetary representation.
 */
import { getSupabaseAdmin } from "../_shared/supabaseAdminClient.ts";
import { signDnseRequest } from "../_shared/dnseSignature.ts";
import { isVietnameseStockMarketOpen } from "../_shared/marketHours.ts";
import { filterChangedSnapshots } from "../_shared/dedupe.ts";

const DNSE_ORIGIN = "https://openapi.dnse.com.vn";
const VND_QUOTE_MULTIPLIER = 1000;

type DnseTrade = { symbol?: string; matchPrice?: number; time?: string };
export function parseLatestTrade(
  body: unknown,
  expectedSymbol: string,
  fetchedAt = new Date().toISOString(),
) {
  const trades = (body as { trades?: DnseTrade[] })?.trades;
  const trade = Array.isArray(trades) ? trades[0] : undefined;
  const price = Number(trade?.matchPrice);
  if (!trade || !Number.isFinite(price) || price <= 0) return null;
  return {
    asset_key: (trade.symbol || expectedSymbol).toUpperCase(),
    asset_type: "stock",
    buy_price: price * VND_QUOTE_MULTIPLIER,
    sell_price: null,
    source: "DNSE",
    fetched_at: fetchedAt,
  };
}

if (import.meta.main) {
  Deno.serve(async () => {
    // DNSE trả giá phiên khớp gần nhất bất kể giờ, nên vẫn lấy khi ngoài giờ
    // giao dịch (giá đóng cửa phiên trước) — chỉ dùng giờ để gắn nhãn marketOpen.
    const marketOpen = isVietnameseStockMarketOpen();
    try {
      const supabaseAdmin = getSupabaseAdmin();
      const { data: heldAssets, error: assetError } = await supabaseAdmin.from(
        "assets",
      )
        .select("symbol").eq("category", "stock").not("symbol", "is", null);
      if (assetError) {
        throw assetError;
      }
      const symbols = [
        ...new Set(
          (heldAssets ?? []).map((row) =>
            String(row.symbol).trim().toUpperCase()
          ).filter(Boolean),
        ),
      ];
      const snapshots = [];
      const failures: { symbol: string; status?: number; error: string }[] = [];
      for (const symbol of symbols) {
        const path = `/price/${encodeURIComponent(symbol)}/trades/latest`;
        try {
          const headers = await signDnseRequest("GET", path);
          const response = await fetch(`${DNSE_ORIGIN}${path}`, { headers });
          if (!response.ok) {
            failures.push({
              symbol,
              status: response.status,
              error: await response.text(),
            });
            continue;
          }
          const snapshot = parseLatestTrade(await response.json(), symbol);
          if (snapshot) snapshots.push(snapshot);
          else failures.push({ symbol, error: "No valid latest trade" });
        } catch (error) {
          failures.push({
            symbol,
            error: error instanceof Error ? error.message : "Unknown error",
          });
        }
      }
      const changed = await filterChangedSnapshots(
        supabaseAdmin,
        "stock",
        snapshots,
      );
      if (changed.length) {
        const { error } = await supabaseAdmin.from("price_snapshots").insert(
          changed,
        );
        if (error) throw error;
      }
      return Response.json({
        inserted: changed.length,
        skipped: snapshots.length - changed.length,
        marketOpen,
        failures: failures.map(({ symbol, status, error }) => ({
          symbol,
          status,
          error: error.slice(0, 160),
        })),
      });
    } catch (error) {
      console.error("fetch-stock-price failed", error);
      return Response.json({
        error: error instanceof Error ? error.message : "Unknown error",
      }, { status: 500 });
    }
  });
}
