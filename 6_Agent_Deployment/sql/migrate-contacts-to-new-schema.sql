-- Migration script to update contacts table from old schema to new schema
-- This migration is only needed if your database still has a 'name' column
-- and lacks the first_name, last_name, role, and notes columns

-- Check if the migration is needed by checking if 'name' column exists
DO $$
BEGIN
    -- Only run migration if 'name' column exists
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'contacts'
        AND column_name = 'name'
    ) THEN
        -- Add new columns if they don't exist
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'contacts' AND column_name = 'first_name'
        ) THEN
            ALTER TABLE contacts ADD COLUMN first_name TEXT;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'contacts' AND column_name = 'last_name'
        ) THEN
            ALTER TABLE contacts ADD COLUMN last_name TEXT;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'contacts' AND column_name = 'role'
        ) THEN
            ALTER TABLE contacts ADD COLUMN role TEXT;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'contacts' AND column_name = 'notes'
        ) THEN
            ALTER TABLE contacts ADD COLUMN notes TEXT;
        END IF;

        -- Migrate existing data from 'name' to first_name and last_name
        UPDATE contacts
        SET
            first_name = CASE
                WHEN name IS NOT NULL AND name != '' THEN
                    TRIM(SUBSTRING(name FROM '^[^ ]+'))
                ELSE NULL
            END,
            last_name = CASE
                WHEN name IS NOT NULL AND name LIKE '% %' THEN
                    TRIM(SUBSTRING(name FROM ' (.*)$'))
                ELSE NULL
            END
        WHERE first_name IS NULL OR last_name IS NULL;

        -- Drop the old 'name' column
        ALTER TABLE contacts DROP COLUMN IF EXISTS name;

        -- Drop company_id if it exists (not in the new schema)
        ALTER TABLE contacts DROP COLUMN IF EXISTS company_id;

        -- Drop job_title if it exists (replaced by 'role')
        ALTER TABLE contacts DROP COLUMN IF EXISTS job_title;

        RAISE NOTICE 'Migration completed successfully';
    ELSE
        RAISE NOTICE 'Migration not needed - contacts table already has the new schema';
    END IF;
END $$;