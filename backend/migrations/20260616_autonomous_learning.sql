begin;

create table if not exists autonomous_learning_feedback_events (
  event_id text primary key,
  source_type text not null check (source_type in ('SELF_EVALUATION','USER_FEEDBACK_EXPLICIT','USER_FEEDBACK_IMPLICIT')),
  minimal_feedback_reference text,
  dedup_fingerprint text unique,
  created_at timestamptz not null default now(),
  audit_trail jsonb not null default '[]'::jsonb
);

create table if not exists autonomous_learning_records (
  record_id text primary key,
  current_version_id text,
  source_type text not null check (source_type in ('SELF_EVALUATION','USER_FEEDBACK_EXPLICIT','USER_FEEDBACK_IMPLICIT')),
  originating_question text not null,
  original_answer text,
  corrected_proposed_fact text not null,
  source_citations jsonb not null default '[]'::jsonb,
  chapter_numbers jsonb not null default '[]'::jsonb,
  source_chunk_ids jsonb not null default '[]'::jsonb,
  user_feedback_reference text references autonomous_learning_feedback_events(event_id) on delete set null,
  provider text,
  model text,
  creation_timestamp timestamptz not null default now(),
  evidence_count integer not null default 0 check (evidence_count >= 0),
  independent_evidence_count integer not null default 0 check (independent_evidence_count >= 0),
  contradiction_count integer not null default 0 check (contradiction_count >= 0),
  support_score numeric not null default 0 check (support_score >= 0 and support_score <= 1),
  confidence_score numeric not null default 0 check (confidence_score >= 0 and confidence_score <= 1),
  trust_score numeric not null default 0 check (trust_score >= 0 and trust_score <= 1),
  current_trust_state text not null check (current_trust_state in ('OBSERVED','PROBATIONARY','TRUSTED','DEMOTED','QUARANTINED','RETIRED')),
  retrieval_weight numeric not null default 0 check (retrieval_weight >= 0 and retrieval_weight <= 1),
  version integer not null default 1 check (version >= 1),
  previous_version_id text,
  rollback_target_version_id text,
  promotion_reason text,
  demotion_reason text,
  last_validation_timestamp timestamptz,
  workflow_run_id text,
  user_feedback_event_id text references autonomous_learning_feedback_events(event_id) on delete set null,
  dedup_fingerprint text unique,
  audit_trail jsonb not null default '[]'::jsonb
);

create table if not exists autonomous_learning_record_versions (
  version_id text primary key,
  record_id text not null references autonomous_learning_records(record_id) on delete cascade,
  version integer not null check (version >= 1),
  snapshot jsonb not null,
  trust_state text not null check (trust_state in ('OBSERVED','PROBATIONARY','TRUSTED','DEMOTED','QUARANTINED','RETIRED')),
  dedup_fingerprint text,
  created_at timestamptz not null default now(),
  unique (record_id, version)
);

alter table autonomous_learning_records
  add constraint autonomous_learning_records_current_version_fk
  foreign key (current_version_id) references autonomous_learning_record_versions(version_id) deferrable initially deferred;

alter table autonomous_learning_records
  add constraint autonomous_learning_records_previous_version_fk
  foreign key (previous_version_id) references autonomous_learning_record_versions(version_id) deferrable initially deferred;

alter table autonomous_learning_records
  add constraint autonomous_learning_records_rollback_version_fk
  foreign key (rollback_target_version_id) references autonomous_learning_record_versions(version_id) deferrable initially deferred;

create table if not exists autonomous_learning_audit_events (
  id bigserial primary key,
  record_id text not null references autonomous_learning_records(record_id) on delete cascade,
  event jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists autonomous_learning_control (
  id text primary key,
  autonomous_learning_frozen boolean not null default false,
  disabled_sources jsonb not null default '[]'::jsonb,
  updated_at timestamptz not null default now()
);

insert into autonomous_learning_control (id, autonomous_learning_frozen)
values ('global', false)
on conflict (id) do nothing;

create index if not exists idx_autonomous_records_trust_state on autonomous_learning_records(current_trust_state);
create index if not exists idx_autonomous_records_source_type on autonomous_learning_records(source_type);
create index if not exists idx_autonomous_records_trust_score on autonomous_learning_records(trust_score desc);
create index if not exists idx_autonomous_records_last_validation on autonomous_learning_records(last_validation_timestamp desc);
create index if not exists idx_autonomous_records_retrieval on autonomous_learning_records(current_trust_state, retrieval_weight, trust_score) where current_trust_state = 'TRUSTED';
create index if not exists idx_autonomous_records_feedback_event on autonomous_learning_records(user_feedback_event_id);
create index if not exists idx_autonomous_records_workflow_run on autonomous_learning_records(workflow_run_id);
create index if not exists idx_autonomous_records_dedup on autonomous_learning_records(dedup_fingerprint);
create index if not exists idx_autonomous_versions_record on autonomous_learning_record_versions(record_id, version desc);
create index if not exists idx_autonomous_versions_dedup on autonomous_learning_record_versions(dedup_fingerprint);
create index if not exists idx_autonomous_audit_record on autonomous_learning_audit_events(record_id, created_at desc);

alter table autonomous_learning_records enable row level security;
alter table autonomous_learning_record_versions enable row level security;
alter table autonomous_learning_audit_events enable row level security;
alter table autonomous_learning_feedback_events enable row level security;
alter table autonomous_learning_control enable row level security;

do $$
begin
  create policy "autonomous trusted public read" on autonomous_learning_records
    for select using (current_trust_state = 'TRUSTED');
exception when duplicate_object then null;
end $$;

do $$
begin
  create policy "autonomous service write records" on autonomous_learning_records
    for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
exception when duplicate_object then null;
end $$;

do $$
begin
  create policy "autonomous service versions append" on autonomous_learning_record_versions
    for insert with check (auth.role() = 'service_role');
exception when duplicate_object then null;
end $$;

do $$
begin
  create policy "autonomous service audit append" on autonomous_learning_audit_events
    for insert with check (auth.role() = 'service_role');
exception when duplicate_object then null;
end $$;

do $$
begin
  create policy "autonomous service feedback write" on autonomous_learning_feedback_events
    for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
exception when duplicate_object then null;
end $$;

do $$
begin
  create policy "autonomous service control" on autonomous_learning_control
    for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
exception when duplicate_object then null;
end $$;

create or replace function prevent_autonomous_append_only_update()
returns trigger language plpgsql as $$
begin
  raise exception 'autonomous audit/version tables are append-only';
end;
$$;

drop trigger if exists trg_autonomous_versions_append_only on autonomous_learning_record_versions;
create trigger trg_autonomous_versions_append_only
before update or delete on autonomous_learning_record_versions
for each row execute function prevent_autonomous_append_only_update();

drop trigger if exists trg_autonomous_audit_append_only on autonomous_learning_audit_events;
create trigger trg_autonomous_audit_append_only
before update or delete on autonomous_learning_audit_events
for each row execute function prevent_autonomous_append_only_update();

commit;
