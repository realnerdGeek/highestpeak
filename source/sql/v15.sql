-- EarWorm V15 setup: Play anywhere. Your signed-in devices share one private live channel, "ew:<your account id>".
-- Only your own devices can join it, see who is on it, or send on it, and two-step sign-in applies here too.
-- This adds to the earlier setup code. After pasting, also turn off "Allow public access" in Realtime Settings.
drop policy if exists "ew: own devices listen" on realtime.messages;
create policy "ew: own devices listen" on realtime.messages for select to authenticated
  using ((select realtime.topic()) = 'ew:' || (select auth.uid())::text
         and realtime.messages.extension in ('broadcast', 'presence')
         and (select public.hp_two_step_ok()));
drop policy if exists "ew: own devices send" on realtime.messages;
create policy "ew: own devices send" on realtime.messages for insert to authenticated
  with check ((select realtime.topic()) = 'ew:' || (select auth.uid())::text
              and realtime.messages.extension in ('broadcast', 'presence')
              and (select public.hp_two_step_ok()));
