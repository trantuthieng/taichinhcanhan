import {
  createClient,
  type SupabaseClient,
} from "https://esm.sh/@supabase/supabase-js@2";

type SupabaseAdmin = SupabaseClient<any>;

let client: SupabaseAdmin | undefined;

export function getSupabaseAdmin(): SupabaseAdmin {
  if (client) return client;

  const url = Deno.env.get("SUPABASE_URL");
  const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !serviceRoleKey) {
    throw new Error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY");
  }

  client = createClient<any>(url, serviceRoleKey, {
    auth: { persistSession: false },
  });
  return client;
}
