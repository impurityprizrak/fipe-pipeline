CREATE TABLE fipe (
    id VARCHAR(20) NOT NULL,
    type VARCHAR(50) NOT NULL,
    value NUMERIC(10, 2) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year VARCHAR(50) NOT NULL,
    fuel VARCHAR(50) NOT NULL,
    month_reference CHAR(7) NOT NULL,
    fuel_sign CHAR(1) NOT NULL,
    CONSTRAINT fipe_pkey PRIMARY KEY (id,year)
);

CREATE TABLE brands (
    id VARCHAR(20) NOT NULL,
    name TEXT NOT NULL,
    CONSTRAINT brands_pkey PRIMARY KEY (id)
);

CREATE TABLE models (
    id VARCHAR(20) NOT NULL,
    name TEXT NOT NULL,
    CONSTRAINT models_pkey PRIMARY KEY (id)
);

CREATE TABLE years (
    id VARCHAR(20) NOT NULL,
    name TEXT NOT NULL,
    CONSTRAINT years_pkey PRIMARY KEY (id)
);