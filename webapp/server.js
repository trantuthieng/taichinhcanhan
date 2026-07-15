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

const GOLD_CATEGORIES = new Set(["gold_bar_sjc", "gold_ring_9999", "gold_bar_other_brand", "gold_jewelry", "gold_24k", "gold_18k", "gold_14k", "gold_international", "other_gold"]);
const FUND_CATEGORIES = new Set(["fund_certificate", "open_end_fund"]);

function goldPricePerUnit(pricePerChi, unit) {
  if (["luong", "cay"].includes(unit)) return pricePerChi * 10;
  if (unit === "phan") return pricePerChi / 10;
  if (unit === "gram") return pricePerChi / 3.75;
  if (unit === "ounce") return pricePerChi * 8.2942608;
  return pricePerChi;
}

function marketKeyForAsset(asset) {
  if (GOLD_CATEGORIES.has(asset.category)) return `gold:${String(asset.category).toUpperCase()}`;
  if (!asset.symbol) return null;
  if (FUND_CATEGORIES.has(asset.category)) return `fund:${String(asset.symbol).trim().toUpperCase()}`;
  if (["stock", "etf", "listed_bond", "warrant"].includes(asset.category)) return `stock:${String(asset.symbol).trim().toUpperCase()}`;
  return null;
}

async function loadAssetsWithMarketPrices() {
  const [assets, snapshots] = await Promise.all([
    supabaseRequest("assets", { query: "?select=*&order=created_at.desc&limit=500" }),
    supabaseRequest("price_snapshots", { query: "?select=asset_key,asset_type,buy_price,sell_price,source,fetched_at&order=fetched_at.desc&limit=1000" }),
  ]);
  const latest = new Map();
  for (const snapshot of snapshots) {
    const key = `${snapshot.asset_type}:${String(snapshot.asset_key).trim().toUpperCase()}`;
    if (!latest.has(key)) latest.set(key, snapshot);
  }
  const today = new Date().toISOString().slice(0, 10);
  return assets.map((asset) => {
    const key = marketKeyForAsset(asset);
    const snapshot = key ? latest.get(key) : null;
    if (!snapshot || Number(snapshot.buy_price || 0) <= 0) {
      const valuationDate = String(asset.valuation_date || "").slice(0, 10);
      return { ...asset, stored_current_price: asset.current_price, stored_valuation_date: asset.valuation_date, price_source: asset.valuation_source || "Nhập tay", price_is_automatic: false, price_is_stale: valuationDate !== today };
    }
    const marketPrice = GOLD_CATEGORIES.has(asset.category)
      ? goldPricePerUnit(Number(snapshot.buy_price), asset.unit)
      : Number(snapshot.buy_price);
    return {
      ...asset,
      stored_current_price: asset.current_price,
      stored_valuation_date: asset.valuation_date,
      current_price: marketPrice,
      valuation_date: snapshot.fetched_at,
      price_source: snapshot.source,
      price_is_automatic: true,
      price_is_stale: String(snapshot.fetched_at).slice(0, 10) !== today,
    };
  });
}

async function syncMarketPricesToAssets() {
  const assets = await loadAssetsWithMarketPrices();
  const changed = assets.filter((asset) => asset.price_is_automatic && (
    Number(asset.stored_current_price || 0) !== Number(asset.current_price || 0)
    || String(asset.stored_valuation_date || "").slice(0, 19) !== String(asset.valuation_date || "").slice(0, 19)
    || asset.valuation_source !== asset.price_source
  ));
  const results = await Promise.allSettled(changed.map((asset) => supabaseRequest("assets", {
    method: "PATCH",
    query: `?id=eq.${asset.id}`,
    body: {
      current_price: asset.current_price,
      valuation_date: asset.valuation_date,
      valuation_source: asset.price_source,
      updated_at: new Date().toISOString(),
    },
  })));
  return {
    updated: results.filter((result) => result.status === "fulfilled").length,
    failed: results.filter((result) => result.status === "rejected").length,
    available: assets.filter((asset) => asset.price_is_automatic).length,
    fresh: assets.filter((asset) => asset.price_is_automatic && !asset.price_is_stale).length,
  };
}

