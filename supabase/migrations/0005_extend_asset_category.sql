alter table public.assets drop constraint assets_category_check;
alter table public.assets add constraint assets_category_check check (category in (
    'stock','fund_certificate','etf','listed_bond','warrant','foreign_stock','open_end_fund','other_security',
    'gold_bar_sjc','gold_ring_9999','gold_bar_other_brand','gold_jewelry','gold_24k','gold_18k','gold_14k','gold_international','other_gold',
    'real_estate','car','motorbike','non_listed_bond','crypto','insurance_cash_value','loan_receivable','business_equity',
    'collectible','digital_asset','rental_asset'
));
alter table public.assets add column valuation_source text;
alter table public.assets add column generated_income numeric;
alter table public.assets add column related_cost numeric;
alter table public.assets drop constraint assets_unit_check;
alter table public.assets add constraint assets_unit_check check (unit in ('share','luong','cay','chi','phan','gram','ounce','item'));
