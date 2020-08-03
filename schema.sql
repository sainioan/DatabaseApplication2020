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
