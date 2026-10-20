-- local stand-in for Supabase's realtime schema (Realtime checks these policies when a device joins a private channel,
-- with realtime.topic() set to the channel's topic)
create schema if not exists realtime;
grant usage on schema realtime to authenticated, anon;
create table if not exists realtime.messages (id bigserial primary key, topic text not null, extension text not null, event text, payload jsonb, private boolean default true, inserted_at timestamptz default now());
alter table realtime.messages enable row level security;
grant select, insert on realtime.messages to authenticated, anon; grant usage on sequence realtime.messages_id_seq to authenticated, anon;
create or replace function realtime.topic() returns text language sql stable as $$ select nullif(current_setting('realtime.topic', true), '') $$;
