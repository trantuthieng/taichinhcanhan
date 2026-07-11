import { assertEquals } from "https://deno.land/std@0.224.0/assert/mod.ts";
import { parseBtmcRows } from "./index.ts";

Deno.test("parses dynamic BTMC row suffix and ignores unknown products", () => {
  const result = parseBtmcRows([
    {
      "@row": "9",
      "@n_9": "VÀNG MIẾNG SJC (Vàng SJC)",
      "@pb_9": "14500000",
      "@ps_9": "14990000",
    },
    { "@row": "2", "@n_2": "BẠC", "@pb_2": "100", "@ps_2": "200" },
  ], "2026-07-11T00:00:00.000Z");
  assertEquals(result, [{
    asset_key: "gold_bar_sjc",
    asset_type: "gold",
    buy_price: 14500000,
    sell_price: 14990000,
    source: "BTMC",
    fetched_at: "2026-07-11T00:00:00.000Z",
  }]);
});
