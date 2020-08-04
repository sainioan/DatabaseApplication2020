CREATE TABLE users (
    id     SERIAL PRIMARY KEY,
    username  TEXT UNIQUE NOT NULL,
    password     TEXT NOT NULL
);

CREATE TABLE booksToRead (
    book_id     SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    author      TEXT NOT NULL,
    user_id     INTEGER
);
CREATE TABLE myBooks (
    book_id     SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    author      TEXT NOT NULL,
    comment     TEXT,
    rating      TEXT,
    img         bytea,
    user_id     INTEGER
);