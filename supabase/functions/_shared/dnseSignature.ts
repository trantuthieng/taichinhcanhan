export async function signDnseRequest(method: string, path: string) {
  const apiKey = Deno.env.get("DNSE_API_KEY");
  const apiSecret = Deno.env.get("DNSE_API_SECRET");
  if (!apiKey || !apiSecret) {
    throw new Error("Missing DNSE_API_KEY or DNSE_API_SECRET");
  }
  const date = new Date().toUTCString();
  const nonce = crypto.randomUUID().replaceAll("-", "");
  const signingString =
    `(request-target): ${method.toLowerCase()} ${path}\ndate: ${date}\nnonce: ${nonce}`;
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(apiSecret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign(
    "HMAC",
    key,
    new TextEncoder().encode(signingString),
  );
  const base64 = btoa(String.fromCharCode(...new Uint8Array(signature)));
  const header =
    `Signature keyId="${apiKey}",algorithm="hmac-sha256",headers="(request-target) date",signature="${
      encodeURIComponent(base64)
    }",nonce="${nonce}"`;
  return { "X-Api-Key": apiKey, "X-Signature": header, Date: date };
}
