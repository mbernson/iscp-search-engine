CREATE OR REPLACE FUNCTION set_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$ language 'plpgsql';


CREATE TRIGGER documents_on_update_current_timestamp BEFORE UPDATE
    ON documents FOR EACH ROW EXECUTE PROCEDURE
    set_updated_at_column();


CREATE or replace FUNCTION insert_job_after_url_insert() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  crawl_at TIMESTAMP;
BEGIN
  crawl_at := (select max(available_at) + interval '2 seconds' from jobs
    where jobs.domain = NEW.domain and available_at < (now() + interval '6 days'));

  IF crawl_at is null THEN
    crawl_at := now() + interval '2 seconds';
  END IF;

  INSERT INTO jobs (queue, payload, domain, available_at) VALUES ('spider', ('{"url_id": ' || NEW.id || '}')::json,
    NEW.domain, crawl_at
  );
  RETURN NEW;
END;
$$;


CREATE TRIGGER insert_job_after_url_insert AFTER INSERT
    ON urls FOR EACH ROW EXECUTE PROCEDURE
    insert_job_after_url_insert();
