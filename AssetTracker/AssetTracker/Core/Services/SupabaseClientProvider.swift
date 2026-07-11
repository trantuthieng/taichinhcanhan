import Foundation
import Supabase

enum SupabaseClientProvider {
  static let shared = SupabaseClient(
    supabaseURL: URL(string: Secrets.supabaseURL)!,
    supabaseKey: Secrets.supabaseAnonKey
  )
}
