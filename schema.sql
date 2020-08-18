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
CREATE TABLE books_read (
    book_id     SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    author      TEXT NOT NULL,
    comment     TEXT,
    rating      TEXT,
    user_id     INTEGER,
    genre       TEXT,
    pages       INTEGER

);
CREATE TABLE books_currently_reading (
    book_id      SERIAL PRIMARY KEY,
    title        TEXT NOT NULL,
    author       TEXT NOT NULL,
    genre        TEXT,
    plot_summary TEXT,
    current_page INTEGER,
    pages        INTEGER,
    user_id      INTEGER NOT NULL
);

CREATE TABLE public_books_read (
    book_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    comment TEXT,
    rating TEXT,
    user_id INTEGER
);

CREATE TABLE links (
   link_id serial PRIMARY KEY,
   title VARCHAR (512) NOT NULL,
   url VARCHAR (1024) NOT NULL
);