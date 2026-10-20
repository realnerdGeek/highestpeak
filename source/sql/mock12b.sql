create table auth.mfa_factors (id uuid primary key default gen_random_uuid(), user_id uuid references auth.users (id) on delete cascade, status text);
-- no read access for signed-in users
create function auth.jwt() returns jsonb language sql stable as $$ select coalesce(nullif(current_setting('request.jwt.claims', true), ''), '{}')::jsonb $$;
