-- Bổ sung dữ liệu chi tiết và thay bản ghi tổng hợp bằng 30 khoản tiết kiệm từ ảnh.
alter table public.savings_deposits
  add column if not exists current_interest numeric,
  add column if not exists progress_days integer,
  add column if not exists term_in_days integer,
  add column if not exists interest_snapshot_date date,
  add column if not exists source_image text;

delete from public.savings_deposits
where id = '00000000-0000-4000-8000-000000000401'
   or name = 'Tiết kiệm tổng hợp (đã trừ 50 triệu)';

with input(row_no, source_image, position, principal, current_interest, maturity_date, progress_days, term_in_days, contract_number) as (
  values
    ( 1, 'image.png',    'Trên',  5000000::numeric,  44075::numeric, '2026-12-04'::date,  39, 183, '607241671455'),
    ( 2, 'image.png',    'Dưới', 10000000::numeric, 428671::numeric, '2026-12-24'::date,  19, 183, null),
    ( 3, 'image_2.png',  'Trên', 10000000::numeric, 428671::numeric, '2026-12-25'::date,  18, 183, 'LD2617653842'),
    ( 4, 'image_2.png',  'Dưới', 10000000::numeric, 428671::numeric, '2026-12-25'::date,  18, 183, null),
    ( 5, 'image_3.png',  'Trên',  5000000::numeric, 226815::numeric, '2027-01-11'::date,   3, 185, 'LD2619119516'),
    ( 6, 'image_3.png',  'Dưới',  5000000::numeric, 226815::numeric, '2027-01-11'::date,   3, 185, null),
    ( 7, 'image_4.png',  'Trên', 21000000::numeric, 334274::numeric, '2026-11-04'::date,  70, 184, '608923990176'),
    ( 8, 'image_4.png',  'Dưới',  4000000::numeric,  61852::numeric, '2026-11-06'::date,  68, 184, null),
    ( 9, 'image_5.png',  'Trên',  5000000::numeric,  86411::numeric, '2026-10-28'::date,  76, 183, '601124002234'),
    (10, 'image_5.png',  'Dưới',  4000000::numeric,  69129::numeric, '2026-10-28'::date,  76, 183, null),
    (11, 'image_6.png',  'Trên', 10000000::numeric, 428671::numeric, '2026-12-25'::date,  18, 183, 'LD2617641099'),
    (12, 'image_6.png',  'Dưới', 11300000::numeric, 484398::numeric, '2026-12-25'::date,  18, 183, null),
    (13, 'image_7.png',  'Trên',  5000000::numeric,  75041::numeric, '2026-11-09'::date,  66, 185, '602146549853'),
    (14, 'image_7.png',  'Dưới',  5329000::numeric,  77263::numeric, '2026-11-11'::date,  63, 184, null),
    (15, 'image_8.png',  'Trên',  7000000::numeric, 315825::numeric, '2027-01-09'::date,   4, 184, 'LD2619000045'),
    (16, 'image_8.png',  'Dưới', 10000000::numeric, 453630::numeric, '2027-01-11'::date,   3, 185, null),
    (17, 'image_9.png',  'Trên',  5000000::numeric,  75041::numeric, '2026-11-09'::date,  66, 185, '600512029849'),
    (18, 'image_9.png',  'Dưới',  5000000::numeric,  75041::numeric, '2026-11-09'::date,  66, 185, null),
    (19, 'image_10.png', 'Trên',  5173000::numeric,  63096::numeric, '2026-11-21'::date,  53, 184, '601840433394'),
    (20, 'image_10.png', 'Dưới',  5178000::numeric,  47985::numeric, '2026-12-02'::date,  41, 183, null),
    (21, 'image_11.png', 'Trên',  5000000::numeric, 114411::numeric, '2026-10-08'::date,  96, 183, '600745070528'),
    (22, 'image_11.png', 'Dưới',  2000000::numeric,  42751::numeric, '2026-10-10'::date,  94, 183, null),
    (23, 'image_12.png', 'Trên', 10000000::numeric, 354411::numeric, '2026-07-27'::date, 168, 182, '609091195601'),
    (24, 'image_12.png', 'Dưới',  5000000::numeric, 120370::numeric, '2026-10-03'::date, 101, 183, null),
    (25, 'image_13.png', 'Trên',  5000000::numeric, 177205::numeric, '2026-07-27'::date, 168, 182, '604049032288'),
    (26, 'image_13.png', 'Dưới', 10000000::numeric, 354411::numeric, '2026-07-27'::date, 168, 182, null),
    (27, 'image_14.png', 'Trên', 10000000::numeric, 354411::numeric, '2026-07-27'::date, 168, 182, '602315072492'),
    (28, 'image_14.png', 'Dưới',  5000000::numeric, 177205::numeric, '2026-07-27'::date, 168, 182, null),
    (29, 'image_15.png', 'Trên', 10000000::numeric, 354411::numeric, '2026-07-27'::date, 168, 182, '601561726586'),
    (30, 'image_15.png', 'Dưới', 10000000::numeric, 354411::numeric, '2026-07-27'::date, 168, 182, null)
), normalized as (
  select
    ('10000000-0000-4000-8000-' || lpad(row_no::text, 12, '0'))::uuid as id,
    case when contract_number is not null then 'Tiết kiệm ' || contract_number
         else 'Tiết kiệm ' || replace(source_image, '.png', '') || ' - ' || lower(position) end as name,
    'Tổng hợp từ ảnh'::text as bank_name,
    principal,
    round(current_interest / principal * 365 / term_in_days * 100, 3) as annual_interest_rate,
    maturity_date - term_in_days as start_date,
    maturity_date,
    current_interest,
    progress_days,
    term_in_days,
    contract_number,
    source_image
  from input
)
insert into public.savings_deposits (
  id, name, bank_name, principal, currency, annual_interest_rate,
  start_date, maturity_date, term_in_months, interest_payment_type,
  auto_renewal_type, status, contract_number, current_interest,
  progress_days, term_in_days, interest_snapshot_date, source_image,
  edited_by, created_at, updated_at
)
select
  id, name, bank_name, principal, 'VND', annual_interest_rate,
  start_date, maturity_date, 6, 'end_of_term', 'none', 'active', contract_number,
  current_interest, progress_days, term_in_days, '2026-07-13'::date, source_image,
  'admin', now(), now()
from normalized
on conflict (id) do update set
  name = excluded.name,
  bank_name = excluded.bank_name,
  principal = excluded.principal,
  annual_interest_rate = excluded.annual_interest_rate,
  start_date = excluded.start_date,
  maturity_date = excluded.maturity_date,
  term_in_months = excluded.term_in_months,
  contract_number = excluded.contract_number,
  current_interest = excluded.current_interest,
  progress_days = excluded.progress_days,
  term_in_days = excluded.term_in_days,
  interest_snapshot_date = excluded.interest_snapshot_date,
  source_image = excluded.source_image,
  edited_by = excluded.edited_by,
  updated_at = now();
