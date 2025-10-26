-- This script is used to initialize the local test database.
-- It is NOT used directly on the production server,
-- but it is still useful as a reference.

CREATE TABLE IF NOT EXISTS users (
  uid INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  salt TEXT NOT NULL,
  role INTEGER NOT NULL,
  fullname TEXT NOT NULL,
  gender INTEGER NOT NULL DEFAULT 0,
  prefs TEXT NOT NULL DEFAULT '0'
);

-- uid: 1
-- username: yash
-- password: narayan
-- role: admin
INSERT OR IGNORE INTO users (uid, username, role, fullname, salt, password)
  VALUES (1, 'yash', 0, 'yash', '', '832a1f2e1e2e3a33332e972391413e336c534f3a390423b289296a58bd27a3ecf2457ca88fbf65bb58fb39b50df1f8485f478c1bb2befdde60c29b0692f826c4');

-- uid: 2
-- username: daniel
-- password: li
-- role: user
INSERT OR IGNORE INTO users (uid, username, role, fullname, salt, password)
  VALUES (2, 'daniel', 1, 'daniel', '', '3a72d4f3fd7dc2a24deb1de1333bf79e49036de56933c21a3910055e742d833edd593ec3aab724fe855404a42724e3cac64f962fe005c868f171e2957a5a81d0');
