DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_mode') THEN
    CREATE TYPE user_mode AS ENUM ('NONE', 'BOOKING', 'QUESTION', 'GROUP_PASSWORD');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'screen_code') THEN
    CREATE TYPE screen_code AS ENUM (
      'MENU',
      'B001','B002','B003','B003B','B004','B005','B006',
      'Q1','Q2',
      'G1','G2',
      'W1'
    );
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'draft_status') THEN
    CREATE TYPE draft_status AS ENUM ('ACTIVE', 'CANCELLED', 'EXPIRED', 'CONFIRMED');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'session_format') THEN
    CREATE TYPE session_format AS ENUM ('ONLINE', 'OFFLINE');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'slot_status') THEN
    CREATE TYPE slot_status AS ENUM ('FREE', 'HELD', 'BOOKED', 'DISABLED');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'hold_status') THEN
    CREATE TYPE hold_status AS ENUM ('ACTIVE', 'RELEASED', 'EXPIRED', 'CONVERTED');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'booking_status') THEN
    CREATE TYPE booking_status AS ENUM ('BOOKED', 'CANCELLED');
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'question_status') THEN
    CREATE TYPE question_status AS ENUM ('NEW', 'READ', 'ANSWERED');
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS user_state (
  user_id    BIGINT PRIMARY KEY,
  mode       user_mode NOT NULL DEFAULT 'NONE',
  screen     screen_code NOT NULL DEFAULT 'MENU',
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS slots (
  slot_id           UUID PRIMARY KEY,
  start_at          TIMESTAMPTZ NOT NULL,
  duration_min      SMALLINT NOT NULL CHECK (duration_min > 0),
  status            slot_status NOT NULL DEFAULT 'FREE',
  held_by_user_id   BIGINT NULL,
  hold_expires_at   TIMESTAMPTZ NULL,
  booked_by_user_id BIGINT NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (
    (status = 'FREE'   AND held_by_user_id IS NULL AND hold_expires_at IS NULL AND booked_by_user_id IS NULL)
 OR (status = 'HELD'   AND held_by_user_id IS NOT NULL AND hold_expires_at IS NOT NULL AND booked_by_user_id IS NULL)
 OR (status = 'BOOKED' AND booked_by_user_id IS NOT NULL)
 OR (status = 'DISABLED')
  )
);

-- Уникальность слота по времени (чтобы seed был идемпотентный)
CREATE UNIQUE INDEX IF NOT EXISTS uq_slots_start_at_unique ON slots(start_at);
CREATE INDEX IF NOT EXISTS idx_slots_status_start ON slots(status, start_at);

CREATE TABLE IF NOT EXISTS holds (
  hold_id    UUID PRIMARY KEY,
  slot_id    UUID NOT NULL REFERENCES slots(slot_id) ON DELETE CASCADE,
  user_id    BIGINT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  status     hold_status NOT NULL DEFAULT 'ACTIVE',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_holds_one_active_per_slot
ON holds(slot_id)
WHERE status = 'ACTIVE';

CREATE TABLE IF NOT EXISTS booking_drafts (
  draft_id       UUID PRIMARY KEY,
  user_id        BIGINT NOT NULL,
  status         draft_status NOT NULL DEFAULT 'ACTIVE',
  format         session_format NULL,
  selected_day   DATE NULL,
  slot_id        UUID NULL REFERENCES slots(slot_id) ON DELETE SET NULL,
  hold_id        UUID NULL REFERENCES holds(hold_id) ON DELETE SET NULL,
  contact_phone  TEXT NULL,
  opened_terms   BOOLEAN NOT NULL DEFAULT FALSE,
  opened_privacy BOOLEAN NOT NULL DEFAULT FALSE,
  consent_id     UUID NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_one_active_draft_per_user
ON booking_drafts(user_id)
WHERE status = 'ACTIVE';

CREATE TABLE IF NOT EXISTS consents (
  consent_id      UUID PRIMARY KEY,
  user_id         BIGINT NOT NULL,
  draft_id        UUID NOT NULL REFERENCES booking_drafts(draft_id) ON DELETE CASCADE,
  terms_version   TEXT NOT NULL,
  privacy_version TEXT NOT NULL,

Denis Leoto, [15.01.2026 12:00]
accepted_at     TIMESTAMPTZ NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

ALTER TABLE booking_drafts
  ADD CONSTRAINT IF NOT EXISTS fk_booking_drafts_consent
  FOREIGN KEY (consent_id) REFERENCES consents(consent_id)
  ON DELETE SET NULL;

CREATE TABLE IF NOT EXISTS bookings (
  booking_id    UUID PRIMARY KEY,
  user_id       BIGINT NOT NULL,
  slot_id       UUID NOT NULL REFERENCES slots(slot_id) ON DELETE RESTRICT,
  format        session_format NOT NULL,
  contact_phone TEXT NOT NULL,
  consent_id    UUID NOT NULL REFERENCES consents(consent_id) ON DELETE RESTRICT,
  status        booking_status NOT NULL DEFAULT 'BOOKED',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_bookings_slot_once ON bookings(slot_id);

CREATE TABLE IF NOT EXISTS questions (
  question_id         UUID PRIMARY KEY,
  user_id             BIGINT NOT NULL,
  telegram_message_id BIGINT NOT NULL,
  content_type        TEXT NOT NULL,
  text                TEXT NULL,
  payload_meta        JSONB NULL,
  status              question_status NOT NULL DEFAULT 'NEW',
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS group_access (
  user_id         BIGINT PRIMARY KEY,
  is_granted      BOOLEAN NOT NULL DEFAULT FALSE,
  granted_at      TIMESTAMPTZ NULL,
  failed_attempts INT NOT NULL DEFAULT 0 CHECK (failed_attempts >= 0),
  blocked_until   TIMESTAMPTZ NULL,
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_events (
  event_id      BIGSERIAL PRIMARY KEY,
  user_id       BIGINT NULL,
  event_type    TEXT NOT NULL,
  payload       JSONB NULL,
  mode_before   user_mode NULL,
  screen_before screen_code NULL,
  mode_after    user_mode NULL,
  screen_after  screen_code NULL,
  result        TEXT NOT NULL,
  error_code    TEXT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_user_created ON audit_events(user_id, created_at);