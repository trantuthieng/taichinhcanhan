import SwiftUI

struct OtherAssetFormView: View {
  @Environment(\.dismiss) private var dismiss
  let asset: Asset?
  let onSave: (Asset, Bool) async -> Bool
  @State private var name = ""
  @State private var category = AssetCategory.realEstate
  @State private var purchaseDate = Date()
  @State private var purchasePrice: Decimal = 0
  @State private var currentValue: Decimal = 0
  @State private var valuationSource = ""
  @State private var income: Decimal = 0
  @State private var cost: Decimal = 0
  @State private var storage = ""
  @State private var attachment = ""
  @State private var note = ""
  var body: some View {
    NavigationStack {
      Form {
        TextField("Tên tài sản", text: $name)
        Picker("Loại", selection: $category) {
          ForEach(OtherAssetViewModel.categories, id: \.self) { Text($0.rawValue).tag($0) }
        }
        DatePicker("Ngày mua", selection: $purchaseDate, displayedComponents: .date)
        TextField("Giá mua", value: $purchasePrice, format: .number).keyboardType(.decimalPad)
        TextField("Giá trị hiện tại", value: $currentValue, format: .number).keyboardType(
          .decimalPad)
        TextField("Nguồn định giá", text: $valuationSource)
        TextField("Thu nhập tạo ra", value: $income, format: .number).keyboardType(.decimalPad)
        TextField("Chi phí liên quan", value: $cost, format: .number).keyboardType(.decimalPad)
        TextField("Nơi lưu giữ", text: $storage)
        TextField("Đường dẫn tài liệu", text: $attachment)
        TextField("Ghi chú", text: $note, axis: .vertical)
      }.navigationTitle(asset == nil ? "Thêm tài sản khác" : "Sửa tài sản khác").toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }.disabled(name.isEmpty || currentValue < 0)
        }
      }.onAppear { prefill() }
    }
  }
  private func prefill() {
    guard let a = asset else { return }
    name = a.name
    category = a.category
    purchaseDate = a.acquisitionDate ?? .now
    purchasePrice = a.averageCost
    currentValue = a.currentPrice
    valuationSource = a.valuationSource ?? ""
    income = a.generatedIncome ?? 0
    cost = a.relatedCost ?? 0
    storage = a.storageLocation ?? ""
    attachment = a.invoiceAttachmentURL ?? ""
    note = a.note ?? ""
  }
  private func save() async {
    let now = Date()
    let a = Asset(
      id: asset?.id ?? UUID(), name: name, category: category, accountID: nil, symbol: nil,
      brand: nil, unit: .item, quantity: 1, averageCost: purchasePrice, currentPrice: currentValue,
      currency: .vnd, acquisitionDate: purchaseDate, valuationDate: now, purchaseLocation: nil,
      storageLocation: storage.nilIfEmpty, invoiceNumber: nil,
      invoiceAttachmentURL: attachment.nilIfEmpty, grossWeight: nil, pureGoldWeight: nil,
      goldPurity: nil, laborCost: nil, gemstoneValue: nil, depreciationRate: nil,
      expectedBuybackPrice: nil, note: note.nilIfEmpty, targetPrice: nil,
      valuationSource: valuationSource.nilIfEmpty, generatedIncome: income, relatedCost: cost,
      createdAt: asset?.createdAt ?? now, updatedAt: now)
    if await onSave(a, asset == nil) { dismiss() }
  }
}
