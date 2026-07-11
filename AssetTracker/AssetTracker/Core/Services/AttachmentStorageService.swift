import Foundation
import Supabase

struct AttachmentStorageService {
  func upload(_ data: Data, fileExtension: String = "jpg") async throws -> String {
    let path = "invoices/\(UUID().uuidString).\(fileExtension)"
    try await SupabaseClientProvider.shared.storage.from("attachments")
      .upload(path, data: data, options: FileOptions(contentType: "image/\(fileExtension)"))
    return path
  }
}
