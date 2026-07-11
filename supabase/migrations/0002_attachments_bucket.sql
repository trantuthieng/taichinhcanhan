insert into storage.buckets (id, name, public)
values ('attachments', 'attachments', false)
on conflict (id) do nothing;

create policy "allow anon attachments select" on storage.objects for select to anon
using (bucket_id = 'attachments');
create policy "allow anon attachments insert" on storage.objects for insert to anon
with check (bucket_id = 'attachments');
create policy "allow anon attachments update" on storage.objects for update to anon
using (bucket_id = 'attachments') with check (bucket_id = 'attachments');
create policy "allow anon attachments delete" on storage.objects for delete to anon
using (bucket_id = 'attachments');