async function optionalTable(table, request) {
  try { return await supabaseRequest(table, request); }
  catch (error) {
    if (error.status === 404) return [];
    throw error;
  }
}

async function buildFinancialSummary() {
  const [accounts, assets, savings, liabilities, incomes, payables, repayments] = await Promise.all([
    supabaseRequest("asset_accounts", { query: "?select=id,name,balance,currency,current_exchange_rate,is_included_in_net_worth" }),
    loadAssetsWithMarketPrices(),
    supabaseRequest("savings_deposits", { query: "?select=*&order=maturity_date.asc" }),
    supabaseRequest("liabilities", { query: "?select=id,name,liability_type,original_principal,current_balance,currency,annual_interest_rate,start_date,next_payment_date,monthly_payment,repayment_method,term_in_months,min_payment_rate,min_payment_fixed_amount" }),
    supabaseRequest("recurring_incomes", { query: "?select=id,name,monthly_amount,is_active" }),
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
  const staleAssetCount = assets.filter((x) => x.price_is_stale).length;
  const assetGroups = [
    { key: "realEstate", label: "Bất động sản", categories: ["real_estate", "rental_asset"] },
    { key: "securities", label: "Chứng khoán", categories: ["stock", "etf", "listed_bond", "warrant", "foreign_stock", "other_security"] },
    { key: "gold", label: "Vàng", categories: [...GOLD_CATEGORIES] },
    { key: "funds", label: "Quỹ", categories: [...FUND_CATEGORIES] },
  ];
  const assetBreakdown = assetGroups.map((group) => ({
    key: group.key, label: group.label,
    value: assets.filter((x) => group.categories.includes(x.category)).reduce((sum, x) => sum + inVnd(Number(x.quantity) * Number(x.current_price), x.currency), 0),
    count: assets.filter((x) => group.categories.includes(x.category)).length,
  }));
  assetBreakdown.unshift({ key: "cash", label: "Tiền & tài khoản", value: accountValue, count: accounts.length });
  assetBreakdown.push({ key: "savings", label: "Tiết kiệm", value: savingsValue, count: savings.filter((x) => x.status === "active").length });
  const debtByType = new Map();
  for (const item of liabilities) {
    const current = debtByType.get(item.liability_type) || { type: item.liability_type, value: 0, count: 0 };
    current.value += inVnd(item.current_balance, item.currency);
    current.count += 1;
    debtByType.set(item.liability_type, current);
  }
  const debtBreakdown = [...debtByType.values()].sort((a, b) => b.value - a.value);
  const topAssets = assets.map((item) => ({
    id: item.id, name: item.name, category: item.category,
    value: inVnd(Number(item.quantity) * Number(item.current_price), item.currency),
    valuationDate: item.valuation_date, priceSource: item.price_source,
  })).sort((a, b) => b.value - a.value).slice(0, 6);
  const topDebts = liabilities.map((item) => ({
    id: item.id, name: item.name, type: item.liability_type,
    balance: inVnd(item.current_balance, item.currency),
    monthlyPayment: automaticDebtPayables.find((x) => x.id === item.id)?.estimated_payment || 0,
    nextPaymentDate: item.next_payment_date,
  })).sort((a, b) => b.balance - a.balance).slice(0, 5);
  const upcomingSavings = savings.filter((x) => x.status === "active" && x.maturity_date).map((item) => ({
    id: item.id, name: item.name, principal: inVnd(item.principal, item.currency),
    interest: inVnd(item.current_interest || 0, item.currency), maturityDate: item.maturity_date,
    annualRate: Number(item.annual_interest_rate || 0),
  })).sort((a, b) => String(a.maturityDate).localeCompare(String(b.maturityDate))).slice(0, 6);
  const expenseMap = new Map();
  for (const item of activePayables) expenseMap.set(item.category, (expenseMap.get(item.category) || 0) + inVnd(item.monthly_amount, item.currency));
  if (monthlyDebtPayments > 0) expenseMap.set("loan_payment", (expenseMap.get("loan_payment") || 0) + monthlyDebtPayments);
  const expenseBreakdown = [...expenseMap.entries()].map(([category, value]) => ({ category, value })).sort((a, b) => b.value - a.value);
  const incomeSources = incomes.filter((x) => x.is_active).map((x) => ({ name: x.name, value: Number(x.monthly_amount || 0) })).sort((a, b) => b.value - a.value);
  const liquidAssets = accountValue + savingsValue;
  return {
    asOfDate: new Date().toISOString(), totalAssets, debt, netWorth: totalAssets - debt,
    monthlyIncome, monthlyPayables, monthlyRecurringPayables, monthlyDebtPayments, monthlyCashFlow,
    savingsRate: monthlyIncome > 0 ? monthlyCashFlow / monthlyIncome * 100 : 0,
    debtToAssets: totalAssets > 0 ? debt / totalAssets * 100 : 0,
    allocation: { accounts: accountValue, investments: assetValue, savings: savingsValue },
    assetBreakdown, debtBreakdown, topAssets, topDebts, upcomingSavings, expenseBreakdown, incomeSources,
    liquidAssets,
    savingsInterest: savings.filter((x) => x.status === "active").reduce((sum, x) => sum + inVnd(x.current_interest || 0, x.currency), 0),
    emergencyMonths: monthlyPayables > 0 ? liquidAssets / monthlyPayables : null,
    debtServiceRatio: monthlyIncome > 0 ? monthlyDebtPayments / monthlyIncome * 100 : 0,
    cashFlowMargin: monthlyIncome > 0 ? monthlyCashFlow / monthlyIncome * 100 : 0,
    staleAssetCount,
    upcomingPayables: activePayables.concat(automaticDebtPayables.map((x) => ({
      id: `debt-${x.id}`, name: x.name,
      category: x.liability_type === "credit_card" ? "credit_card" : "loan_payment",
      monthly_amount: x.estimated_payment, currency: x.currency,
      due_day: x.next_payment_date ? new Date(`${x.next_payment_date}T00:00:00Z`).getUTCDate() : 1,
      is_auto_pay: true, source: "liability",
    }))).sort((a, b) => {
      const today = new Date().getDate();
      return ((a.due_day - today + 31) % 31) - ((b.due_day - today + 31) % 31);
    }).slice(0, 6),
    counts: { accounts: accounts.length, assets: assets.length, savings: savings.length, liabilities: liabilities.length, payables: payables.length },
  };
}

async function loadLiabilitiesWithCalculatedPayments() {
  const [liabilities, repayments] = await Promise.all([
    supabaseRequest("liabilities", { query: "?select=*&order=created_at.desc&limit=500" }),
    supabaseRequest("asset_transactions", { query: "?select=liability_id&type=eq.repayment" }),
  ]);
  const counts = repayments.reduce((result, item) => {
    if (item.liability_id) result.set(item.liability_id, (result.get(item.liability_id) || 0) + 1);
    return result;
  }, new Map());
  return liabilities.map((item) => ({
    ...item,
    calculated_monthly_payment: item.liability_type === "other_payable"
      ? null
      : estimatedMonthlyDebtPayment(item, counts.get(item.id) || 0),
  }));
}

function nextCreditCardDueDate(dueDay) {
  const now = new Date();
  let candidate = new Date(now.getFullYear(), now.getMonth(), Math.min(Math.max(Number(dueDay || 5), 1), 28));
  if (candidate <= now) candidate = new Date(now.getFullYear(), now.getMonth() + 1, Math.min(Math.max(Number(dueDay || 5), 1), 28));
  return candidate.toISOString().slice(0, 10);
}

function normalizeLiabilityBody(body, isNew) {
  const normalized = { ...body };
  if (normalized.liability_type === "credit_card") {
    normalized.original_principal = Number(normalized.credit_limit || 0);
    normalized.annual_interest_rate = Number(normalized.annual_interest_rate || 0);
    normalized.current_balance = Number(normalized.current_balance || 0);
    normalized.start_date ||= new Date().toISOString().slice(0, 10);
    normalized.next_payment_date = nextCreditCardDueDate(normalized.payment_due_day);
  } else if (normalized.liability_type === "other_payable") {
    if (isNew) normalized.original_principal = Number(normalized.current_balance || 0);
    normalized.annual_interest_rate = 0;
    normalized.next_payment_date = normalized.maturity_date || null;
  } else if (normalized.start_date && Number(normalized.term_in_months || 0) > 0) {
    const maturity = new Date(`${normalized.start_date}T00:00:00Z`);
    maturity.setUTCMonth(maturity.getUTCMonth() + Number(normalized.term_in_months));
    normalized.maturity_date = maturity.toISOString().slice(0, 10);
    if (isNew && !normalized.next_payment_date) {
      const next = new Date(`${normalized.start_date}T00:00:00Z`);
      next.setUTCMonth(next.getUTCMonth() + 1);
      normalized.next_payment_date = next.toISOString().slice(0, 10);
    }
  }
  return normalized;
}

app.use("/api/data", requireAuth, (req, res, next) => {
  if (!sameOrigin(req)) return res.status(403).json({ error: "Yêu cầu không hợp lệ." });
  next();
});

app.get("/api/data/summary", async (_req, res, next) => {
  try {
    res.json(await buildFinancialSummary());
  } catch (error) { next(error); }
});

async function invokeSupabaseFunction(name) {
  const { url, key } = supabaseConfig();
  const response = await fetch(`${url}/functions/v1/${name}`, {
    method: "POST",
    headers: { apikey: key, Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: "{}",
    signal: AbortSignal.timeout(30_000),
  });
  const text = await response.text();
  let data;
  try { data = text ? JSON.parse(text) : {}; } catch { data = { message: text }; }
  if (!response.ok) throw new Error(data?.error || `${name} trả về lỗi ${response.status}`);
  return data;
}

app.post("/api/market/refresh", requireAuth, async (req, res, next) => {
  try {
    if (!sameOrigin(req)) return res.status(403).json({ error: "Yêu cầu không hợp lệ." });
    const names = ["fetch-stock-price", "fetch-gold-price", "fetch-fund-nav"];
    const settled = await Promise.allSettled(names.map(invokeSupabaseFunction));
    const results = settled.map((result, index) => result.status === "fulfilled"
      ? { name: names[index], ok: true, ...result.value }
      : { name: names[index], ok: false, error: result.reason?.message || "Không thể cập nhật" });
    const syncedAssets = await syncMarketPricesToAssets();
    if (results.every((item) => !item.ok) && syncedAssets.available === 0) {
      return res.status(502).json({ error: "Không cập nhật được nguồn giá nào.", results, syncedAssets });
    }
    const refreshStatus = results.every((item) => item.ok) ? "complete" : results.some((item) => item.ok) ? "partial" : "cached";
    res.json({ refreshedAt: new Date().toISOString(), refreshStatus, results, syncedAssets });
  } catch (error) { next(error); }
});

let aiCache = null;
app.post("/api/ai/analysis", requireAuth, async (req, res, next) => {
  try {
    if (!sameOrigin(req)) return res.status(403).json({ error: "Yêu cầu không hợp lệ." });
    const apiKey = process.env.ANTHROPIC_API_KEY || "";
    if (!apiKey) return res.status(503).json({ error: "Chưa cấu hình ANTHROPIC_API_KEY trên Render." });
    if (!req.body?.force && aiCache && Date.now() - aiCache.cachedAt < 15 * 60_000) return res.json(aiCache.value);
    const financial = await buildFinancialSummary();
    const model = process.env.ANTHROPIC_MODEL || "claude-opus-4-8";
    const prompt = `Phân tích tình hình tài chính cá nhân tại ${financial.asOfDate} dựa trên dữ liệu VND sau:\n${JSON.stringify(financial)}\n\nTrả lời bằng tiếng Việt, ngắn gọn nhưng định lượng, theo đúng 4 mục: 1) Đánh giá hiện tại; 2) Rủi ro ưu tiên; 3) Chiến lược 30 ngày; 4) Chiến lược 6-12 tháng. Tập trung vào dòng tiền, tỷ lệ nợ, quỹ dự phòng, lịch trả nợ, thanh khoản và mức độ tập trung tài sản. Nêu tối đa 3 hành động cụ thể theo thứ tự ưu tiên. Không bịa dữ liệu, không hứa lợi nhuận, không khuyến nghị mua/bán mã chứng khoán cụ thể.`;
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "x-api-key": apiKey, "anthropic-version": "2023-06-01", "content-type": "application/json" },
      body: JSON.stringify({
        model, max_tokens: 1800,
        system: "Bạn là chuyên gia lập kế hoạch tài chính cá nhân thận trọng. Chỉ sử dụng số liệu được cung cấp; mọi chiến lược phải có lý do định lượng và cảnh báo đây là phân tích tham khảo.",
        messages: [{ role: "user", content: prompt }],
      }),
      signal: AbortSignal.timeout(45_000),
    });
    const body = await response.json();
    if (!response.ok) throw Object.assign(new Error(body?.error?.message || `Claude API trả về lỗi ${response.status}`), { status: 502 });
    const analysis = body?.content?.find((item) => item.type === "text")?.text;
    if (!analysis) throw Object.assign(new Error("Claude không trả về nội dung phân tích."), { status: 502 });
    const value = { analysis, generatedAt: new Date().toISOString(), model, disclaimer: "Phân tích AI chỉ mang tính tham khảo, không thay thế tư vấn tài chính chuyên nghiệp." };
    aiCache = { cachedAt: Date.now(), value };
    res.json(value);
  } catch (error) { next(error); }
});

