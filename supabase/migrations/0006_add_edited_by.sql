alter table public.asset_transactions add column edited_by text;
alter table public.asset_accounts add column edited_by text;
alter table public.savings_deposits add column edited_by text;
alter table public.liabilities add column edited_by text;
