create table if not exists users
(
    id           SERIAL PRIMARY KEY,
    email        TEXT    NOT NULL UNIQUE,
    password     TEXT    NOT NULL,
    active       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMP        DEFAULT current_timestamp,
    activated_at TIMESTAMP
);

create table if not exists tokens
(
    id         serial PRIMARY KEY,
    token      text      NOT NULL,
    user_id    integer   NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    created_at timestamp NOT NULL DEFAULT current_timestamp
);

create table if not exists guestbook
(
    id         serial PRIMARY KEY,
    message    text      NOT NULL,
    user_id    integer   NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    private    boolean   NOT NULL DEFAULT false,
    created_at timestamp NOT NULL DEFAULT current_timestamp,
    updated_at  timestamp
);

create table if not exists upvotes
(
    id         serial PRIMARY KEY,
    user_id    integer   NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    message_id integer   NOT NULL REFERENCES guestbook (id) ON DELETE CASCADE,
    created_at timestamp NOT NULL DEFAULT current_timestamp
);

create or replace view top_messages as
select g.id, g.message, count(u.id) as upvotes
from guestbook as g
         left join upvotes u on g.id = u.message_id
where private = false
group by g.id
order by upvotes desc
limit 10;

