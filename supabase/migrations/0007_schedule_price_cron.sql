-- Lên lịch tự động lấy giá qua pg_cron + pg_net.
-- Hai function giữ verify_jwt = true; cron gắn bearer token là anon key,
-- lấy từ Vault (secret 'cron_anon_key') nên file migration không chứa key.
create extension if not exists pg_cron;
create extension if not exists pg_net;

-- Vàng: vang.today làm mới ~5 phút; kéo mỗi 30 phút, cả ngày.
select cron.schedule(
  'fetch-gold-price',
  '*/30 * * * *',
  $$select net.http_post(
      url := 'https://hiekanuqptblnuficpra.supabase.co/functions/v1/fetch-gold-price',
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'Authorization', 'Bearer ' ||
          (select decrypted_secret from vault.decrypted_secrets where name = 'cron_anon_key')
      ),
      body := '{}'::jsonb
  );$$
);

-- Chứng khoán: mỗi 10 phút; function tự trả về sớm ngoài giờ HOSE/HNX/UPCOM.
select cron.schedule(
  'fetch-stock-price',
  '*/10 * * * *',
  $$select net.http_post(
      url := 'https://hiekanuqptblnuficpra.supabase.co/functions/v1/fetch-stock-price',
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'Authorization', 'Bearer ' ||
          (select decrypted_secret from vault.decrypted_secrets where name = 'cron_anon_key')
      ),
      body := '{}'::jsonb
  );$$
);
