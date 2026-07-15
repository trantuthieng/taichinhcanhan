const $ = (selector) => document.querySelector(selector);
const state = { user: null, page: "dashboard", records: [], editing: null };

const options = {
  currency: [["VND", "VND"], ["USD", "USD"], ["EUR", "EUR"], ["JPY", "JPY"], ["AUD", "AUD"], ["SGD", "SGD"]],
  accountType: [["cash_personal", "Tiền mặt cá nhân"], ["cash_family", "Tiền mặt gia đình"], ["bank_account", "Tài khoản ngân hàng"], ["salary_account", "Tài khoản nhận lương"], ["spending_account", "Tài khoản chi tiêu"], ["e_wallet", "Ví điện tử"], ["emergency_fund", "Quỹ khẩn cấp"], ["investment_fund", "Quỹ đầu tư"], ["foreign_currency_cash", "Tiền mặt ngoại tệ"]],
  assetCategory: [["real_estate", "Bất động sản"], ["rental_asset", "Bất động sản cho thuê"], ["stock", "Cổ phiếu"], ["etf", "Quỹ ETF niêm yết"], ["listed_bond", "Trái phiếu niêm yết"], ["warrant", "Chứng quyền"], ["foreign_stock", "Cổ phiếu nước ngoài"], ["other_security", "Chứng khoán khác"], ["gold_bar_sjc", "Vàng miếng SJC"], ["gold_ring_9999", "Vàng nhẫn 9999"], ["gold_bar_other_brand", "Vàng miếng thương hiệu khác"], ["gold_jewelry", "Vàng trang sức"], ["gold_24k", "Vàng 24K"], ["gold_18k", "Vàng 18K"], ["gold_14k", "Vàng 14K"], ["gold_international", "Vàng quốc tế"], ["other_gold", "Vàng khác"], ["fund_certificate", "Chứng chỉ quỹ"], ["open_end_fund", "Quỹ mở"]],
  realEstateCategory: [["real_estate", "Bất động sản"], ["rental_asset", "Bất động sản cho thuê"]],
  securitiesCategory: [["stock", "Cổ phiếu"], ["etf", "Quỹ ETF niêm yết"], ["listed_bond", "Trái phiếu niêm yết"], ["warrant", "Chứng quyền"], ["foreign_stock", "Cổ phiếu nước ngoài"], ["other_security", "Chứng khoán khác"]],
  goldCategory: [["gold_bar_sjc", "Vàng miếng SJC"], ["gold_ring_9999", "Vàng nhẫn 9999"], ["gold_bar_other_brand", "Vàng miếng thương hiệu khác"], ["gold_jewelry", "Vàng trang sức"], ["gold_24k", "Vàng 24K"], ["gold_18k", "Vàng 18K"], ["gold_14k", "Vàng 14K"], ["gold_international", "Vàng quốc tế"], ["other_gold", "Vàng khác"]],
  fundCategory: [["fund_certificate", "Chứng chỉ quỹ"], ["open_end_fund", "Quỹ mở"]],
  unit: [["share", "Cổ phiếu / CCQ"], ["luong", "Lượng"], ["cay", "Cây"], ["chi", "Chỉ"], ["phan", "Phân"], ["gram", "Gram"], ["ounce", "Ounce"], ["item", "Tài sản"]],
  liabilityType: [["mortgage_loan", "Vay mua nhà"], ["car_loan", "Vay mua xe"], ["consumer_loan", "Vay tiêu dùng"], ["unsecured_loan", "Vay tín chấp"], ["family_loan", "Vay người thân"], ["installment_plan", "Trả góp"], ["credit_card", "Thẻ tín dụng"], ["other_payable", "Khoản phải trả khác"]],
  interestRateType: [["fixed", "Cố định toàn kỳ"], ["floating", "Thả nổi / cố định rồi thả nổi"]],
  repaymentMethod: [["equal_principal", "Gốc đều, lãi giảm dần"], ["annuity", "Tổng tiền trả đều hàng kỳ"]],
  paymentFrequency: [["monthly", "Hàng tháng"], ["quarterly", "Hàng quý"], ["semi_annual", "Mỗi 6 tháng"], ["annual", "Hàng năm"], ["one_time", "Thanh toán một lần"]],
  transactionType: [["deposit", "Nạp tiền"], ["withdrawal", "Rút tiền"], ["transfer", "Chuyển tiền"], ["buy", "Mua"], ["sell", "Bán"], ["interest", "Tiền lãi"], ["dividend", "Cổ tức"], ["maturity", "Tất toán"], ["repayment", "Trả nợ"], ["fee", "Phí"], ["tax", "Thuế"], ["adjustment", "Điều chỉnh"]],
  payableCategory: [["loan_interest", "Lãi vay"], ["loan_payment", "Khoản trả vay"], ["rent", "Tiền thuê nhà"], ["credit_card", "Thẻ tín dụng"], ["utilities", "Điện, nước, internet"], ["insurance", "Bảo hiểm"], ["tax", "Thuế, phí"], ["family", "Chi phí gia đình"], ["subscription", "Dịch vụ đăng ký"], ["other", "Khoản khác"]],
};

