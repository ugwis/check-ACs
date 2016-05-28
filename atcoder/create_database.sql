CREATE DATABASE atcoderdb;

CREATE TABLE registrants (
	uid			SERIAL	PRIMARY KEY,
	twitterid	TEXT
);

CREATE TABLE users (
	uid			SERIAL	PRIMARY KEY,
	userid		TEXT UNIQUE,
	username	TEXT
);

CREATE TABLE solved (
	rid			SERIAL PRIMARY KEY,
	uid			SERIAL,
	cid			SERIAL,
	pid			SERIAL,
	lid			SERIAL,
	cputime		INTEGER,
	memory		INTEGER,
	codesize	INTEGER,
	datetime	TIMESTAMP
);

CREATE TABLE languages (
	lid		SERIAL	PRIMARY KEY,
	name	TEXT	UNIQUE
);

CREATE TABLE contests (
	cid			SERIAL PRIMARY KEY,
	contestid	TEXT UNIQUE,
	name		TEXT,
	begintime	TIMESTAMP,
	endtime		TIMESTAMP
);

CREATE TABLE problems (
	pid			SERIAL PRIMARY KEY,
	cid			SERIAL,
	problemid	TEXT UNIQUE,
	title		TEXT
);

CREATE OR REPLACE FUNCTION insert_user(id TEXT,name TEXT)
RETURNS INTEGER AS
$$
	DECLARE
		ret INTEGER;
	BEGIN
		INSERT INTO users(userid,username) VALUES(id,name) returning uid INTO ret;
		return ret;
	EXCEPTION WHEN unique_violation THEN
		SELECT uid FROM users WHERE userid=id INTO ret;
		RETURN ret;
	END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION insert_language(lname TEXT)
RETURNS INTEGER AS
$$
	DECLARE
		ret INTEGER;
	BEGIN
		INSERT INTO languages(name) VALUES(lname) returning lid INTO ret;
		return ret;
	EXCEPTION WHEN unique_violation THEN
		SELECT lid FROM languages WHERE name=lname INTO ret;
		RETURN ret;
	END;
$$
LANGUAGE plpgsql;

