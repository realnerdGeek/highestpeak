-- HighestPeak sync setup: one table for your library, and one private folder of files per account.
create table if not exists public.docs (
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  coll text not null check (coll in ('tracks', 'playlists', 'settings')),
  id text not null,
  data jsonb,
  m bigint not null default 0,
  deleted boolean not null default false,
  updated_at timestamptz not null default now(),
  primary key (user_id, coll, id)
);
create index if not exists docs_user_updated on public.docs (user_id, updated_at);
alter table public.docs enable row level security;
drop policy if exists "own docs" on public.docs;
create policy "own docs" on public.docs for all to authenticated
  using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));
grant usage on schema public to authenticated;
grant select, insert, update, delete on public.docs to authenticated;

create or replace function public.docs_touch() returns trigger language plpgsql set search_path = '' as $$
begin new.updated_at := now(); return new; end $$;
drop trigger if exists docs_touch on public.docs;
create trigger docs_touch before insert or update on public.docs for each row execute function public.docs_touch();

insert into storage.buckets (id, name, public, file_size_limit)
values ('media', 'media', false, 52428800)
on conflict (id) do update set public = false, file_size_limit = 52428800;

drop policy if exists "hp own files read" on storage.objects;
drop policy if exists "hp own files add" on storage.objects;
drop policy if exists "hp own files change" on storage.objects;
drop policy if exists "hp own files remove" on storage.objects;
create policy "hp own files read" on storage.objects for select to authenticated
  using (bucket_id = 'media' and (storage.foldername(name))[1] = (select auth.uid())::text);
create policy "hp own files add" on storage.objects for insert to authenticated
  with check (bucket_id = 'media' and (storage.foldername(name))[1] = (select auth.uid())::text);
create policy "hp own files change" on storage.objects for update to authenticated
  using (bucket_id = 'media' and (storage.foldername(name))[1] = (select auth.uid())::text);
create policy "hp own files remove" on storage.objects for delete to authenticated
  using (bucket_id = 'media' and (storage.foldername(name))[1] = (select auth.uid())::text);