const assetColumns = [["name", "Tên"], ["category", "Phân loại", "assetCategory"], ["symbol", "Mã"], ["quantity", "Số lượng", "number"], ["current_price", "Giá hiện tại", "money"], ["valuation_date", "Cập nhật giá", "valuation"]];
function assetFields(categorySource, defaultCategory) {
  return [["name", "Tên tài sản", "text", true], ["category", "Phân loại", "select", true, categorySource, defaultCategory], ["symbol", "Mã / ký hiệu"], ["brand", "Thương hiệu"], ["unit", "Đơn vị", "select", true, "unit", "item"], ["quantity", "Số lượng", "number", true, null, 1], ["average_cost", "Giá vốn bình quân", "number", true, null, 0], ["current_price", "Giá hiện tại", "number", true, null, 0], ["currency", "Tiền tệ", "select", true, "currency", "VND"], ["acquisition_date", "Ngày mua", "date"], ["valuation_date", "Ngày cập nhật giá", "date", true], ["valuation_source", "Nguồn định giá"], ["target_price", "Giá mục tiêu", "number"], ["note", "Ghi chú", "textarea"]];
}
function assetPage(label, icon, title, eyebrow, singular, categories, categorySource, refreshMarket = false) {
  return { label, icon, title, eyebrow, singular, table: "assets", categories, refreshMarket, columns: assetColumns, fields: assetFields(categorySource, categories[0]) };
}

