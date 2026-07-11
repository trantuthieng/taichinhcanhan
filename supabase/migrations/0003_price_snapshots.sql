create table public.price_snapshots (
    id uuid primary key default gen_random_uuid(),
    asset_key text not null,
    asset_type text not null check (asset_type in ('gold','stock')),
    buy_price numeric,
    sell_price numeric,
    source text not null,
    fetched_at timestamptz not null,
    created_at timestamptz not null default now()
);
create index idx_price_snapshots_lookup on public.price_snapshots (asset_type, asset_key, fetched_at desc);
alter table public.price_snapshots enable row level security;
create policy "allow anon read" on public.price_snapshots for select to anon using (true);
