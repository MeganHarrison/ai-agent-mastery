#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_FILE="${SCRIPT_DIR}/migrate-contacts-to-new-schema.sql"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/contacts-migration-test.XXXXXX")"
TEST_PGDATA="${TEST_ROOT}/data"
TEST_SOCKET="${TEST_ROOT}/socket"
TEST_PORT="$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')"

cleanup() {
  if [[ -f "${TEST_PGDATA}/postmaster.pid" ]]; then
    pg_ctl -D "${TEST_PGDATA}" -m fast stop >/dev/null
  fi
  rm -rf "${TEST_ROOT}"
}
trap cleanup EXIT

mkdir -p "${TEST_SOCKET}"
initdb -D "${TEST_PGDATA}" --no-locale --encoding=UTF8 --auth=trust >/dev/null
pg_ctl -D "${TEST_PGDATA}" \
  -l "${TEST_ROOT}/postgres.log" \
  -o "-F -k '${TEST_SOCKET}' -p ${TEST_PORT} -h ''" start >/dev/null

psql -v ON_ERROR_STOP=1 -h "${TEST_SOCKET}" -p "${TEST_PORT}" -d postgres <<'SQL'
CREATE TABLE public.companies (
  id text PRIMARY KEY,
  name text NOT NULL
);
CREATE TABLE public.contacts (
  id integer PRIMARY KEY,
  name text,
  job_title text,
  company_id text REFERENCES public.companies(id)
);
INSERT INTO public.companies (id, name) VALUES ('company-1', 'Northstar Builders');
INSERT INTO public.contacts (id, name, job_title, company_id) VALUES
  (1, 'Samira Chen', 'Estimator', 'company-1'),
  (2, 'Priya Shah', 'Controller', NULL),
  (3, 'Madonna', NULL, NULL);
SQL

psql -v ON_ERROR_STOP=1 -h "${TEST_SOCKET}" -p "${TEST_PORT}" -d postgres -f "${MIGRATION_FILE}"
psql -v ON_ERROR_STOP=1 -h "${TEST_SOCKET}" -p "${TEST_PORT}" -d postgres \
  -c "UPDATE public.contacts SET role = 'Chief Financial Officer' WHERE id = 2"
psql -v ON_ERROR_STOP=1 -h "${TEST_SOCKET}" -p "${TEST_PORT}" -d postgres -f "${MIGRATION_FILE}"
psql -v ON_ERROR_STOP=1 -h "${TEST_SOCKET}" -p "${TEST_PORT}" -d postgres <<'SQL'
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'contacts' AND column_name = 'company_id'
  ) THEN
    RAISE EXCEPTION 'company_id was removed';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = 'contacts' AND column_name = 'job_title'
  ) THEN
    RAISE EXCEPTION 'job_title was removed';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM public.contacts
    WHERE id = 1 AND first_name = 'Samira' AND last_name = 'Chen'
      AND role = 'Estimator' AND company_id = 'company-1'
  ) THEN
    RAISE EXCEPTION 'legacy name, role, or company link was not preserved';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM public.contacts
    WHERE id = 2 AND role = 'Chief Financial Officer' AND job_title = 'Controller'
  ) THEN
    RAISE EXCEPTION 'existing role was overwritten or legacy job_title was lost';
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM public.contacts
    WHERE id = 3 AND first_name = 'Madonna' AND last_name IS NULL
  ) THEN
    RAISE EXCEPTION 'single-token contact name was split incorrectly';
  END IF;
END $$;
SELECT 'contacts migration preservation checks passed' AS result;
SQL
