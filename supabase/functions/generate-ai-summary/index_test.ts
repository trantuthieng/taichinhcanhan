import { assertEquals } from "https://deno.land/std@0.224.0/assert/mod.ts";
import { removeInvestmentAdvice } from "./index.ts";
Deno.test("removes advice", () =>
  assertEquals(
    removeInvestmentAdvice(
      "Tài sản ròng tăng 5%. Bạn nên mua HPG. Tiền mặt chiếm 30%.",
    ),
    "Tài sản ròng tăng 5%. Tiền mặt chiếm 30%.",
  ));
