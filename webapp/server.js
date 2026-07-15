const crypto = require("node:crypto");
const path = require("node:path");
const express = require("express");

const app = express();
const PORT = Number(process.env.PORT || 3000);
const ADMIN_USERNAME = process.env.ADMIN_USERNAME || "admin";
const DEFAULT_PASSWORD_HASH = "scrypt:4a16ab466659b13653606ffe7df7c473:3204421c000fdf52f43878be5d535d5f4835dfe5d67a24afb113dca49da5448e15d56af1c41de2cacbcb276fa87af2fe4bd4cc5265dd582a3e1a4e3a8401356e";
const ADMIN_PASSWORD_HASH = process.env.ADMIN_PASSWORD_HASH || DEFAULT_PASSWORD_HASH;
const SESSION_SECRET = process.env.SESSION_SECRET || crypto.randomBytes(32).toString("hex");
const SESSION_TTL_SECONDS = 60 * 60 * 12;

const TABLES = new Set([
  "asset_accounts",
  "assets",
  "asset_transactions",
  "savings_deposits",
  "liabilities",
  "recurring_incomes",
  "monthly_payables",
  "valuation_snapshots",
]);
const READ_ONLY_TABLES = new Set(["valuation_snapshots"]);
const loginAttempts = new Map();

app.disable("x-powered-by");
app.set("trust proxy", 1);
app.use(express.json({ limit: "256kb" }));
app.use(express.static(path.join(__dirname, "public"), { extensions: ["html"] }));

function base64url(value) {
  return Buffer.from(value).toString("base64url");
}

function sign(value) {
  return crypto.createHmac("sha256", SESSION_SECRET).update(value).digest("base64url");
}

function createSession(username) {
  const payload = base64url(JSON.stringify({ username, exp: Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS }));
  return `${payload}.${sign(payload)}`;
}

function parseCookies(header = "") {
  return Object.fromEntries(
    header.split(";").map((part) => part.trim()).filter(Boolean).map((part) => {
      const index = part.indexOf("=");
      return [decodeURIComponent(part.slice(0, index)), decodeURIComponent(part.slice(index + 1))];
    }),
  );
}

function getSession(req) {
  const token = parseCookies(req.headers.cookie).asset_session;
  if (!token) return null;
  const [payload, signature] = token.split(".");
  if (!payload || !signature) return null;
  const expected = sign(payload);
  const a = Buffer.from(signature);
  const b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  try {
    const session = JSON.parse(Buffer.from(payload, "base64url").toString("utf8"));
    return session.exp > Date.now() / 1000 ? session : null;
  } catch {
    return null;
  }
}

function requireAuth(req, res, next) {
  const session = getSession(req);
  if (!session) return res.status(401).json({ error: "Phiên đăng nhập đã hết hạn." });
  req.session = session;
  next();
}

function verifyPassword(password) {
  const [algorithm, salt, expectedHex] = ADMIN_PASSWORD_HASH.split(":");
  if (algorithm !== "scrypt" || !salt || !expectedHex) return Promise.resolve(false);
  return new Promise((resolve) => {
    crypto.scrypt(password, salt, expectedHex.length / 2, (error, key) => {
      if (error) return resolve(false);
      const expected = Buffer.from(expectedHex, "hex");
      resolve(key.length === expected.length && crypto.timingSafeEqual(key, expected));
    });
  });
}

function checkLoginRate(ip) {
  const now = Date.now();
  const current = loginAttempts.get(ip) || { count: 0, resetAt: now + 15 * 60_000 };
  if (now > current.resetAt) {
    loginAttempts.set(ip, { count: 0, resetAt: now + 15 * 60_000 });
    return true;
  }
  return current.count < 8;
}

function recordFailedLogin(ip) {
  const current = loginAttempts.get(ip) || { count: 0, resetAt: Date.now() + 15 * 60_000 };
  current.count += 1;
  loginAttempts.set(ip, current);
}

function sameOrigin(req) {
  const origin = req.get("origin");
  if (!origin) return true;
  const forwardedHost = req.get("x-forwarded-host") || req.get("host");
  return origin === `${req.protocol}://${forwardedHost}`;
}