const pages = {
  dashboard: { label: "Tổng quan", icon: "⌂", title: "Bức tranh tài chính", eyebrow: "TỔNG QUAN" },
  asset_accounts: {
    label: "Tài khoản", icon: "▣", title: "Tài khoản tiền", eyebrow: "TÀI SẢN THANH KHOẢN", singular: "tài khoản",
    columns: [["name", "Tên"], ["institution", "Nơi quản lý"], ["account_type", "Loại", "accountType"], ["balance", "Số dư", "money"], ["currency", "Tiền tệ"]],
    fields: [["name", "Tên tài khoản", "text", true], ["institution", "Ngân hàng / nơi quản lý"], ["account_type", "Loại tài khoản", "select", true, "accountType"], ["currency", "Tiền tệ", "select", true, "currency", "VND"], ["balance", "Số dư", "number", true, null, 0], ["current_exchange_rate", "Tỷ giá hiện tại", "number"], ["is_included_in_net_worth", "Tính vào tài sản ròng", "checkbox", false, null, true], ["target_group", "Nhóm mục tiêu"], ["note", "Ghi chú", "textarea"]],
  },
  real_estate: assetPage("Bất động sản", "⌂", "Danh mục bất động sản", "TÀI SẢN", "bất động sản", ["real_estate", "rental_asset"], "realEstateCategory"),
  securities: assetPage("Chứng khoán", "↗", "Danh mục chứng khoán", "ĐẦU TƯ", "mã chứng khoán", ["stock", "etf", "listed_bond", "warrant", "foreign_stock", "other_security"], "securitiesCategory", true),
  gold: assetPage("Vàng", "◇", "Danh mục vàng", "TÀI SẢN PHÒNG THỦ", "khoản vàng", ["gold_bar_sjc", "gold_ring_9999", "gold_bar_other_brand", "gold_jewelry", "gold_24k", "gold_18k", "gold_14k", "gold_international", "other_gold"], "goldCategory", true),
  funds: assetPage("Quỹ", "◫", "Danh mục quỹ", "ĐẦU TƯ QUỸ", "khoản đầu tư quỹ", ["fund_certificate", "open_end_fund"], "fundCategory", true),
  savings_deposits: {
    label: "Tiết kiệm", icon: "◉", title: "Sổ tiết kiệm", eyebrow: "TIỀN GỬI", singular: "sổ tiết kiệm",
    columns: [["name", "Tên sổ"], ["principal", "Tiền gốc", "money"], ["current_interest", "Lãi hiện tại", "money"], ["annual_interest_rate", "Lãi suất/năm", "percent"], ["term_in_days", "Kỳ hạn", "termDays"], ["progress_days", "Tiến độ", "progress"], ["maturity_date", "Ngày đáo hạn", "date"], ["contract_number", "Số tài khoản"]],
    fields: [["name", "Tên sổ", "text", true], ["bank_name", "Ngân hàng", "text", true], ["principal", "Tiền gốc", "number", true], ["current_interest", "Lãi hiện tại", "number"], ["currency", "Tiền tệ", "select", true, "currency", "VND"], ["annual_interest_rate", "Lãi suất năm (%)", "number", true], ["start_date", "Ngày gửi", "date", true], ["maturity_date", "Ngày đáo hạn", "date", true], ["term_in_months", "Kỳ hạn (tháng)", "number", true], ["term_in_days", "Kỳ hạn (ngày)", "number"], ["progress_days", "Tiến độ hiện tại (ngày)", "number"], ["interest_snapshot_date", "Ngày chốt lãi và tiến độ", "date"], ["interest_payment_type", "Trả lãi", "select", true, [["end_of_term", "Cuối kỳ"], ["monthly", "Hàng tháng"], ["upfront", "Trả trước"]], "end_of_term"], ["auto_renewal_type", "Tái tục", "select", false, [["none", "Không tái tục"], ["principal_only", "Chỉ tiền gốc"], ["principal_and_interest", "Gốc và lãi"]], "none"], ["status", "Trạng thái", "select", true, [["active", "Đang hoạt động"], ["matured", "Đã đáo hạn"], ["closed", "Đã đóng"], ["withdrawn_early", "Rút trước hạn"]], "active"], ["contract_number", "Số tài khoản"], ["source_image", "Ảnh nguồn"]],
  },
  liabilities: {
    label: "Nợ phải trả", icon: "▾", title: "Nợ phải trả", eyebrow: "NGHĨA VỤ TÀI CHÍNH", singular: "khoản nợ",
    columns: [["name", "Tên"], ["liability_type", "Loại", "liabilityType"], ["lender", "Bên cho vay"], ["current_balance", "Dư nợ", "money"], ["annual_interest_rate", "Lãi suất", "percent"], ["calculated_monthly_payment", "Kỳ trả dự kiến", "money"], ["next_payment_date", "Kỳ trả tới", "date"]],
    fields: [
      ["name", "Tên khoản nợ", "text", true], ["liability_type", "Loại nợ", "select", true, "liabilityType", "other_payable"], ["lender", "Bên cho vay / ngân hàng"], ["currency", "Tiền tệ", "select", true, "currency", "VND"], ["current_balance", "Dư nợ hiện tại", "number", true], ["start_date", "Ngày bắt đầu / phát sinh", "date", true], ["annual_interest_rate", "Lãi suất năm (%)", "number", false, null, 0, "interest"],
      ["original_principal", "Số tiền vay ban đầu", "number", true, null, null, "term"], ["interest_rate_type", "Cơ chế lãi suất", "select", true, "interestRateType", "fixed", "term"], ["fixed_rate_end_date", "Ngày bắt đầu thả nổi", "date", false, null, null, "term"], ["repayment_method", "Phương thức trả", "select", true, "repaymentMethod", "annuity", "term"], ["term_in_months", "Kỳ hạn (tháng)", "number", true, null, 12, "term"], ["payment_frequency", "Kỳ thanh toán", "select", true, "paymentFrequency", "monthly", "term"], ["early_repayment_fee_rate", "Phí trả trước hạn (%)", "number", false, null, null, "term"], ["grace_period_months", "Ân hạn gốc (tháng)", "number", false, null, null, "term"], ["collateral", "Tài sản bảo đảm", "text", false, null, null, "term"],
      ["credit_limit", "Hạn mức tín dụng", "number", true, null, null, "credit"], ["statement_day", "Ngày sao kê", "number", true, null, 15, "credit"], ["payment_due_day", "Ngày đến hạn", "number", true, null, 5, "credit"], ["interest_free_days", "Số ngày miễn lãi", "number", true, null, 45, "credit"], ["min_payment_rate", "Tỷ lệ thanh toán tối thiểu (%)", "number", true, null, 5, "credit"], ["min_payment_fixed_amount", "Số tiền tối thiểu cố định", "number", false, null, 0, "credit"], ["annual_fee", "Phí thường niên", "number", false, null, 0, "credit"], ["late_fee", "Phí trả chậm", "number", false, null, 0, "credit"],
      ["maturity_date", "Hạn trả dự kiến", "date", false, null, null, "other"], ["note", "Ghi chú", "textarea"]
    ],
  },
  recurring_incomes: {
    label: "Thu nhập", icon: "+", title: "Thu nhập định kỳ", eyebrow: "DÒNG TIỀN", singular: "nguồn thu",
    columns: [["name", "Nguồn thu"], ["monthly_amount", "Mỗi tháng", "money"], ["day_of_month", "Ngày nhận"], ["start_date", "Bắt đầu", "date"], ["end_date", "Kết thúc", "date"], ["is_active", "Hoạt động", "boolean"]],
    fields: [["name", "Tên nguồn thu", "text", true], ["monthly_amount", "Số tiền hàng tháng", "number", true], ["day_of_month", "Ngày nhận trong tháng", "number", true, null, 1], ["start_date", "Ngày bắt đầu", "date", true], ["end_date", "Ngày kết thúc", "date"], ["is_active", "Đang hoạt động", "checkbox", false, null, true], ["note", "Ghi chú", "textarea"]],
  },
  monthly_payables: {
    label: "Phải trả tháng", icon: "₫", title: "Khoản phải trả hàng tháng", eyebrow: "DÒNG TIỀN RA", singular: "khoản phải trả",
    columns: [["name", "Khoản phải trả"], ["category", "Phân loại", "payableCategory"], ["monthly_amount", "Mỗi tháng", "money"], ["due_day", "Ngày đến hạn"], ["is_auto_pay", "Tự động", "boolean"], ["is_active", "Hoạt động", "boolean"]],
    fields: [["name", "Tên khoản phải trả", "text", true], ["category", "Phân loại", "select", true, "payableCategory", "other"], ["monthly_amount", "Số tiền hàng tháng", "number", true], ["currency", "Tiền tệ", "select", true, "currency", "VND"], ["due_day", "Ngày đến hạn trong tháng", "number", true, null, 1], ["start_date", "Ngày bắt đầu", "date", true], ["end_date", "Ngày kết thúc", "date"], ["is_auto_pay", "Đã cài thanh toán tự động", "checkbox", false, null, false], ["is_active", "Đang theo dõi", "checkbox", false, null, true], ["note", "Ghi chú", "textarea"]],
  },
  asset_transactions: {
    label: "Giao dịch", icon: "⇄", title: "Lịch sử giao dịch", eyebrow: "DÒNG TIỀN", singular: "giao dịch",
    columns: [["type", "Loại", "transactionType"], ["date", "Thời gian", "datetime"], ["amount", "Số tiền", "money"], ["fee", "Phí", "money"], ["tax", "Thuế", "money"], ["note", "Ghi chú"]],
    fields: [["type", "Loại giao dịch", "select", true, "transactionType"], ["date", "Ngày giao dịch", "datetime-local", true], ["amount", "Số tiền", "number", true], ["quantity", "Số lượng", "number"], ["unit_price", "Đơn giá", "number"], ["fee", "Phí", "number", true, null, 0], ["tax", "Thuế", "number", true, null, 0], ["note", "Ghi chú", "textarea"]],
  },
};

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
}

