-- Adds columns for relaxed 100-actor layout positions.
alter table public.actors
  add column if not exists x_100 double precision,
  add column if not exists y_100 double precision;