app.get("/api/health", (_req, res) => res.json({ ok: true }));

app.get("/api/session", (req, res) => {
  const session = getSession(req);
  if (!session) return res.status(401).json({ authenticated: false });
  res.json({ authenticated: true, username: session.username });
});

app.post("/api/login", async (req, res) => {
  if (!sameOrigin(req)) return res.status(403).json({ error: "Yêu cầu không hợp lệ." });
  if (!checkLoginRate(req.ip)) return res.status(429).json({ error: "Đăng nhập sai quá nhiều lần. Vui lòng thử lại sau." });
  const username = String(req.body?.username || "");
  const password = String(req.body?.password || "");
  const usernameBuffer = Buffer.from(username);
  const expectedUsernameBuffer = Buffer.from(ADMIN_USERNAME);
  const usernameMatches = usernameBuffer.length === expectedUsernameBuffer.length && crypto.timingSafeEqual(usernameBuffer, expectedUsernameBuffer);
  const passwordMatches = await verifyPassword(password);
  if (!usernameMatches || !passwordMatches) {
    recordFailedLogin(req.ip);
    return res.status(401).json({ error: "Tên đăng nhập hoặc mật khẩu không đúng." });
  }
  loginAttempts.delete(req.ip);
  const secure = process.env.NODE_ENV === "production" ? "; Secure" : "";
  res.setHeader("Set-Cookie", `asset_session=${createSession(username)}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${SESSION_TTL_SECONDS}${secure}`);
  res.json({ authenticated: true, username });
});

app.post("/api/logout", requireAuth, (req, res) => {
  if (!sameOrigin(req)) return res.status(403).json({ error: "Yêu cầu không hợp lệ." });
  const secure = process.env.NODE_ENV === "production" ? "; Secure" : "";
  res.setHeader("Set-Cookie", `asset_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0${secure}`);
  res.json({ ok: true });
});

function supabaseConfig() {
  const url = String(process.env.SUPABASE_URL || "").replace(/\/$/, "");
  const key = process.env.SUPABASE_ANON_KEY || "";
  if (!url || !key) throw new Error("Chưa cấu hình SUPABASE_URL và SUPABASE_ANON_KEY trên Render.");
  return { url, key };
}

