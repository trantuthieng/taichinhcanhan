-- Mở rộng bảng liabilities theo note.txt mục 5: 3 cơ chế nợ (vay kỳ hạn / thẻ tín dụng / khoản phải trả khác).
alter table public.liabilities
    add column if not exists liability_type text not null default 'other_payable' check (liability_type in (
        'mortgage_loan','car_loan','consumer_loan','unsecured_loan',
        'family_loan','installment_plan','credit_card','other_payable'
    )),
    add column if not exists currency text not null default 'VND',
    add column if not exists interest_rate_type text check (interest_rate_type in ('fixed','floating')),
    add column if not exists fixed_rate_end_date date,
    add column if not exists repayment_method text check (repayment_method in ('equal_principal','annuity')),
    add column if not exists term_in_months int,
    add column if not exists early_repayment_fee_rate numeric,
    add column if not exists grace_period_months int,
    add column if not exists credit_limit numeric,
    add column if not exists statement_day int check (statement_day between 1 and 31),
    add column if not exists payment_due_day int check (payment_due_day between 1 and 31),
    add column if not exists interest_free_days int,
    add column if not exists min_payment_rate numeric,
    add column if not exists min_payment_fixed_amount numeric,
    add column if not exists annual_fee numeric,
    add column if not exists late_fee numeric,
    add column if not exists last_statement_balance numeric,
    add column if not exists last_statement_date date;

-- Giao dịch repayment gắn với 1 khoản nợ (song song asset_id cho tài sản); mỗi giao dịch chỉ nên gắn 1 trong 2.
alter table public.asset_transactions
    add column if not exists liability_id uuid references public.liabilities(id),
    add column if not exists payment_type text check (payment_type in ('full','minimum','partial'));
