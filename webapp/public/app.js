const $ = (selector) => document.querySelector(selector);
const state = { user: null, page: "dashboard", records: [], editing: null };

const options = {
  currency: [["VND", "VND"], ["USD", "USD"], ["EUR", "EUR"], ["JPY", "JPY"], ["AUD", "AUD"], ["SGD", "SGD"]],
  accountType: [["cash_personal", "Tiền mặt cá nhân"], ["cash_family", "Tiền mặt gia đình"], ["bank_account", "Tài khoản ngân hàng"], ["salary_account", "Tài khoản nhận lương"], ["spending_account", "Tài khoản chi tiêu"], ["e_wallet", "Ví điện tử"], ["emergency_fund", "Quỹ khẩn cấp"], ["investment_fund", "Quỹ đầu tư"], ["foreign_currency_cash", "Tiền mặt ngoại tệ"]],
  assetCategory: [["stock", "Cổ phiếu"], ["fund_certificate", "Chứng chỉ quỹ"], ["etf", "Quỹ ETF"], ["listed_bond", "Trái phiếu niêm yết"], ["foreign_stock", "Cổ phiếu nước ngoài"], ["gold_bar_sjc", "Vàng miếng SJC"], ["gold_ring_9999", "Vàng nhẫn 9999"], ["gold_jewelry", "Vàng trang sức"], ["real_estate", "Bất động sản"], ["car", "Ô tô"], ["motorbike", "Xe máy"], ["crypto", "Tiền mã hóa"], ["business_equity", "Vốn góp kinh doanh"], ["other_security", "Tài sản khác"]],
  unit: [["share", "Cổ phiếu / CCQ"], ["luong", "Lượng"], ["cay", "Cây"], ["chi", "Chỉ"], ["phan", "Phân"], ["gram", "Gram"], ["ounce", "Ounce"], ["item", "Tài sản"]],
  liabilityType: [["mortgage_loan", "Vay mua nhà"], ["car_loan", "Vay mua xe"], ["consumer_loan", "Vay tiêu dùng"], ["unsecured_loan", "Vay tín chấp"], ["family_loan", "Vay người thân"], ["installment_plan", "Trả góp"], ["credit_card", "Thẻ tín dụng"], ["other_payable", "Khoản phải trả khác"]],
  transactionType: [["deposit", "Nạp tiền"], ["withdrawal", "Rút tiền"], ["transfer", "Chuyển tiền"], ["buy", "Mua"], ["sell", "Bán"], ["interest", "Tiền lãi"], ["dividend", "Cổ tức"], ["maturity", "Tất toán"], ["repayment", "Trả nợ"], ["fee", "Phí"], ["tax", "Thuế"], ["adjustment", "Điều chỉnh"]],
  payableCategory: [["loan_interest", "Lãi vay"], ["loan_payment", "Khoản trả vay"], ["rent", "Tiền thuê nhà"], ["credit_card", "Thẻ tín dụng"], ["utilities", "Điện, nước, internet"], ["insurance", "Bảo hiểm"], ["tax", "Thuế, phí"], ["family", "Chi phí gia đình"], ["subscription", "Dịch vụ đăng ký"], ["other", "Khoản khác"]],
};