async function supabaseRequest(table, { method = "GET", query = "", body, prefer = "return=representation" } = {}) {
  const { url, key } = supabaseConfig();
  const response = await fetch(`${url}/rest/v1/${table}${query}`, {
    method,
    headers: {
      apikey: key,
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/json",
      Prefer: prefer,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const text = await response.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!response.ok) {
    const missingMonthlyPayables = table === "monthly_payables" && response.status === 404;
    const error = new Error(missingMonthlyPayables
      ? "Chưa có bảng khoản phải trả. Hãy chạy migration 0011_monthly_payables.sql trên Supabase."
      : data?.message || `Supabase trả về lỗi ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return data;
}

function estimatedMonthlyDebtPayment(liability, priorRepayments = 0) {
  const balance = Number(liability.current_balance || 0);
  if (balance <= 0) return 0;
  const savedPayment = Number(liability.monthly_payment || 0);
  if (savedPayment > 0) return savedPayment;

  if (liability.liability_type === "credit_card") {
    return Math.min(balance, Math.max(
      balance * Number(liability.min_payment_rate || 0) / 100,
      Number(liability.min_payment_fixed_amount || 0),
    ));
  }

  const months = Number(liability.term_in_months || 0);
  if (months <= 0 || priorRepayments >= months) return 0;
  const originalPrincipal = Number(liability.original_principal || balance);
  const monthlyRate = Number(liability.annual_interest_rate || 0) / 100 / 12;
  if (liability.repayment_method === "equal_principal") {
    const principalPerPeriod = originalPrincipal / months;
    const remainingBeforePayment = Math.max(0, originalPrincipal - principalPerPeriod * priorRepayments);
    const principalDue = priorRepayments === months - 1 ? remainingBeforePayment : principalPerPeriod;
    return principalDue + remainingBeforePayment * monthlyRate;
  }
  if (monthlyRate === 0) return originalPrincipal / months;
  const growth = Math.pow(1 + monthlyRate, months);
  return originalPrincipal * monthlyRate * growth / (growth - 1);
}

app.use("/api/data", requireAuth, (req, res, next) => {
  if (!sameOrigin(req)) return res.status(403).json({ error: "Yêu cầu không hợp lệ." });
  next();
});

app.get("/api/data/summary", async (_req, res, next) => {
  try {
    const optionalTable = async (table, request) => {
      try { return await supabaseRequest(table, request); }
      catch (error) {
        if (error.status === 404) return [];
        throw error;
      }
    };
    const [accounts, assets, savings, liabilities, incomes, payables, repayments] = await Promise.all([
      supabaseRequest("asset_accounts", { query: "?select=id,balance,currency,current_exchange_rate,is_included_in_net_worth" }),
      supabaseRequest("assets", { query: "?select=id,category,quantity,current_price,currency" }),
      supabaseRequest("savings_deposits", { query: "?select=id,principal,currency,status" }),
      supabaseRequest("liabilities", { query: "?select=id,name,liability_type,original_principal,current_balance,currency,annual_interest_rate,start_date,next_payment_date,monthly_payment,repayment_method,term_in_months,min_payment_rate,min_payment_fixed_amount" }),
      supabaseRequest("recurring_incomes", { query: "?select=id,monthly_amount,is_active" }),
      optionalTable("monthly_payables", { query: "?select=id,name,category,monthly_amount,currency,due_day,is_active,is_auto_pay,liability_id&order=due_day.asc" }),
      supabaseRequest("asset_transactions", { query: "?select=liability_id&type=eq.repayment" }),
    ]);
    const inVnd = (amount, currency, rate) => Number(amount || 0) * (currency === "VND" ? 1 : Number(rate || 1));
    const accountValue = accounts.filter((x) => x.is_included_in_net_worth).reduce((sum, x) => sum + inVnd(x.balance, x.currency, x.current_exchange_rate), 0);
    const assetValue = assets.reduce((sum, x) => sum + inVnd(Number(x.quantity) * Number(x.current_price), x.currency), 0);
    const savingsValue = savings.filter((x) => x.status === "active").reduce((sum, x) => sum + inVnd(x.principal, x.currency), 0);
    const debt = liabilities.reduce((sum, x) => sum + inVnd(x.current_balance, x.currency), 0);
    const monthlyIncome = incomes.filter((x) => x.is_active).reduce((sum, x) => sum + Number(x.monthly_amount || 0), 0);
    const activePayables = payables.filter((x) => x.is_active);
    const linkedLiabilityIDs = new Set(activePayables.map((x) => x.liability_id).filter(Boolean));
    const repaymentCounts = repayments.reduce((counts, item) => {
      if (item.liability_id) counts.set(item.liability_id, (counts.get(item.liability_id) || 0) + 1);
      return counts;
    }, new Map());
    const automaticDebtPayables = liabilities
      .filter((x) => !linkedLiabilityIDs.has(x.id))
      .map((x) => ({ ...x, estimated_payment: estimatedMonthlyDebtPayment(x, repaymentCounts.get(x.id) || 0) }))
      .filter((x) => x.estimated_payment > 0);
    const monthlyRecurringPayables = activePayables.reduce((sum, x) => sum + inVnd(x.monthly_amount, x.currency), 0);
    const monthlyDebtPayments = automaticDebtPayables.reduce((sum, x) => sum + inVnd(x.estimated_payment, x.currency), 0);
    const monthlyPayables = monthlyRecurringPayables + monthlyDebtPayments;
    const totalAssets = accountValue + assetValue + savingsValue;
    const monthlyCashFlow = monthlyIncome - monthlyPayables;
    res.json({
      totalAssets,
      debt,
      netWorth: totalAssets - debt,
      monthlyIncome,
      monthlyPayables,
      monthlyRecurringPayables,
      monthlyDebtPayments,
      monthlyCashFlow,
      savingsRate: monthlyIncome > 0 ? monthlyCashFlow / monthlyIncome * 100 : 0,
      debtToAssets: totalAssets > 0 ? debt / totalAssets * 100 : 0,
      allocation: { accounts: accountValue, investments: assetValue, savings: savingsValue },
      upcomingPayables: activePayables.concat(automaticDebtPayables.map((x) => ({
        id: `debt-${x.id}`,
        name: x.name,
        category: x.liability_type === "credit_card" ? "credit_card" : "loan_payment",
        monthly_amount: x.estimated_payment,
        currency: x.currency,
        due_day: x.next_payment_date ? new Date(`${x.next_payment_date}T00:00:00Z`).getUTCDate() : 1,
        is_auto_pay: true,
        source: "liability",
      }))).sort((a, b) => {
        const today = new Date().getDate();
        return ((a.due_day - today + 31) % 31) - ((b.due_day - today + 31) % 31);
      }).slice(0, 6),
      counts: { accounts: accounts.length, assets: assets.length, savings: savings.length, liabilities: liabilities.length, payables: payables.length },
    });
  } catch (error) { next(error); }
});

app.get("/api/data/:table", async (req, res, next) => {
  try {
    if (!TABLES.has(req.params.table)) return res.status(404).json({ error: "Loại dữ liệu không tồn tại." });
    const limit = Math.min(Math.max(Number(req.query.limit) || 200, 1), 500);
    const order = req.params.table === "valuation_snapshots" ? "date.desc" : req.params.table === "asset_transactions" ? "date.desc" : "created_at.desc";
    res.json(await supabaseRequest(req.params.table, { query: `?select=*&order=${order}&limit=${limit}` }));
  } catch (error) { next(error); }
});

app.post("/api/data/:table", async (req, res, next) => {
  try {
    const table = req.params.table;
    if (!TABLES.has(table) || READ_ONLY_TABLES.has(table)) return res.status(405).json({ error: "Không thể thêm loại dữ liệu này." });
    const body = { ...req.body };
    delete body.id; delete body.created_at; delete body.updated_at;
    if ("edited_by" in body || ["asset_accounts", "asset_transactions", "savings_deposits", "liabilities", "recurring_incomes", "monthly_payables"].includes(table)) body.edited_by = req.session.username;
    res.status(201).json(await supabaseRequest(table, { method: "POST", body }));
  } catch (error) { next(error); }
});

app.patch("/api/data/:table/:id", async (req, res, next) => {
  try {
    const table = req.params.table;
    if (!TABLES.has(table) || READ_ONLY_TABLES.has(table)) return res.status(405).json({ error: "Không thể sửa loại dữ liệu này." });
    if (!/^[0-9a-f-]{36}$/i.test(req.params.id)) return res.status(400).json({ error: "ID không hợp lệ." });
    const body = { ...req.body };
    delete body.id; delete body.created_at;
    if (table !== "asset_transactions") body.updated_at = new Date().toISOString();
    if (["asset_accounts", "asset_transactions", "savings_deposits", "liabilities", "recurring_incomes", "monthly_payables"].includes(table)) body.edited_by = req.session.username;
    res.json(await supabaseRequest(table, { method: "PATCH", query: `?id=eq.${req.params.id}`, body }));
  } catch (error) { next(error); }
});

app.delete("/api/data/:table/:id", async (req, res, next) => {
  try {
    const table = req.params.table;
    if (!TABLES.has(table) || READ_ONLY_TABLES.has(table)) return res.status(405).json({ error: "Không thể xóa loại dữ liệu này." });
    if (!/^[0-9a-f-]{36}$/i.test(req.params.id)) return res.status(400).json({ error: "ID không hợp lệ." });
    await supabaseRequest(table, { method: "DELETE", query: `?id=eq.${req.params.id}`, prefer: "return=minimal" });
    res.status(204).end();
  } catch (error) { next(error); }
});

app.use((error, _req, res, _next) => {
  console.error(error);
  const status = error.status && error.status >= 400 && error.status < 600 ? error.status : 500;
  res.status(status).json({ error: error.message || "Có lỗi xảy ra." });
});

app.listen(PORT, "0.0.0.0", () => console.log(`AssetTracker web đang chạy tại cổng ${PORT}`));
