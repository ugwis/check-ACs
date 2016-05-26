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
