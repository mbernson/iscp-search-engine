-- CREATE TABLESPACE scratch LOCATION '/mnt/usb_scratch/postgresql/data';

create table jobs (
    id BIGSERIAL PRIMARY KEY,
    
    queue TEXT NOT NULL,
    payload JSON NOT NULL,
        
    reserved BOOLEAN DEFAULT 'f' NOT NULL,
    reserved_at TIMESTAMP DEFAULT NULL,
    available_at TIMESTAMP NOT NULL DEFAULT NOW(),
    attempts integer DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

create table urls (
    id BIGSERIAL PRIMARY KEY,

    url TEXT NOT NULL,

    scheme TEXT DEFAULT 'http' NOT NULL,
    domain TEXT NOT NULL,
    path TEXT,
    params TEXT,
    query TEXT,
    fragment TEXT,
    port SMALLINT DEFAULT 80,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE (url),
    UNIQUE (scheme, domain, path, params, query, fragment, port)
);

create table documents (
    id BIGSERIAL PRIMARY KEY,

    language regconfig NOT NULL DEFAULT 'english'::regconfig,

	  url_id BIGINT NOT NULL REFERENCES urls (id) ON DELETE CASCADE,

    status_code SMALLINT NOT NULL,
    headers JSON NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);

create table excerpts (
    id BIGSERIAL PRIMARY KEY,

    document_id BIGINT NOT NULL REFERENCES documents (id)  ON DELETE CASCADE,
    language regconfig NOT NULL DEFAULT 'english'::regconfig,

    tag TEXT NOT NULL DEFAULT 'p',
    importance SMALLINT NOT NULL DEFAULT 0,
    body TEXT NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX excerpts_body_fulltext_index ON excerpts USING gin(to_tsvector(language, body));

create table images (
    id BIGSERIAL PRIMARY KEY,
    
    document_id BIGINT NOT NULL REFERENCES documents (id)  ON DELETE CASCADE,
    
    url TEXT,
    alt TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);