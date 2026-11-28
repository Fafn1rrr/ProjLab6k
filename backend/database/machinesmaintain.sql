BEGIN;


LOCK TABLE machines IN ACCESS EXCLUSIVE MODE;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY
);

DO $migration$
BEGIN
    IF EXISTS (
        SELECT 1 FROM schema_migrations WHERE version = 'PRO-165-PRO-166'
    ) THEN
        RETURN;
    END IF;

   
    ALTER TABLE machines
        ALTER COLUMN available_time TYPE NUMERIC(14,2)
            USING (available_time * 60),
        ADD COLUMN continuous_printing_time NUMERIC(12,2) NOT NULL DEFAULT 0
            CHECK (continuous_printing_time >= 0),
        ADD COLUMN maintenance_time NUMERIC(12,2) NOT NULL DEFAULT 0
            CHECK (maintenance_time >= 0);

    ALTER TABLE processing_times
        ALTER COLUMN processing_time TYPE NUMERIC(14,4)
            USING (processing_time * 60);

    COMMENT ON COLUMN machines.available_time IS 'Available machine time in minutes';
    COMMENT ON COLUMN machines.continuous_printing_time IS 'Continuous printing time before maintenance in minutes';
    COMMENT ON COLUMN machines.maintenance_time IS 'Maintenance duration in minutes';
    COMMENT ON COLUMN processing_times.processing_time IS 'Processing time per book in minutes';

    INSERT INTO schema_migrations (version) VALUES ('PRO-165-PRO-166');
END;
$migration$;

COMMIT;
