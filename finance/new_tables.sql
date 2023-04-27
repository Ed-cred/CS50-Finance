CREATE TABLE purchase
(purchaseid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
symbol TEXT NOT NULL,
stock_price INTEGER NOT NULL,
date_of_purchase DATE NOT NULL,
shares INTEGER NOT NULL,
personid INTEGER REFERENCES users(id));


ALTER TABLE purchase
ADD shares INTEGER;

ALTER TABLE purchase
ALTER COLUMN personid