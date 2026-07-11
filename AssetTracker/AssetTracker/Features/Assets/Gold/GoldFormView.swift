import PhotosUI
import SwiftUI

struct GoldFormView: View {
  @Environment(\.dismiss) private var dismiss
  let asset: Asset?
  let onSave: (Asset, Bool) async -> Bool
  @State private var name = ""
  @State private var category = AssetCategory.goldBarSJC
  @State private var brand = ""
  @State private var quantity: Decimal = 0
  @State private var unit = AssetUnit.luong
  @State private var price: Decimal = 0
  @State private var currentPrice: Decimal = 0
  @State private var date = Date()
  @State private var purchaseLocation = ""
  @State private var storageLocation = ""
  @State private var grossWeight: Decimal = 0
  @State private var pureWeight: Decimal = 0
  @State private var purity: Decimal = 0
  @State private var laborCost: Decimal = 0
  @State private var gemstoneValue: Decimal = 0
  @State private var photo: PhotosPickerItem?
  @State private var attachmentPath: String?
  @State private var targetPrice: Decimal = 0
  var body: some View {
    NavigationStack {
      Form {
        Picker("Loại vàng", selection: $category) {
          ForEach(GoldViewModel.categories, id: \.self) { Text($0.rawValue).tag($0) }
        }
        TextField("Tên khoản mục", text: $name)
        TextField("Thương hiệu", text: $brand)
        TextField("Số lượng", value: $quantity, format: .number).keyboardType(.decimalPad)
        Picker("Đơn vị", selection: $unit) {
          ForEach(AssetUnit.allCases.filter { $0 != .share }, id: \.self) {
            Text($0.rawValue).tag($0)
          }
        }
        TextField("Giá mua/đơn vị", value: $price, format: .number).keyboardType(.decimalPad)
        TextField("Giá hiện tại", value: $currentPrice, format: .number).keyboardType(.decimalPad)
        TextField("Giá mục tiêu (tùy chọn)", value: $targetPrice, format: .number).keyboardType(
          .decimalPad)
        DatePicker("Ngày mua", selection: $date, displayedComponents: .date)
        TextField("Nơi mua", text: $purchaseLocation)
        TextField("Nơi lưu giữ", text: $storageLocation)
        if category == .goldJewelry {
          Section("Trang sức") {
            TextField("Trọng lượng tổng", value: $grossWeight, format: .number)
            TextField("Trọng lượng vàng thực", value: $pureWeight, format: .number)
            TextField("Tuổi vàng (%)", value: $purity, format: .number)
            TextField("Tiền công", value: $laborCost, format: .number)
            TextField("Giá trị đá quý", value: $gemstoneValue, format: .number)
          }
        }
        PhotosPicker(selection: $photo, matching: .images) {
          Label(
            attachmentPath == nil ? "Chọn hóa đơn" : "Đã chọn hóa đơn", systemImage: "paperclip")
        }
      }.navigationTitle(asset == nil ? "Thêm vàng" : "Sửa vàng").toolbar {
        ToolbarItem(placement: .cancellationAction) { Button("Hủy") { dismiss() } }
        ToolbarItem(placement: .confirmationAction) {
          Button("Lưu") { Task { await save() } }.disabled(quantity <= 0)
        }
      }.onAppear { prefill() }
    }
  }
  private func prefill() {
    guard let a = asset else { return }
    name = a.name
    category = a.category
    brand = a.brand ?? ""
    quantity = a.quantity
    unit = a.unit
    price = a.averageCost
    currentPrice = a.currentPrice
    targetPrice = a.targetPrice ?? 0
    date = a.acquisitionDate ?? .now
    purchaseLocation = a.purchaseLocation ?? ""
    storageLocation = a.storageLocation ?? ""
    grossWeight = a.grossWeight ?? 0
    pureWeight = a.pureGoldWeight ?? 0
    purity = a.goldPurity ?? 0
    laborCost = a.laborCost ?? 0
    gemstoneValue = a.gemstoneValue ?? 0
    attachmentPath = a.invoiceAttachmentURL
  }
  private func save() async {
    if let photo, let data = try? await photo.loadTransferable(type: Data.self) {
      attachmentPath = try? await AttachmentStorageService().upload(data)
    }
    let now = Date()
    let a = Asset(
      id: asset?.id ?? UUID(), name: name.nilIfEmpty ?? category.rawValue, category: category,
      accountID: nil, symbol: nil, brand: brand.nilIfEmpty, unit: unit, quantity: quantity,
      averageCost: price, currentPrice: currentPrice, currency: .vnd, acquisitionDate: date,
      valuationDate: now, purchaseLocation: purchaseLocation.nilIfEmpty,
      storageLocation: storageLocation.nilIfEmpty, invoiceNumber: nil,
      invoiceAttachmentURL: attachmentPath,
      grossWeight: category == .goldJewelry ? grossWeight : nil,
      pureGoldWeight: category == .goldJewelry ? pureWeight : nil,
      goldPurity: category == .goldJewelry ? purity : nil,
      laborCost: category == .goldJewelry ? laborCost : nil,
      gemstoneValue: category == .goldJewelry ? gemstoneValue : nil, depreciationRate: nil,
      expectedBuybackPrice: nil, note: nil, targetPrice: targetPrice > 0 ? targetPrice : nil,
      createdAt: asset?.createdAt ?? now, updatedAt: now)
    if await onSave(a, asset == nil) { dismiss() }
  }
}
