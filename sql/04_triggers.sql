
CREATE OR REPLACE FUNCTION set_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER documents_on_update_current_timestamp BEFORE UPDATE
    ON document FOR EACH ROW EXECUTE PROCEDURE
    set_updated_at_column();




CREATE OR REPLACE FUNCTION insert_job_after_url_insert()
RETURNS TRIGGER AS $$
BEGIN
   INSERT INTO jobs (queue, payload) VALUES ('spider', '{ "url_id": ' || NEW.id || ' }'::json);
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER insert_job_after_url_insert AFTER INSERT
    ON urls FOR EACH ROW EXECUTE PROCEDURE
    insert_job_after_url_insert();