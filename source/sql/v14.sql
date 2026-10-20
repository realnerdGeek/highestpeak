-- EarWorm V14 setup: an anonymous weekly count of devices, and feedback. Anyone can add a row; nobody can read them
-- through the app (only the project owner, in the Supabase dashboard). This adds to the earlier setup code.

-- one row per device per week: a random id the app made, the week, the version, phone or computer. Nothing else.
create table if not exists public.pings (
  device text not null check (device ~ '^[A-Za-z0-9]{8,64}$'),
  week text not null check (week ~ '^\d{4}-W\d{2}$'),
  version text not null check (char_length(version) <= 16),
  kind text not null check (kind in ('phone', 'computer')),
  created_at timestamptz not null default now(),
  primary key (device, week)
);
alter table public.pings enable row level security;
drop policy if exists "anyone can add a ping" on public.pings;
create policy "anyone can add a ping" on public.pings for insert to anon, authenticated with check (true);
revoke all on public.pings from anon, authenticated;
grant insert on public.pings to anon, authenticated;

-- feedback from the app: the message, and an email only if they want a reply
create table if not exists public.feedback (
  id bigint generated always as identity primary key,
  message text not null check (char_length(message) between 1 and 2000),
  email text check (email is null or (char_length(email) <= 200 and email ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$')),
  version text check (version is null or char_length(version) <= 16),
  kind text check (kind is null or kind in ('phone', 'computer')),
  created_at timestamptz not null default now()
);
alter table public.feedback enable row level security;
drop policy if exists "anyone can send feedback" on public.feedback;
create policy "anyone can send feedback" on public.feedback for insert to anon, authenticated with check (true);
revoke all on public.feedback from anon, authenticated;
grant insert on public.feedback to anon, authenticated;

-- quiet a warning: Supabase's own "turn on row level security for new tables" helper is an event trigger,
-- so nobody ever needs to call it through the API
do $$ begin
  if exists (select 1 from pg_proc p join pg_namespace n on n.oid = p.pronamespace where n.nspname = 'public' and p.proname = 'rls_auto_enable') then
    revoke execute on function public.rls_auto_enable() from public, anon, authenticated;
  end if;
end $$;
