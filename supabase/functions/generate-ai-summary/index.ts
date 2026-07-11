import { getSupabaseAdmin } from "../_shared/supabaseAdminClient.ts";
const MODEL = Deno.env.get("ANTHROPIC_MODEL") ?? "claude-opus-4-8";
const forbidden = [
  /\bnên\s+(mua|bán|đầu tư)/iu,
  /\b(khuyến nghị|hãy mua|hãy bán|mã nên)/iu,
  /\b(you should|recommend buying|recommend selling)\b/iu,
];
export function removeInvestmentAdvice(text: string): string {
  return text.split(/(?<=[.!?。])\s+/u).filter((s) =>
    !forbidden.some((r) => r.test(s))
  ).join(" ").trim();
}
if (import.meta.main) {
  Deno.serve(async () => {
    try {
      const apiKey = Deno.env.get("ANTHROPIC_API_KEY");
      if (!apiKey) {
        return Response.json({ error: "ANTHROPIC_API_KEY is not configured" }, {
          status: 500,
        });
      }
      const supabaseAdmin = getSupabaseAdmin();
      const sinceSnapshots = new Date(Date.now() - 90 * 86400_000).toISOString()
          .slice(0, 10),
        sinceTransactions = new Date(Date.now() - 30 * 86400_000).toISOString();
      const [
        { data: snapshots, error: snapshotError },
        { data: transactions, error: transactionError },
      ] = await Promise.all([
        supabaseAdmin.from("valuation_snapshots").select(
          "date,total_assets,total_liabilities,net_worth,cash_value,stock_value,gold_value,savings_value,other_asset_value",
        ).gte("date", sinceSnapshots).order("date"),
        supabaseAdmin.from("asset_transactions").select(
          "type,date,amount,fee,tax",
        ).gte("date", sinceTransactions).order("date", { ascending: false })
          .limit(200),
      ]);
      if (snapshotError) throw snapshotError;
      if (transactionError) throw transactionError;
      if (!snapshots?.length) {
        return Response.json({ error: "Chưa có dữ liệu snapshot để tóm tắt" }, {
          status: 422,
        });
      }
      const prompt = `Dữ liệu tài chính cá nhân (VND):\nSnapshots: ${
        JSON.stringify(snapshots)
      }\nGiao dịch 30 ngày: ${
        JSON.stringify(transactions ?? [])
      }\nViết 2-4 câu tiếng Việt, nêu biến động tài sản ròng, nguyên nhân định lượng và cơ cấu nổi bật. Chỉ mô tả; không khuyên mua, bán, giữ, đầu tư hoặc dự đoán.`;
      const response = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: {
          "x-api-key": apiKey,
          "anthropic-version": "2023-06-01",
          "content-type": "application/json",
        },
        body: JSON.stringify({
          model: MODEL,
          max_tokens: 350,
          system:
            "Chỉ tóm tắt số liệu đã cho. Không đưa lời khuyên hoặc khuyến nghị đầu tư.",
          messages: [{ role: "user", content: prompt }],
        }),
      });
      if (!response.ok) {
        return Response.json(
          { error: `Anthropic returned ${response.status}` },
          { status: 502 },
        );
      }
      const body = await response.json(),
        raw = body?.content?.find((x: { type?: string }) => x.type === "text")
          ?.text;
      if (typeof raw !== "string") {
        return Response.json({ error: "Anthropic response has no text" }, {
          status: 502,
        });
      }
      const summary = removeInvestmentAdvice(raw);
      if (!summary) {
        return Response.json({ error: "Summary removed by safety filter" }, {
          status: 422,
        });
      }
      return Response.json({
        summary,
        generatedAt: new Date().toISOString(),
        model: MODEL,
      });
    } catch (error) {
      console.error("generate-ai-summary failed", error);
      const message = error instanceof Error
        ? error.message
        : typeof error === "string"
        ? error
        : (error as { message?: string })?.message ?? JSON.stringify(error);
      return Response.json({ error: message }, { status: 500 });
    }
  });
}
