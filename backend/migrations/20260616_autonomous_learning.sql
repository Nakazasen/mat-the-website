create table if not exists autonomous_learning_records (
  record_id text primary key,
  source_type text not null check (source_type in ('SELF_EVALUATION','USER_FEEDBACK_EXPLICIT','USER_FEEDBACK_IMPLICIT')),
  originating_question text not null,
  original_answer text,
  corrected_proposed_fact text not null,
  source_citations jsonb not null default '[]'::jsonb,
  chapter_numbers jsonb not null default '[]'::jsonb,
  source_chunk_ids jsonb not null default '[]'::jsonb,
  user_feedback_reference text,
  provider text,
  model text,
  creation_timestamp timestamptz not null default now(),
  evidence_count integer not null default 0,
  independent_evidence_count integer not null default 0,
  contradiction_count integer not null default 0,
  support_score numeric not null default 0,
  confidence_score numeric not null default 0,
  trust_score numeric not null default 0,
  current_trust_state text not null check (current_trust_state in ('OBSERVED','PROBATIONARY','TRUSTED','DEMOTED','QUARANTINED','RETIRED')),
  retrieval_weight numeric not null default 0,
  version integer not null default 1,
  previous_version integer,
  rollback_target integer,
  promotion_reason text,
  demotion_reason text,
  last_validation_timestamp timestamptz,
  workflow_run_id text,
  user_feedback_event_id text,
  audit_trail jsonb not null default '[]'::jsonb
);

create table if not exists autonomous_learning_audit_events (
  id bigserial primary key,
  record_id text not null,
  event jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists autonomous_learning_feedback_events (
  event_id text primary key,
  source_type text not null,
  minimal_feedback_reference text,
  created_at timestamptz not null default now(),
  audit_trail jsonb not null default '[]'::jsonb
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
