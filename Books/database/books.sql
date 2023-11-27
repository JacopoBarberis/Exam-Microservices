drop table if exists item;
drop table if exists book;


create table book(
    id serial primary key,
    isbn varchar(255),
    title varchar(255),
    author varchar(255),
    genre varchar(255),
    publish_date int
);

create table item(
    id serial primary key,
    book_id int not null,
    isDisponibile boolean default True,
    stato_libro boolean default True,
    foreign key (book_id) references book(id)  
);