const pages = {
  dashboard: { label: "Tổng quan", icon: "⌂", title: "Bức tranh tài chính", eyebrow: "TỔNG QUAN" },
  asset_accounts: {
    label: "Tài khoản", icon: "▣", title: "Tài khoản tiền", eyebrow: "TÀI SẢN THANH KHOẢN", singular: "tài khoản",
    columns: [["name", "Tên"], ["institution", "Nơi quản lý"], ["account_type", "Loại", "accountType"], ["balance", "Số dư", "money"], ["currency", "Tiền tệ"]],
    fields: [["name", "Tên tài khoản", "text", true], ["institution", "Ngân hàng / nơi quản lý"], ["account_type", "Loại tài khoản", "select", true, "accountType"], ["currency", "Tiền tệ", "select", true, "currency", "VND"], ["balance", "Số dư", "number", true, null, 0], ["current_exchange_rate", "Tỷ giá hiện tại", "number"], ["is_included_in_net_worth", "Tính vào tài sản ròng", "checkbox", false, null, true], ["target_group", "Nhóm mục tiêu"], ["note", "Ghi chú", "textarea"]],
  },
  assets: {
    label: "Tài sản", icon: "◆", title: "Danh mục tài sản", eyebrow: "ĐẦU TƯ & TÀI SẢN", singular: "tài sản",
    columns: [["name", "Tên"], ["category", "Phân loại", "assetCategory"], ["symbol", "Mã"], ["quantity", "Số lượng", "number"], ["current_price", "Giá hiện tại", "money"], ["currency", "Tiền tệ"]],
    fields: [["name", "Tên tài sản", "text", true], ["category", "Phân loại", "select", true, "assetCategory"], ["symbol", "Mã / ký hiệu"], ["brand", "Thương hiệu"], ["unit", "Đơn vị", "select", true, "unit", "item"], ["quantity", "Số lượng", "number", true, null, 1], ["average_cost", "Giá vốn bình quân", "number", true, null, 0], ["current_price", "Giá hiện tại", "number", true, null, 0], ["currency", "Tiền tệ", "select", true, "currency", "VND"], ["acquisition_date", "Ngày mua", "date"], ["valuation_source", "Nguồn định giá"], ["target_price", "Giá mục tiêu", "number"], ["note", "Ghi chú", "textarea"]],
  },
  savings_deposits: {
    label: "Tiết kiệm", icon: "◉", title: "Sổ tiết kiệm", eyebrow: "TIỀN GỬI", singular: "sổ tiết kiệm",
    columns: [["name", "Tên sổ"], ["principal", "Tiền gốc", "money"], ["current_interest", "Lãi hiện tại", "money"], ["annual_interest_rate", "Lãi suất/năm", "percent"], ["term_in_days", "Kỳ hạn", "termDays"], ["progress_days", "Tiến độ", "progress"], ["maturity_date", "Ngày đáo hạn", "date"], ["contract_number", "Số tài khoản"]],
    fields: [["name", "Tên sổ", "text", true], ["bank_name", "Ngân hàng", "text", true], ["principal", "Tiền gốc", "number", true], ["current_interest", "Lãi hiện tại", "number"], ["currency", "Tiền tệ", "select", true, "currency", "VND"], ["annual_interest_rate", "Lãi suất năm (%)", "number", true], ["start_date", "Ngày gửi", "date", true], ["maturity_date", "Ngày đáo hạn", "date", true], ["term_in_months", "Kỳ hạn (tháng)", "number", true], ["term_in_days", "Kỳ hạn (ngày)", "number"], ["progress_days", "Tiến độ hiện tại (ngày)", "number"], ["interest_snapshot_date", "Ngày chốt lãi và tiến độ", "date"], ["interest_payment_type", "Trả lãi", "select", true, [["end_of_term", "Cuối kỳ"], ["monthly", "Hàng tháng"], ["upfront", "Trả trước"]], "end_of_term"], ["auto_renewal_type", "Tái tục", "select", false, [["none", "Không tái tục"], ["principal_only", "Chỉ tiền gốc"], ["principal_and_interest", "Gốc và lãi"]], "none"], ["status", "Trạng thái", "select", true, [["active", "Đang hoạt động"], ["matured", "Đã đáo hạn"], ["closed", "Đã đóng"], ["withdrawn_early", "Rút trước hạn"]], "active"], ["contract_number", "Số tài khoản"], ["source_image", "Ảnh nguồn"]],
  },
  liabilities: {
    label: "Nợ phải trả", icon: "▾", title: "Nợ phải trả", eyebrow: "NGHĨA VỤ TÀI CHÍNH", singular: "khoản nợ",
    columns: [["name", "Tên"], ["liability_type", "Loại", "liabilityType"], ["lender", "Bên cho vay"], ["current_balance", "Dư nợ", "money"], ["annual_interest_rate", "Lãi suất", "percent"], ["next_payment_date", "Kỳ trả tới", "date"]],
    fields: [["name", "Tên khoản nợ", "text", true], ["liability_type", "Loại nợ", "select", true, "liabilityType", "other_payable"], ["lender", "Bên cho vay"], ["currency", "Tiền tệ", "select", true, "currency", "VND"], ["original_principal", "Số tiền ban đầu", "number", true], ["current_balance", "Dư nợ hiện tại", "number", true], ["annual_interest_rate", "Lãi suất năm (%)", "number", true, null, 0], ["start_date", "Ngày bắt đầu", "date", true], ["maturity_date", "Ngày kết thúc", "date"], ["next_payment_date", "Ngày trả tiếp theo", "date"], ["monthly_payment", "Số tiền trả hàng tháng", "number"], ["note", "Ghi chú", "textarea"]],
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
    state.records = await api(`/api/data/${pageKey}`);
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
    </section>`;
}

function renderTable() {
  const page = pages[state.page];
  const rows = state.records.map((record) => `<tr>${page.columns.map((column) => `<td>${escapeHtml(formatCell(record, column))}</td>`).join("")}<td><div class="actions"><button data-edit="${record.id}" title="Sửa">✎</button><button class="delete" data-delete="${record.id}" title="Xóa">⌫</button></div></td></tr>`).join("");
  $("#content").innerHTML = `
    <div class="section-header"><div><h3>${state.records.length} ${page.singular}</h3><span class="muted">Dữ liệu đồng bộ với ứng dụng iPhone</span></div><button id="addButton" class="primary-button">+ Thêm ${page.singular}</button></div>
    <div class="table-wrap">${rows ? `<table><thead><tr>${page.columns.map(([, label]) => `<th>${label}</th>`).join("")}<th></th></tr></thead><tbody>${rows}</tbody></table>` : `<div class="empty-state"><strong>Chưa có ${page.singular}</strong><span>Bấm nút thêm để tạo dữ liệu đầu tiên.</span></div>`}</div>`;
}

function fieldOptions(source) {
  return Array.isArray(source) ? source : options[source] || [];
}

function inputValue(record, name, fallback, type) {
  if (!record && type === "date" && name === "start_date" && fallback === undefined) return new Date().toISOString().slice(0, 10);
  const value = record?.[name] ?? fallback ?? "";
  if (type === "datetime-local" && value) return new Date(value).toISOString().slice(0, 16);
  return value;
}

function renderField(field, record) {
  const [name, label, type = "text", required = false, source, fallback] = field;
  const value = inputValue(record, name, fallback, type);
  if (type === "checkbox") return `<label class="checkbox-label"><input name="${name}" type="checkbox" ${value ? "checked" : ""}> ${label}</label>`;
  if (type === "select") return `<label>${label}<select name="${name}" ${required ? "required" : ""}><option value="">— Chọn —</option>${fieldOptions(source).map(([key, text]) => `<option value="${escapeHtml(key)}" ${key === value ? "selected" : ""}>${escapeHtml(text)}</option>`).join("")}</select></label>`;
  if (type === "textarea") return `<label class="full">${label}<textarea name="${name}">${escapeHtml(value)}</textarea></label>`;
  const step = type === "number" ? 'step="any"' : "";
  return `<label>${label}<input name="${name}" type="${type}" value="${escapeHtml(value)}" ${step} ${required ? "required" : ""}></label>`;
}

function openModal(record = null) {
  const page = pages[state.page];
  state.editing = record;
  $("#modalEyebrow").textContent = record ? "CẬP NHẬT" : "THÊM MỚI";
  $("#modalTitle").textContent = record ? `Sửa ${page.singular}` : `Thêm ${page.singular}`;
  $("#dataForm").innerHTML = page.fields.map((field) => renderField(field, record)).join("") + `<p class="form-error full" id="dataError"></p><div class="form-actions"><button type="button" class="secondary-button" data-close>Hủy</button><button type="submit" class="primary-button">${record ? "Lưu thay đổi" : "Thêm mới"}</button></div>`;
  $("#modal").classList.remove("hidden");
}

function closeModal() { $("#modal").classList.add("hidden"); state.editing = null; }

function serializeForm(form) {
  const page = pages[state.page];
  const data = {};
  for (const [name, _label, type = "text"] of page.fields) {
    const input = form.elements[name];
    if (type === "checkbox") data[name] = input.checked;
    else if (input.value !== "") data[name] = type === "number" ? Number(input.value) : type === "datetime-local" ? new Date(input.value).toISOString() : input.value;
    else if (state.editing) data[name] = null;
  }
  return data;
}

async function saveRecord(event) {
  event.preventDefault();
  const button = event.target.querySelector('[type="submit"]');
  button.disabled = true;
  $("#dataError").textContent = "";
  try {
    const wasEditing = Boolean(state.editing);
    const path = state.editing ? `/api/data/${state.page}/${state.editing.id}` : `/api/data/${state.page}`;
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
    await api(`/api/data/${state.page}/${id}`, { method: "DELETE" });
    toast("Đã xóa dữ liệu.");
    await navigate(state.page);
  } catch (error) { toast(error.message, true); }
}

function renderError(error) {
  $("#content").innerHTML = `<div class="empty-state"><strong>Không tải được dữ liệu</strong><span>${escapeHtml(error.message)}</span><br><br><button class="secondary-button" data-retry>Thử lại</button></div>`;
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
  if (event.target.closest("[data-retry]")) navigate(state.page);
});

$("#today").textContent = new Intl.DateTimeFormat("vi-VN", { weekday: "long", day: "2-digit", month: "2-digit", year: "numeric" }).format(new Date());
api("/api/session").then((session) => showApp(session.username)).catch(showLogin);
