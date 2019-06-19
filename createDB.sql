CREATE DOMAIN ACTION_TYPE AS varchar
CHECK(
    VALUE IN ('support', 'protest')
     );

CREATE DOMAIN VOTE_TYPE AS varchar
CHECK
    (
    VALUE IN ('Y', 'N')
    );


CREATE TABLE Allid (
	Id INTEGER PRIMARY KEY
);

CREATE TABLE Projects (
	Id INTEGER PRIMARY KEY REFERENCES Allid(Id),
  authority INTEGER REFERENCES Allid(Id)
);

CREATE TABLE Members (
	Id INTEGER PRIMARY KEY REFERENCES Allid(Id),
	password TEXT NOT NULL,
	last_activity INTEGER,
	Uppvote INTEGER,
  Downvote INTEGER
);

CREATE TABLE Actions (
	Id INTEGER PRIMARY KEY REFERENCES Allid(Id),
  Type ACTION_TYPE,
  Id_member INTEGER REFERENCES Members(Id),
  Id_project INTEGER REFERENCES Projects(Id),
  Uppvote INTEGER,
  Downvote INTEGER
);

CREATE TABLE Leaders (
	Id INTEGER PRIMARY KEY REFERENCES Members(Id)
);

CREATE TABLE Votes (
	Id_member INTEGER REFERENCES Members(Id),
  Id_action INTEGER REFERENCES Actions(Id),
	vote VOTE_TYPE,
  PRIMARY KEY (Id_member, Id_action)
);

CREATE USER app with ENCRYPTED PASSWORD 'qwerty';
GRANT CONNECT ON DATABASE student TO app;

GRANT INSERT, UPDATE, SELECT ON Actions, Members, Allid, Votes, Projects, Leaders TO app;