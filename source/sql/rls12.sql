\set ON_ERROR_STOP 0
create or replace function pg_temp.as_user(uid text, aal text) returns void language plpgsql as $$
begin
  perform set_config('request.jwt.claim.sub', uid, false);
  perform set_config('request.jwt.claims', json_build_object('sub', uid, 'aal', aal)::text, false);
end $$;
\echo == 1. username rules
set role authenticated; select pg_temp.as_user('11111111-1111-1111-1111-111111111111', 'aal1');
insert into public.profiles (username) values ('matt.w_9');
select 'own profile visible' as t, count(*) = 1 as ok from public.profiles;
insert into public.profiles (user_id, username) values ('22222222-2222-2222-2222-222222222222', 'someone');
update public.profiles set username = 'matt_w';
select 'rename works' as t, username = 'matt_w' as ok from public.profiles;
select pg_temp.as_user('22222222-2222-2222-2222-222222222222', 'aal1');
select 'other user sees nothing' as t, count(*) = 0 as ok from public.profiles;
select 'taken check (any case)' as t, public.username_taken('MATT_W') and not public.username_taken('free.name') as ok;
insert into public.profiles (username) values ('matt_w');
insert into public.profiles (username) values ('ab');
insert into public.profiles (username) values ('Has Space');
insert into public.profiles (username) values ('waaaaaaaaaaaaaaaaaaay2long');
insert into public.profiles (username) values ('user.two');
select pg_temp.as_user('11111111-1111-1111-1111-111111111111', 'aal1');
select 'own name not counted as taken' as t, not public.username_taken('matt_w') as ok;
\echo == 2. two-step off: library opens normally
insert into public.docs (coll, id, data, m) values ('tracks', 't1', '{}', 1);
insert into storage.objects (bucket_id, name) values ('media', '11111111-1111-1111-1111-111111111111/b1');
select 'docs + files ok at aal1' as t, (select count(*) from public.docs) = 1 and (select count(*) from storage.objects) = 1 as ok;
\echo == 3. two-step on (verified authenticator)
reset role; insert into auth.mfa_factors (user_id, status) values ('22222222-2222-2222-2222-222222222222', 'unverified'), ('11111111-1111-1111-1111-111111111111', 'verified'); set role authenticated;
select pg_temp.as_user('11111111-1111-1111-1111-111111111111', 'aal1');
select 'aal1 sees no docs/files/profile' as t, (select count(*) from public.docs) = 0 and (select count(*) from storage.objects) = 0 and (select count(*) from public.profiles) = 0 as ok;
insert into public.docs (coll, id, data, m) values ('tracks', 't2', '{}', 1);
insert into storage.objects (bucket_id, name) values ('media', '11111111-1111-1111-1111-111111111111/b2');
select public.delete_my_account();
select pg_temp.as_user('11111111-1111-1111-1111-111111111111', 'aal2');
select 'aal2 opens it all' as t, (select count(*) from public.docs) = 1 and (select count(*) from storage.objects) = 1 and (select count(*) from public.profiles) = 1 as ok;
insert into public.docs (coll, id, data, m) values ('tracks', 't2', '{}', 1);
select pg_temp.as_user('22222222-2222-2222-2222-222222222222', 'aal1');
select 'half-set-up authenticator does not lock' as t, (select count(*) from public.profiles) = 1 as ok;
\echo == 4. delete account
set role anon;
select public.delete_my_account();
select public.username_taken('x');
set role authenticated; select pg_temp.as_user('11111111-1111-1111-1111-111111111111', 'aal2');
select public.delete_my_account();
reset role;
select 'user, docs, profile, factor gone; other user kept' as t,
  (select count(*) from auth.users where id = '11111111-1111-1111-1111-111111111111') = 0
  and (select count(*) from public.docs where user_id = '11111111-1111-1111-1111-111111111111') = 0
  and (select count(*) from public.profiles where user_id = '11111111-1111-1111-1111-111111111111') = 0
  and (select count(*) from auth.mfa_factors where user_id = '11111111-1111-1111-1111-111111111111') = 0
  and (select count(*) from public.profiles) = 1 as ok;
