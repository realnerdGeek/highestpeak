-- HighestPeak V12 fix: the two-step rules now check through a helper that is allowed to look,
-- because signed-in users can't read the sign-in factors table themselves. Paste and run once.
create or replace function public.hp_two_step_ok() returns boolean
language sql stable security definer set search_path = '' as $$
  select coalesce((select auth.jwt()->>'aal'), '') = 'aal2'
      or not exists (select 1 from auth.mfa_factors f where f.user_id = (select auth.uid()) and f.status = 'verified');
$$;
revoke all on function public.hp_two_step_ok() from public, anon;
grant execute on function public.hp_two_step_ok() to authenticated;

drop policy if exists "two-step when on" on public.docs;
create policy "two-step when on" on public.docs as restrictive to authenticated
  using ((select public.hp_two_step_ok())) with check ((select public.hp_two_step_ok()));
drop policy if exists "two-step when on" on public.profiles;
create policy "two-step when on" on public.profiles as restrictive to authenticated
  using ((select public.hp_two_step_ok())) with check ((select public.hp_two_step_ok()));
drop policy if exists "hp two-step when on" on storage.objects;
create policy "hp two-step when on" on storage.objects as restrictive to authenticated
  using (bucket_id <> 'media' or (select public.hp_two_step_ok())) with check (bucket_id <> 'media' or (select public.hp_two_step_ok()));
