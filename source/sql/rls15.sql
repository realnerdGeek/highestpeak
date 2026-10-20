\set ON_ERROR_STOP 0
-- V15 checks: the Play anywhere channel. Realtime asks the database whether a signed-in device may read (join, see
-- presence) or send on a topic. Every check prints t; every ERROR line is an expected refusal.
create or replace function pg_temp.as_user(uid text, aal text, topic text) returns void language plpgsql as $$
begin
  perform set_config('request.jwt.claim.sub', uid, false);
  perform set_config('request.jwt.claims', json_build_object('sub', uid, 'aal', aal)::text, false);
  perform set_config('realtime.topic', topic, false);
end $$;
-- what Realtime looks at: a broadcast row, a presence row, and one of another kind
insert into realtime.messages (topic, extension, event) values ('probe', 'broadcast', 'state'), ('probe', 'presence', 'sync'), ('probe', 'postgres_changes', 'x');
\echo == 1. your own devices, on your own channel
set role authenticated; select pg_temp.as_user('11111111-1111-1111-1111-111111111111', 'aal1', 'ew:11111111-1111-1111-1111-111111111111');
select 'can listen to broadcast and presence on own channel' as t, count(*) = 2 as ok from realtime.messages where extension in ('broadcast', 'presence');
select 'nothing else' as t, count(*) = 0 as ok from realtime.messages where extension = 'postgres_changes';
insert into realtime.messages (topic, extension, event) values ('ew:11111111-1111-1111-1111-111111111111', 'broadcast', 'state');
insert into realtime.messages (topic, extension, event) values ('ew:11111111-1111-1111-1111-111111111111', 'presence', 'track');
insert into realtime.messages (topic, extension, event) values ('ew:11111111-1111-1111-1111-111111111111', 'postgres_changes', 'x');
reset role;
select 'sent a broadcast and presence, not the other kind' as t, count(*) = 2 as ok from realtime.messages where topic = 'ew:11111111-1111-1111-1111-111111111111';
\echo == 2. another account trying your channel
set role authenticated; select pg_temp.as_user('22222222-2222-2222-2222-222222222222', 'aal1', 'ew:11111111-1111-1111-1111-111111111111');
select 'cannot listen to someone else''s channel' as t, count(*) = 0 as ok from realtime.messages;
insert into realtime.messages (topic, extension, event) values ('ew:11111111-1111-1111-1111-111111111111', 'broadcast', 'state');
select pg_temp.as_user('22222222-2222-2222-2222-222222222222', 'aal1', 'ew:other');
select 'cannot listen to a made-up channel either' as t, count(*) = 0 as ok from realtime.messages;
select pg_temp.as_user('22222222-2222-2222-2222-222222222222', 'aal1', 'ew:22222222-2222-2222-2222-222222222222');
select 'but can use their own' as t, count(*) = 2 as ok from realtime.messages where topic = 'probe';
reset role;
\echo == 3. not signed in
set role anon; select pg_temp.as_user('', '', 'ew:11111111-1111-1111-1111-111111111111');
select 'anon sees nothing' as t, count(*) = 0 as ok from realtime.messages;
insert into realtime.messages (topic, extension, event) values ('ew:11111111-1111-1111-1111-111111111111', 'broadcast', 'state');
reset role;
\echo == 4. two-step sign-in is on: a device that has not entered the code is kept out
insert into auth.mfa_factors (user_id, status) values ('11111111-1111-1111-1111-111111111111', 'verified');
set role authenticated; select pg_temp.as_user('11111111-1111-1111-1111-111111111111', 'aal1', 'ew:11111111-1111-1111-1111-111111111111');
select 'without the code: nothing' as t, count(*) = 0 as ok from realtime.messages;
insert into realtime.messages (topic, extension, event) values ('ew:11111111-1111-1111-1111-111111111111', 'broadcast', 'state');
select pg_temp.as_user('11111111-1111-1111-1111-111111111111', 'aal2', 'ew:11111111-1111-1111-1111-111111111111');
select 'with the code: works again' as t, count(*) >= 2 as ok from realtime.messages where topic = 'probe';
reset role;