async function api(path, init = {}) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json", ...(init.headers || {}) }, ...init });
  const text = await response.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (response.status === 401 && path !== "/api/login") showLogin();
  if (!response.ok) throw new Error(data?.error || "Không thể kết nối máy chủ.");
  return data;
}

function money(value, currency = "VND") {
  return new Intl.NumberFormat("vi-VN", { style: "currency", currency, maximumFractionDigits: currency === "VND" ? 0 : 2 }).format(Number(value || 0));
}

function optionLabel(group, value) {
  const list = Array.isArray(group) ? group : options[group] || [];
  return list.find(([key]) => key === value)?.[1] || value || "—";
}

function formatCell(record, [key, _label, format]) {
  const value = record[key];
  if (value === null || value === undefined || value === "") return "—";
  if (format === "money") return money(value, record.currency || "VND");
  if (format === "number") return new Intl.NumberFormat("vi-VN").format(Number(value));
  if (format === "percent") return `${new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 2 }).format(Number(value))}%`;
  if (format === "termDays") return `${new Intl.NumberFormat("vi-VN").format(Number(value))} ngày`;
  if (format === "progress") return `${new Intl.NumberFormat("vi-VN").format(Number(value))}/${new Intl.NumberFormat("vi-VN").format(Number(record.term_in_days || 0))} ngày`;
  if (format === "date") return new Intl.DateTimeFormat("vi-VN").format(new Date(`${value}T00:00:00`));
  if (format === "datetime") return new Intl.DateTimeFormat("vi-VN", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
  if (format === "valuation") {
    const date = new Intl.DateTimeFormat("vi-VN").format(new Date(value));
    return `${date} · ${record.price_source || "Nhập tay"}${record.price_is_stale ? " · Cần cập nhật" : ""}`;
  }
  if (format === "boolean") return value ? "Đang bật" : "Đã tắt";
  if (format) return optionLabel(format, value);
  return value;
}

function showLogin() {
  state.user = null;
  $("#loginView").classList.remove("hidden");
  $("#appView").classList.add("hidden");
}

function showApp(user) {
  state.user = user;
  $("#loginView").classList.add("hidden");
  $("#appView").classList.remove("hidden");
  $("#currentUser").textContent = user;
  $("#userInitial").textContent = user.slice(0, 1).toUpperCase();
  renderNav();
  navigate("dashboard");
}

function renderNav() {
  $("#nav").innerHTML = Object.entries(pages).map(([key, page]) => `<button class="nav-button ${state.page === key ? "active" : ""}" data-page="${key}"><span class="nav-icon">${page.icon}</span>${page.label}</button>`).join("");
}

async function navigate(pageKey) {
  state.page = pageKey;
  const page = pages[pageKey];
  $("#pageTitle").textContent = page.title;
  $("#pageEyebrow").textContent = page.eyebrow;
  renderNav();
  $(".sidebar").classList.remove("open");
  $("#content").innerHTML = '<div class="loading">Đang tải dữ liệu…</div>';
  try {
    if (pageKey === "dashboard") return await renderDashboard();
    state.records = await api(`/api/data/${page.table || pageKey}`);
    if (page.categories) state.records = state.records.filter((record) => page.categories.includes(record.category));
    renderTable();
  } catch (error) { renderError(error); }
}

async function renderDashboard() {
  const data = await api("/api/data/summary");
  const allocation = [
    ["Tiền & tài khoản", data.allocation.accounts], ["Đầu tư & tài sản", data.allocation.investments],
    ["Tiết kiệm", data.allocation.savings],
  ];
  const allocationTotal = allocation.reduce((sum, [, value]) => sum + value, 0) || 1;
  const cashFlowPositive = data.monthlyCashFlow >= 0;
  $("#content").innerHTML = `
    ${data.staleAssetCount ? `<div class="freshness-alert"><strong>${data.staleAssetCount} tài sản chưa có giá cập nhật hôm nay.</strong><span>Giá thị trường được tự động lấy khi có nguồn; bất động sản cần cập nhật định giá thủ công.</span></div>` : `<div class="freshness-alert fresh"><strong>Dữ liệu giá đã cập nhật đến hôm nay.</strong><span>Thời điểm báo cáo: ${new Intl.DateTimeFormat("vi-VN", { dateStyle: "short", timeStyle: "short" }).format(new Date(data.asOfDate))}</span></div>`}
    <section class="summary-grid">
      <article class="summary-card accent"><span>TÀI SẢN RÒNG</span><strong>${money(data.netWorth)}</strong></article>
      <article class="summary-card"><span>TỔNG TÀI SẢN</span><strong>${money(data.totalAssets)}</strong></article>
      <article class="summary-card"><span>TỔNG DƯ NỢ</span><strong>${money(data.debt)}</strong></article>
      <article class="summary-card"><span>THU NHẬP / THÁNG</span><strong>${money(data.monthlyIncome)}</strong></article>
      <article class="summary-card outgoing"><span>PHẢI TRẢ / THÁNG</span><strong>${money(data.monthlyPayables)}</strong></article>
      <article class="summary-card ${cashFlowPositive ? "positive" : "negative"}"><span>DÒNG TIỀN RÒNG</span><strong>${cashFlowPositive ? "+" : ""}${money(data.monthlyCashFlow)}</strong></article>
    </section>
    <section class="dashboard-grid">
      <article class="panel"><div class="panel-header"><h3>Cơ cấu tài sản</h3><span class="muted">Theo giá trị hiện tại</span></div>
        ${allocation.map(([label, value]) => `<div class="allocation-row value"><span>${label}</span><div class="bar"><i style="width:${value / allocationTotal * 100}%"></i></div><strong>${(value / allocationTotal * 100).toFixed(1)}%</strong></div>`).join("")}
      </article>
      <article class="panel"><div class="panel-header"><h3>Sức khỏe tài chính</h3></div><div class="quick-stats">
        <div class="quick-stat"><span>Tỷ lệ tiết kiệm</span><strong class="${data.savingsRate >= 20 ? "good" : "warn"}">${data.savingsRate.toFixed(1)}%</strong></div>
        <div class="quick-stat"><span>Tỷ lệ nợ / tài sản</span><strong class="${data.debtToAssets <= 50 ? "good" : "warn"}">${data.debtToAssets.toFixed(1)}%</strong></div>
        <div class="quick-stat"><span>Phải trả / thu nhập</span><strong>${data.monthlyIncome ? (data.monthlyPayables / data.monthlyIncome * 100).toFixed(1) : "0.0"}%</strong></div>
        <div class="quick-stat"><span>Trả nợ & trả góp / tháng</span><strong>${money(data.monthlyDebtPayments)}</strong></div>
        <div class="quick-stat"><span>Trạng thái dòng tiền</span><strong class="${cashFlowPositive ? "good" : "bad"}">${cashFlowPositive ? "Dương" : "Âm"}</strong></div>
      </div></article>
      <article class="panel cash-flow-panel"><div class="panel-header"><h3>Dòng tiền hàng tháng</h3><span class="muted">Thu nhập định kỳ và khoản phải trả</span></div>
        <div class="cash-flow-visual">
          <div><span>Tiền vào</span><strong>${money(data.monthlyIncome)}</strong><i class="income" style="width:100%"></i></div>
          <div><span>Trả nợ</span><strong>${money(data.monthlyDebtPayments)}</strong><i class="debt" style="width:${data.monthlyIncome ? Math.min(data.monthlyDebtPayments / data.monthlyIncome * 100, 100) : (data.monthlyDebtPayments ? 100 : 0)}%"></i></div>
          <div><span>Chi định kỳ</span><strong>${money(data.monthlyRecurringPayables)}</strong><i class="expense" style="width:${data.monthlyIncome ? Math.min(data.monthlyRecurringPayables / data.monthlyIncome * 100, 100) : (data.monthlyRecurringPayables ? 100 : 0)}%"></i></div>
        </div>
      </article>
      <article class="panel"><div class="panel-header"><h3>Sắp đến hạn hàng tháng</h3><button class="secondary-button" data-page="monthly_payables">Quản lý</button></div>
        <div class="due-list">${data.upcomingPayables.length ? data.upcomingPayables.map((item) => `<div class="due-item"><span class="due-day">${item.due_day}</span><div><strong>${escapeHtml(item.name)}</strong><small>${escapeHtml(optionLabel("payableCategory", item.category))}${item.source === "liability" ? " · Tự động từ khoản nợ" : item.is_auto_pay ? " · Thanh toán tự động" : ""}</small></div><b>${money(item.monthly_amount, item.currency)}</b></div>`).join("") : '<div class="empty-compact">Chưa có khoản phải trả định kỳ.</div>'}</div>
      </article>
    </section>
    <section class="panel ai-panel">
      <div class="panel-header"><div><p class="eyebrow">CLAUDE AI</p><h3>Phân tích & chiến lược tài chính</h3></div><button class="primary-button" data-ai-analysis>Phân tích ngay</button></div>
      <div id="aiAnalysis" class="ai-analysis"><strong>Nhận đánh giá dựa trên số liệu hiện tại</strong><span>Claude sẽ phân tích dòng tiền, nợ, thanh khoản, cơ cấu tài sản và đề xuất thứ tự hành động.</span></div>
      <p class="ai-disclaimer">Phân tích AI chỉ mang tính tham khảo, không thay thế tư vấn tài chính chuyên nghiệp.</p>
    </section>`;
}

function renderTable() {
  const page = pages[state.page];
  const rows = state.records.map((record) => `<tr>${page.columns.map((column) => `<td>${escapeHtml(formatCell(record, column))}</td>`).join("")}<td><div class="actions"><button data-edit="${record.id}" title="Sửa">✎</button><button class="delete" data-delete="${record.id}" title="Xóa">⌫</button></div></td></tr>`).join("");
  $("#content").innerHTML = `
    <div class="section-header"><div><h3>${state.records.length} ${page.singular}</h3><span class="muted">Dữ liệu đồng bộ với ứng dụng iPhone${page.table === "assets" ? " · Giá trị theo ngày cập nhật hiển thị" : ""}</span></div><div class="header-actions">${page.refreshMarket ? '<button class="secondary-button" data-refresh-market>↻ Cập nhật giá hôm nay</button>' : ""}<button id="addButton" class="primary-button">+ Thêm ${page.singular}</button></div></div>
    <div class="table-wrap">${rows ? `<table><thead><tr>${page.columns.map(([, label]) => `<th>${label}</th>`).join("")}<th></th></tr></thead><tbody>${rows}</tbody></table>` : `<div class="empty-state"><strong>Chưa có ${page.singular}</strong><span>Bấm nút thêm để tạo dữ liệu đầu tiên.</span></div>`}</div>`;
}

function fieldOptions(source) {
  return Array.isArray(source) ? source : options[source] || [];
}

function inputValue(record, name, fallback, type) {
  if (!record && type === "date" && ["start_date", "valuation_date"].includes(name) && fallback === undefined) return new Date().toISOString().slice(0, 10);
  const value = record?.[name] ?? fallback ?? "";
  if (type === "datetime-local" && value) return new Date(value).toISOString().slice(0, 16);
  if (type === "date" && value) return String(value).slice(0, 10);
  return value;
}

function renderField(field, record) {
  const [name, label, type = "text", required = false, source, fallback, group] = field;
  const value = inputValue(record, name, fallback, type);
  let control;
  if (type === "checkbox") control = `<label class="checkbox-label"><input name="${name}" type="checkbox" ${value ? "checked" : ""}> ${label}</label>`;
  else if (type === "select") control = `<label>${label}<select name="${name}" ${required ? "required" : ""}><option value="">— Chọn —</option>${fieldOptions(source).map(([key, text]) => `<option value="${escapeHtml(key)}" ${key === value ? "selected" : ""}>${escapeHtml(text)}</option>`).join("")}</select></label>`;
  else if (type === "textarea") control = `<label class="full">${label}<textarea name="${name}">${escapeHtml(value)}</textarea></label>`;
  else {
    const step = type === "number" ? 'step="any"' : "";
    control = `<label>${label}<input name="${name}" type="${type}" value="${escapeHtml(value)}" ${step} ${required ? "required" : ""}></label>`;
  }
  return group ? `<div class="conditional-field ${type === "textarea" ? "full" : ""}" data-liability-group="${group}">${control}</div>` : control;
}

function openModal(record = null) {
  const page = pages[state.page];
  state.editing = record;
  $("#modalEyebrow").textContent = record ? "CẬP NHẬT" : "THÊM MỚI";
  $("#modalTitle").textContent = record ? `Sửa ${page.singular}` : `Thêm ${page.singular}`;
  const liabilityPreview = state.page === "liabilities" ? '<div id="liabilityPreview" class="liability-preview full"></div>' : "";
  $("#dataForm").innerHTML = page.fields.map((field) => renderField(field, record)).join("") + liabilityPreview + `<p class="form-error full" id="dataError"></p><div class="form-actions"><button type="button" class="secondary-button" data-close>Hủy</button><button type="submit" class="primary-button">${record ? "Lưu thay đổi" : "Thêm mới"}</button></div>`;
  $("#modal").classList.remove("hidden");
  if (state.page === "liabilities") setupLiabilityForm(record);
}

function closeModal() { $("#modal").classList.add("hidden"); state.editing = null; }

function serializeForm(form) {
  const page = pages[state.page];
  const data = {};
  for (const [name, _label, type = "text"] of page.fields) {
    const input = form.elements[name];
    if (!input || input.disabled) continue;
    if (type === "checkbox") data[name] = input.checked;
    else if (input.value !== "") data[name] = type === "number" ? Number(input.value) : type === "datetime-local" ? new Date(input.value).toISOString() : input.value;
    else if (state.editing) data[name] = null;
  }
  return data;
}

function liabilityGroup(type) {
  if (type === "credit_card") return "credit";
  if (type === "other_payable") return "other";
  return "term";
}

function setupLiabilityForm(record) {
  const form = $("#dataForm");
  form.querySelectorAll("[required]").forEach((input) => { input.dataset.wasRequired = "true"; });
  const typeInput = form.elements.liability_type;
  const updateVisibility = () => {
    const group = liabilityGroup(typeInput.value);
    form.querySelectorAll("[data-liability-group]").forEach((wrapper) => {
      const fieldGroup = wrapper.dataset.liabilityGroup;
      const visible = fieldGroup === group || (fieldGroup === "interest" && group !== "other");
      wrapper.classList.toggle("hidden", !visible);
      wrapper.querySelectorAll("input,select,textarea").forEach((input) => {
        input.disabled = !visible;
        if (!visible) input.removeAttribute("required");
        else if (input.dataset.wasRequired === "true") input.required = true;
      });
    });
    const fixedEndInput = form.elements.fixed_rate_end_date;
    if (fixedEndInput) {
      const wrapper = fixedEndInput.closest("[data-liability-group]");
      const visible = group === "term" && form.elements.interest_rate_type?.value === "floating";
      wrapper.classList.toggle("hidden", !visible);
      fixedEndInput.disabled = !visible;
    }
    const interestInput = form.elements.annual_interest_rate;
    if (interestInput) interestInput.required = group === "term";
    updateLiabilityPreview(record);
  };
  typeInput.addEventListener("change", updateVisibility);
  form.elements.interest_rate_type?.addEventListener("change", updateVisibility);
  form.addEventListener("input", () => updateLiabilityPreview(record));
  updateVisibility();
}

function updateLiabilityPreview(record) {
  const form = $("#dataForm");
  const preview = $("#liabilityPreview");
  if (!form || !preview) return;
  const type = form.elements.liability_type?.value;
  const group = liabilityGroup(type);
  const balance = Number(form.elements.current_balance?.value || 0);
  let amount = 0;
  let label = "Số phải trả kỳ tới (ước tính)";
  if (group === "credit") {
    const rate = Number(form.elements.min_payment_rate?.value || 0);
    const fixed = Number(form.elements.min_payment_fixed_amount?.value || 0);
    amount = Math.min(balance, Math.max(balance * rate / 100, fixed));
    label = "Thanh toán tối thiểu kỳ tới";
  } else if (group === "other") {
    amount = balance;
    label = "Tổng khoản phải trả";
  } else {
    const original = Number(form.elements.original_principal?.value || 0);
    const months = Number(form.elements.term_in_months?.value || 0);
    const monthlyRate = Number(form.elements.annual_interest_rate?.value || 0) / 100 / 12;
    const method = form.elements.repayment_method?.value;
    if (record && original === Number(record.original_principal) && months === Number(record.term_in_months) && Number(record.calculated_monthly_payment) > 0) amount = Number(record.calculated_monthly_payment);
    else if (months > 0 && method === "equal_principal") amount = original / months + balance * monthlyRate;
    else if (months > 0 && monthlyRate === 0) amount = original / months;
    else if (months > 0) {
      const growth = Math.pow(1 + monthlyRate, months);
      amount = original * monthlyRate * growth / (growth - 1);
    }
  }
  preview.innerHTML = `<span>${label}</span><strong>${money(Number.isFinite(amount) ? amount : 0)}</strong><small>Tự động tính theo cùng nguyên tắc với ứng dụng iOS.</small>`;
}

async function saveRecord(event) {
  event.preventDefault();
  const button = event.target.querySelector('[type="submit"]');
  button.disabled = true;
  $("#dataError").textContent = "";
  try {
    const wasEditing = Boolean(state.editing);
    const table = pages[state.page].table || state.page;
    const path = state.editing ? `/api/data/${table}/${state.editing.id}` : `/api/data/${table}`;
    await api(path, { method: state.editing ? "PATCH" : "POST", body: JSON.stringify(serializeForm(event.target)) });
    closeModal();
    toast(wasEditing ? "Đã lưu thay đổi." : "Đã thêm dữ liệu.");
    await navigate(state.page);
  } catch (error) {
    $("#dataError").textContent = error.message;
    button.disabled = false;
  }
}

async function deleteRecord(id) {
  const page = pages[state.page];
  if (!confirm(`Xóa ${page.singular} này? Thao tác không thể hoàn tác.`)) return;
  try {
    await api(`/api/data/${page.table || state.page}/${id}`, { method: "DELETE" });
    toast("Đã xóa dữ liệu.");
    await navigate(state.page);
  } catch (error) { toast(error.message, true); }
}

function renderError(error) {
  $("#content").innerHTML = `<div class="empty-state"><strong>Không tải được dữ liệu</strong><span>${escapeHtml(error.message)}</span><br><br><button class="secondary-button" data-retry>Thử lại</button></div>`;
}

async function refreshMarketPrices(button) {
  button.disabled = true;
  button.textContent = "Đang cập nhật…";
  try {
    const result = await api("/api/market/refresh", { method: "POST", body: "{}" });
    const failures = result.results.filter((item) => !item.ok).length;
    toast(failures ? `Đã cập nhật, ${failures} nguồn gặp lỗi.` : "Đã cập nhật giá thị trường mới nhất.", failures > 0);
    await navigate(state.page);
  } catch (error) {
    toast(error.message, true);
    button.disabled = false;
    button.textContent = "↻ Cập nhật giá hôm nay";
  }
}

async function generateAIAnalysis(button) {
  button.disabled = true;
  button.textContent = "Claude đang phân tích…";
  const output = $("#aiAnalysis");
  output.classList.add("loading-ai");
  output.textContent = "Đang tổng hợp tài sản, dư nợ và dòng tiền hiện tại…";
  try {
    const result = await api("/api/ai/analysis", { method: "POST", body: JSON.stringify({ force: true }) });
    output.classList.remove("loading-ai");
    output.innerHTML = "";
    const text = document.createElement("div");
    text.className = "ai-text";
    text.textContent = result.analysis;
    const meta = document.createElement("small");
    meta.textContent = `${result.model} · ${new Intl.DateTimeFormat("vi-VN", { dateStyle: "short", timeStyle: "short" }).format(new Date(result.generatedAt))}`;
    output.append(text, meta);
  } catch (error) {
    output.classList.remove("loading-ai");
    output.innerHTML = `<strong>Chưa thể phân tích</strong><span>${escapeHtml(error.message)}</span>`;
  } finally {
    button.disabled = false;
    button.textContent = "Phân tích lại";
  }
}

let toastTimer;
function toast(message, isError = false) {
  clearTimeout(toastTimer);
  $("#toast").textContent = message;
  $("#toast").className = `toast${isError ? " error" : ""}`;
  toastTimer = setTimeout(() => $("#toast").classList.add("hidden"), 3500);
}

$("#loginForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = event.target.querySelector("button");
  button.disabled = true;
  $("#loginError").textContent = "";
  try {
    const values = Object.fromEntries(new FormData(event.target));
    const result = await api("/api/login", { method: "POST", body: JSON.stringify(values) });
    event.target.reset();
    showApp(result.username);
  } catch (error) { $("#loginError").textContent = error.message; }
  finally { button.disabled = false; }
});

