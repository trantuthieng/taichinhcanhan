-- Sprint 1.1: initial no-auth asset-tracking schema.
create table public.asset_accounts (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    institution text,
    account_type text not null check (account_type in (
        'cash_personal','cash_family','bank_account','salary_account',
        'spending_account','e_wallet','emergency_fund','travel_fund',
        'investment_fund','foreign_currency_cash'
    )),
    currency text not null default 'VND',
    balance numeric not null default 0,
    exchange_rate_at_opening numeric,
    current_exchange_rate numeric,
    is_included_in_net_worth boolean not null default true,
    target_group text,
    note text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table public.assets (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    category text not null check (category in (
        'stock','fund_certificate','etf','listed_bond','warrant',
        'foreign_stock','open_end_fund','other_security',
        'gold_bar_sjc','gold_ring_9999','gold_bar_other_brand','gold_jewelry',
        'gold_24k','gold_18k','gold_14k','gold_international','other_gold'
    )),
    account_id uuid references public.asset_accounts(id),
    symbol text,
    brand text,
    unit text not null check (unit in ('share','luong','cay','chi','phan','gram','ounce')),
    quantity numeric not null default 0,
    average_cost numeric not null default 0,
    current_price numeric not null default 0,
    currency text not null default 'VND',
    acquisition_date date,
    valuation_date timestamptz not null default now(),
    purchase_location text,
    storage_location text,
    invoice_number text,
    invoice_attachment_url text,
    gross_weight numeric,
    pure_gold_weight numeric,
    gold_purity numeric,
    labor_cost numeric,
    gemstone_value numeric,
    depreciation_rate numeric,
    expected_buyback_price numeric,
    note text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table public.asset_transactions (
    id uuid primary key default gen_random_uuid(),
    asset_id uuid references public.assets(id),
    type text not null check (type in (
        'deposit','withdrawal','transfer','buy','sell','interest',
        'dividend','maturity','repayment','fee','tax','adjustment'
    )),
    date timestamptz not null,
    quantity numeric,
    unit_price numeric,
    amount numeric not null,
    fee numeric not null default 0,
    tax numeric not null default 0,
    source_account_id uuid references public.asset_accounts(id),
    destination_account_id uuid references public.asset_accounts(id),
    note text,
    attachment_url text,
    created_at timestamptz not null default now()
);

create table public.savings_deposits (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    bank_name text not null,
    principal numeric not null,
    currency text not null default 'VND',
    annual_interest_rate numeric not null,
    start_date date not null,
    maturity_date date not null,
    term_in_months int not null,
    interest_payment_type text not null check (interest_payment_type in ('end_of_term','monthly','upfront')),
    auto_renewal_type text check (auto_renewal_type in ('none','principal_only','principal_and_interest')),
    early_withdrawal_rate numeric,
    status text not null default 'active' check (status in ('active','matured','closed','withdrawn_early')),
    contract_number text,
    attachment_url text,
    account_id uuid references public.asset_accounts(id),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table public.liabilities (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    lender text,
    original_principal numeric not null,
    current_balance numeric not null,
    annual_interest_rate numeric not null,
    start_date date not null,
    maturity_date date,
    payment_frequency text check (payment_frequency in ('monthly','quarterly','semi_annual','annual','one_time')),
    next_payment_date date,
    monthly_payment numeric,
    collateral text,
    note text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table public.valuation_snapshots (
    id uuid primary key default gen_random_uuid(),
    date date not null unique,
    total_assets numeric not null,
    total_liabilities numeric not null,
    net_worth numeric not null,
    cash_value numeric not null,
    stock_value numeric not null,
    gold_value numeric not null,
    savings_value numeric not null,
    other_asset_value numeric not null default 0,
    fx_rates_snapshot jsonb,
    created_at timestamptz not null default now()
);

do $$
declare t text;
begin
  for t in select unnest(array[
    'asset_accounts','assets','asset_transactions',
    'savings_deposits','liabilities','valuation_snapshots'
  ])
  loop
    execute format('alter table public.%I enable row level security;', t);
    execute format('create policy "allow anon all" on public.%I for all to anon using (true) with check (true);', t);
  end loop;
end $$;
