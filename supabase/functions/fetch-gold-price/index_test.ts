import { assertEquals } from "https://deno.land/std@0.224.0/assert/mod.ts";
import { parseVangTodayPrices } from "./index.ts";

Deno.test("maps vang.today codes to asset keys and converts luong -> chi", () => {
  const result = parseVangTodayPrices({
    SJL1L10: { name: "SJC 9999", buy: 146900000, sell: 149900000, currency: "VND" },
    SJ9999: { name: "SJC Ring", buy: 146400000, sell: 149400000, currency: "VND" },
    XAUUSD: { name: "World Gold", buy: 4121.4, sell: 0, currency: "USD" }, // bỏ: không phải VND
    UNKNOWN: { name: "??", buy: 1000000, sell: 2000000, currency: "VND" }, // bỏ: chưa map
  }, "2026-07-11T00:00:00.000Z");
  assertEquals(result, [
    {
      asset_key: "gold_bar_sjc",
      asset_type: "gold",
      buy_price: 14690000,
      sell_price: 14990000,
      source: "vang.today",
      fetched_at: "2026-07-11T00:00:00.000Z",
    },
    {
      asset_key: "gold_ring_9999",
      asset_type: "gold",
      buy_price: 14640000,
      sell_price: 14940000,
      source: "vang.today",
      fetched_at: "2026-07-11T00:00:00.000Z",
    },
  ]);
});

Deno.test("drops rows with missing or zero buy price", () => {
  const result = parseVangTodayPrices({
    SJL1L10: { name: "SJC 9999", buy: 0, sell: 149900000, currency: "VND" },
    SJ9999: { name: "SJC Ring", sell: 149400000, currency: "VND" },
  }, "2026-07-11T00:00:00.000Z");
  assertEquals(result, []);
});
