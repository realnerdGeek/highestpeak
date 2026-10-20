-- HighestPeak V12 setup: usernames, deleting your account, and two-step sign-in.
-- This adds to the first setup code. Do not delete or change that one.

create table if not exists public.profiles (
  user_id uuid primary key default auth.uid() references auth.users (id) on delete cascade,
  username text not null check (username ~ '^[a-z0-9._]{3,20}$'),
  created_at timestamptz not null default now()
);
create unique index if not exists profiles_username_key on public.profiles (username);
alter table public.profiles enable row level security;
drop policy if exists "own profile" on public.profiles;
create policy "own profile" on public.profiles for all to authenticated
  using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));
grant select, insert, update, delete on public.profiles to authenticated;

-- lets the app check if a username is free, without showing anyone else's account
create or replace function public.username_taken(name text) returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.profiles p where p.username = lower(name) and p.user_id <> (select auth.uid()));
$$;
revoke all on function public.username_taken(text) from public, anon;
grant execute on function public.username_taken(text) to authenticated;

-- deletes the signed-in account (its library records and username go with it); with two-step sign-in on, only after the code
create or replace function public.delete_my_account() returns void
language plpgsql security definer set search_path = '' as $$
begin
  if (select auth.uid()) is null then raise exception 'not signed in'; end if;
  if exists (select 1 from auth.mfa_factors f where f.user_id = (select auth.uid()) and f.status = 'verified')
     and coalesce((select auth.jwt()->>'aal'), '') <> 'aal2' then raise exception 'two-step code needed'; end if;
  delete from auth.users where id = (select auth.uid());
end $$;
revoke all on function public.delete_my_account() from public, anon;
grant execute on function public.delete_my_account() to authenticated;

-- two-step sign-in: once an account turns it on, its library only opens after the code
drop policy if exists "two-step when on" on public.docs;
create policy "two-step when on" on public.docs as restrictive to authenticated
  using (array[(select auth.jwt()->>'aal')] <@ (select case when count(f.id) > 0 then array['aal2'] else array['aal1', 'aal2'] end from auth.mfa_factors f where f.user_id = (select auth.uid()) and f.status = 'verified'))
  with check (array[(select auth.jwt()->>'aal')] <@ (select case when count(f.id) > 0 then array['aal2'] else array['aal1', 'aal2'] end from auth.mfa_factors f where f.user_id = (select auth.uid()) and f.status = 'verified'));
drop policy if exists "two-step when on" on public.profiles;
create policy "two-step when on" on public.profiles as restrictive to authenticated
  using (array[(select auth.jwt()->>'aal')] <@ (select case when count(f.id) > 0 then array['aal2'] else array['aal1', 'aal2'] end from auth.mfa_factors f where f.user_id = (select auth.uid()) and f.status = 'verified'))
  with check (array[(select auth.jwt()->>'aal')] <@ (select case when count(f.id) > 0 then array['aal2'] else array['aal1', 'aal2'] end from auth.mfa_factors f where f.user_id = (select auth.uid()) and f.status = 'verified'));
drop policy if exists "hp two-step when on" on storage.objects;
create policy "hp two-step when on" on storage.objects as restrictive to authenticated
  using (bucket_id <> 'media' or array[(select auth.jwt()->>'aal')] <@ (select case when count(f.id) > 0 then array['aal2'] else array['aal1', 'aal2'] end from auth.mfa_factors f where f.user_id = (select auth.uid()) and f.status = 'verified'))
  with check (bucket_id <> 'media' or array[(select auth.jwt()->>'aal')] <@ (select case when count(f.id) > 0 then array['aal2'] else array['aal1', 'aal2'] end from auth.mfa_factors f where f.user_id = (select auth.uid()) and f.status = 'verified'));
