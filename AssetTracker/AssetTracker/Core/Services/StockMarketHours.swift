import Foundation

enum StockMarketHours {
  static func isOpen(at date: Date = .now, calendar: Calendar = vietnamCalendar) -> Bool {
    let weekday = calendar.component(.weekday, from: date)
    guard weekday != 1 && weekday != 7 else { return false }
    let hour = calendar.component(.hour, from: date)
    let minute = calendar.component(.minute, from: date)
    let value = hour * 60 + minute
    return (value >= 540 && value <= 690) || (value >= 780 && value <= 900)
  }
  private static var vietnamCalendar: Calendar {
    var value = Calendar(identifier: .gregorian)
    value.timeZone = TimeZone(identifier: "Asia/Ho_Chi_Minh")!
    return value
  }
}
