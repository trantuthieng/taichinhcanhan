import { assertEquals } from "https://deno.land/std@0.224.0/assert/mod.ts";
import { latestTradePath, parseLatestTrade } from "./index.ts";

Deno.test("builds the verified DNSE latest-trade path with board id", () => {
  assertEquals(
    latestTradePath("MBB"),
    "/price/MBB/trades/latest?boardId=G1",
  );
});

Deno.test("parses verified DNSE latest trade response into VND", () => {
  assertEquals(
    parseLatestTrade(
      {
        trades: [{
          symbol: "GAS",
          matchPrice: 75.2,
          time: "2026-07-10 14:45:03.269",
        }],
      },
      "GAS",
      "2026-07-11T00:00:00.000Z",
    ),
    {
      asset_key: "GAS",
      asset_type: "stock",
      buy_price: 75200,
      sell_price: null,
      source: "DNSE",
      fetched_at: "2026-07-11T00:00:00.000Z",
    },
  );
});

Deno.test("rejects missing or zero trade price", () => {
  assertEquals(parseLatestTrade({ trades: [] }, "GAS"), null);
  assertEquals(parseLatestTrade({ trades: [{ matchPrice: 0 }] }, "GAS"), null);
});