$("#logoutButton").addEventListener("click", async () => { try { await api("/api/logout", { method: "POST" }); } finally { showLogin(); } });
$("#menuButton").addEventListener("click", () => $(".sidebar").classList.toggle("open"));
$("#modalClose").addEventListener("click", closeModal);
$("#modal").addEventListener("click", (event) => { if (event.target === $("#modal") || event.target.closest("[data-close]")) closeModal(); });
$("#dataForm").addEventListener("submit", saveRecord);
document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeModal(); });
document.addEventListener("click", (event) => {
  const nav = event.target.closest("[data-page]"); if (nav) navigate(nav.dataset.page);
  if (event.target.closest("#addButton")) openModal();
  const edit = event.target.closest("[data-edit]"); if (edit) openModal(state.records.find((item) => item.id === edit.dataset.edit));
  const remove = event.target.closest("[data-delete]"); if (remove) deleteRecord(remove.dataset.delete);
  const refresh = event.target.closest("[data-refresh-market]"); if (refresh) refreshMarketPrices(refresh);
  const ai = event.target.closest("[data-ai-analysis]"); if (ai) generateAIAnalysis(ai);
  if (event.target.closest("[data-retry]")) navigate(state.page);
});

$("#today").textContent = new Intl.DateTimeFormat("vi-VN", { weekday: "long", day: "2-digit", month: "2-digit", year: "numeric" }).format(new Date());
api("/api/session").then((session) => showApp(session.username)).catch(showLogin);
