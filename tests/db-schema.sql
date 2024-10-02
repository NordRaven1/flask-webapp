CREATE TABLE IF NOT EXISTS articles (
    article_id TEXT PRIMARY KEY,
    article_title TEXT NOT NULL,
    parent_course_id TEXT REFERENCES courses (course_id) ON DELETE CASCADE NOT NULL,
    article_text TEXT NOT NULL,
    author_id TEXT REFERENCES users (user_id) ON DELETE CASCADE,
    image BLOB
    );

CREATE TABLE IF NOT EXISTS comments (
    comment_id TEXT PRIMARY KEY,
    comment_text TEXT NOT NULL,
    author_id TEXT REFERENCES users (user_id) ON DELETE CASCADE NOT NULL,
    parent_article_id TEXT REFERENCES articles (article_id) ON DELETE CASCADE NOT NULL,
    parent_comment_id TEXT DEFAULT NULL REFERENCES comments (comment_id) ON DELETE CASCADE);

CREATE TABLE IF NOT EXISTS courses (
    course_id TEXT PRIMARY KEY,
    course_title TEXT NOT NULL UNIQUE,
    author_id TEXT REFERENCES users (user_id) ON DELETE CASCADE,
    description TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS fav_courses (
    user_id   TEXT REFERENCES users (user_id) ON DELETE NO ACTION,
    course_id TEXT REFERENCES courses (course_id) ON DELETE NO ACTION,
    PRIMARY KEY (user_id, course_id));

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    login TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'author', 'reader')));

CREATE UNIQUE INDEX IF NOT EXISTS title_parcourse_idx ON articles (article_title, parent_course_id);

