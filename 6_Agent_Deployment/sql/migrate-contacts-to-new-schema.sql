-- Add the current contacts fields while preserving the legacy values and
-- company associations until every consumer has moved to the new schema.
DO $$
BEGIN
    IF to_regclass('public.contacts') IS NULL THEN
        RAISE EXCEPTION 'Migration requires public.contacts to exist';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'contacts'
          AND column_name IN ('name', 'job_title')
    ) THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'contacts'
              AND column_name = 'first_name'
        ) THEN
            ALTER TABLE public.contacts ADD COLUMN first_name TEXT;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'contacts'
              AND column_name = 'last_name'
        ) THEN
            ALTER TABLE public.contacts ADD COLUMN last_name TEXT;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'contacts'
              AND column_name = 'role'
        ) THEN
            ALTER TABLE public.contacts ADD COLUMN role TEXT;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'contacts'
              AND column_name = 'notes'
        ) THEN
            ALTER TABLE public.contacts ADD COLUMN notes TEXT;
        END IF;

        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'contacts'
              AND column_name = 'name'
        ) THEN
            UPDATE public.contacts
            SET
                first_name = COALESCE(
                    first_name,
                    NULLIF(substring(btrim(name) FROM '^([^[:space:]]+)'), '')
                ),
                last_name = COALESCE(
                    last_name,
                    NULLIF(btrim(substring(btrim(name) FROM '^[^[:space:]]+[[:space:]]+(.*)$')), '')
                )
            WHERE name IS NOT NULL
              AND (first_name IS NULL OR last_name IS NULL);
        END IF;

        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'contacts'
              AND column_name = 'job_title'
        ) THEN
            UPDATE public.contacts
            SET role = COALESCE(role, job_title)
            WHERE job_title IS NOT NULL;
        END IF;

        -- Keep name, job_title, and company_id. Dropping them here would lose
        -- source values and company links before all consumers are migrated.
        RAISE NOTICE 'Contacts fields added and legacy values copied; legacy columns preserved';
    ELSE
        RAISE NOTICE 'Migration not needed - no legacy name or job_title columns found';
    END IF;
END $$;
