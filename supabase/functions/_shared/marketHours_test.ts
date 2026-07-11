import { assertEquals } from "https://deno.land/std@0.224.0/assert/mod.ts";
import { isVietnameseStockMarketOpen } from "./marketHours.ts";

Deno.test("Vietnam market sessions and weekend", () => {
  assertEquals(
    isVietnameseStockMarketOpen(new Date("2026-07-13T02:30:00Z")),
    true,
  );
  assertEquals(
    isVietnameseStockMarketOpen(new Date("2026-07-13T05:00:00Z")),
    false,
  );
  assertEquals(
    isVietnameseStockMarketOpen(new Date("2026-07-13T06:30:00Z")),
    true,
  );
  assertEquals(
    isVietnameseStockMarketOpen(new Date("2026-07-12T02:30:00Z")),
    false,
  );
});
