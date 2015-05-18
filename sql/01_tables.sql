create table urls (
    id BIGSERIAL PRIMARY KEY,

    url TEXT NOT NULL,

    scheme TEXT DEFAULT 'http' NOT NULL,
    domain TEXT NOT NULL,
    path TEXT,
    params TEXT,
    query TEXT,
    fragment TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
);
create table crawlings (
    id SERIAL PRIMARY KEY,

    url_id BIGINT NOT NULL REFERENCES urls (id),
    status_code SMALLINT NOT NULL,
    headers TEXT,
    body TEXT,
    content TEXT,

    created_at TIMESTAMP DEFAULT NOW(),
);