app.get("/api/data/:table", async (req, res, next) => {
  try {
    if (!TABLES.has(req.params.table)) return res.status(404).json({ error: "Loại dữ liệu không tồn tại." });
    const limit = Math.min(Math.max(Number(req.query.limit) || 200, 1), 500);
    const order = req.params.table === "valuation_snapshots" ? "date.desc" : req.params.table === "asset_transactions" ? "date.desc" : "created_at.desc";
    if (req.params.table === "assets") return res.json((await loadAssetsWithMarketPrices()).slice(0, limit));
    if (req.params.table === "liabilities") return res.json((await loadLiabilitiesWithCalculatedPayments()).slice(0, limit));
    res.json(await supabaseRequest(req.params.table, { query: `?select=*&order=${order}&limit=${limit}` }));
  } catch (error) { next(error); }
});

app.post("/api/data/:table", async (req, res, next) => {
  try {
    const table = req.params.table;
    if (!TABLES.has(table) || READ_ONLY_TABLES.has(table)) return res.status(405).json({ error: "Không thể thêm loại dữ liệu này." });
    let body = { ...req.body };
    delete body.id; delete body.created_at; delete body.updated_at;
    if (table === "liabilities") body = normalizeLiabilityBody(body, true);
    if ("edited_by" in body || ["asset_accounts", "asset_transactions", "savings_deposits", "liabilities", "recurring_incomes", "monthly_payables"].includes(table)) body.edited_by = req.session.username;
    res.status(201).json(await supabaseRequest(table, { method: "POST", body }));
  } catch (error) { next(error); }
});

app.patch("/api/data/:table/:id", async (req, res, next) => {
  try {
    const table = req.params.table;
    if (!TABLES.has(table) || READ_ONLY_TABLES.has(table)) return res.status(405).json({ error: "Không thể sửa loại dữ liệu này." });
    if (!/^[0-9a-f-]{36}$/i.test(req.params.id)) return res.status(400).json({ error: "ID không hợp lệ." });
    let body = { ...req.body };
    delete body.id; delete body.created_at;
    if (table === "liabilities") body = normalizeLiabilityBody(body, false);
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
