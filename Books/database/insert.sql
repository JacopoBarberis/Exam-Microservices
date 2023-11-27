-- Inserisci un libro nella tabella "book"
INSERT INTO book(isbn, title, author, genre, publish_date)
VALUES ('1234567890', 'Harry Potter e la pietra filosofale', 'J.K. Rowling', 'Fantasy', 2001);

-- Inserisci un record nella tabella "item" facendo riferimento al libro appena inserito
INSERT INTO item(book_id)
VALUES (1);

-- Inserisci un altro libro nella tabella "book"
INSERT INTO book(isbn, title, author, genre, publish_date)
VALUES ('1234567891', 'Harry Potter e la camera dei segreti', 'J.K. Rowling', 'Fantasy', 2003);

-- Inserisci un record nella tabella "item" facendo riferimento al secondo libro
INSERT INTO item(book_id)
VALUES (2);
