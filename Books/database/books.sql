drop table if exists item;
drop table if exists book;


create table book(
    id serial primary key,
    isbn varchar(255),
    titolo varchar(255),
    autore varchar(255),
    genere varchar(255),
    anno int
);

create table item(
    id serial primary key,
    book_id int not null,
    isDisponibile boolean default True,
    stato_libro boolean default True,
    foreign key (book_id) references book(id)  
);