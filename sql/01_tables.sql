create table urls (
    id BIGSERIAL PRIMARY KEY,

    url TEXT NOT NULL,

    schema TEXT DEFAULT 'http' NOT NULL,
    domain TEXT NOT NULL,
    path TEXT,
    params TEXT,
    query TEXT,
    fragment TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

create table documents (
    id BIGSERIAL PRIMARY KEY,

	language TEXT,

    url_id BIGINT NOT NULL REFERENCES urls (id),
    status_code SMALLINT NOT NULL,
    headers TEXT,
    title TEXT,
    body TEXT,
    content TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

create table excerpts (
    id BIGSERIAL PRIMARY KEY,

    document_id BIGINT NOT NULL REFERENCES documents (id),

    body TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX excerpts_fulltext_index ON excerpts (body) USING gin(to_tsvector(language, body));

create table images (
	id BIGSERIAL PRIMARY KEY,
	
	document_id BIGINT NOT NULL REFERENCES documents (id),
	
	url TEXT,
	alt TEXT,
	
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLESPACE scratch LOCATION '/mnt/usb_scratch/postgresql/data';

create table testing (
	id BIGSERIAL PRIMARY KEY
) TABLESPACE scratch;