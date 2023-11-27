drop table if exists loan;

CREATE TABLE loan (
    id SERIAL PRIMARY KEY,
    book_id INT NOT NULL,
    user_id TEXT NOT NULL,
    data_prestito TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_restituzione TIMESTAMP,
    data_scadenza TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP + interval '14 days')
);


