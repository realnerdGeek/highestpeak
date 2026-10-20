\set ON_ERROR_STOP 0
-- V14 checks: pings and feedback can be added by anyone, read by no one through the API. Every check prints t;
-- every ERROR line is an expected refusal.
\echo == 1. pings
set role anon;
insert into public.pings (device, week, version, kind) values ('abc123def456', '2026-W43', 'V14', 'phone');
insert into public.pings (device, week, version, kind) values ('abc123def456', '2026-W43', 'V14', 'phone') on conflict do nothing;
insert into public.pings (device, week, version, kind) values ('abc123def456', '2026-W43', 'V14', 'phone');
insert into public.pings (device, week, version, kind) values ('bad id!', '2026-W43', 'V14', 'phone');
insert into public.pings (device, week, version, kind) values ('abc123def456', 'week 43', 'V14', 'phone');
insert into public.pings (device, week, version, kind) values ('abc123def456', '2026-W44', 'V14', 'tablet');
select count(*) from public.pings;
update public.pings set version = 'V99';
delete from public.pings;
set role authenticated;
insert into public.pings (device, week, version, kind) values ('zzz999yyy888', '2026-W43', 'V14', 'computer');
select count(*) from public.pings;
reset role;
select 'two pings stored, the duplicate ignored, bad ones refused, nothing readable or changeable by the app' as t, count(*) = 2 and bool_and(version = 'V14') as ok from public.pings;
\echo == 2. feedback
set role anon;
insert into public.feedback (message, email, version, kind) values ('Love the gym mode', null, 'V14', 'phone');
insert into public.feedback (message, email, version, kind) values ('Reply please', 'me@example.com', 'V14', 'computer');
insert into public.feedback (message) values ('');
insert into public.feedback (message) values (repeat('x', 2001));
insert into public.feedback (message, email) values ('Bad email', 'not an email');
select count(*) from public.feedback;
delete from public.feedback;
reset role;
select 'two messages stored, empty, too long and bad email refused, nothing readable by the app' as t, count(*) = 2 as ok from public.feedback;
\echo == 3. row level security is on
select 'rls on for both' as t, bool_and(relrowsecurity) as ok from pg_class where relname in ('pings', 'feedback') and relnamespace = 'public'::regnamespace;
