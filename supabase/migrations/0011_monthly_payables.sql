-- Các khoản phải trả định kỳ phục vụ theo dõi dòng tiền hàng tháng trên webapp.
create table if not exists public.monthly_payables (
  id uuid primary key default gen_random_uuid(),
  name text not null check (length(trim(name)) > 0),
  category text not null default 'other' check (category in (
    'loan_interest','loan_payment','rent','credit_card','utilities',
    'insurance','tax','family','subscription','other'
  )),
  monthly_amount numeric not null check (monthly_amount > 0),
  currency text not null default 'VND',
  due_day integer not null default 1 check (due_day between 1 and 31),
  start_date date not null default current_date,
  end_date date,
  is_active boolean not null default true,
  is_auto_pay boolean not null default false,
  liability_id uuid references public.liabilities(id) on delete set null,
  note text,
  edited_by text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint monthly_payables_dates_valid check (end_date is null or end_date >= start_date)
);

create index if not exists idx_monthly_payables_active_due
  on public.monthly_payables (is_active, due_day);

alter table public.monthly_payables enable row level security;
drop policy if exists "monthly_payables_anon_all" on public.monthly_payables;
create policy "monthly_payables_anon_all" on public.monthly_payables
  for all to anon using (true) with check (true);
