# Module 6b — Two SQLite writers

I opened the same SQLite database in two Terminal windows. In Window 1,
I used BEGIN IMMEDIATE and increased the counter from 0 to 1. When I tried
to update it in Window 2, SQLite said `database is locked`.

I also tried COMMIT in Window 2 and got `no transaction is active`.
That helped me see that the transaction belonged to Window 1. After
committing there, I retried the update in Window 2. The final count was 2.

## What would change with a shared PostgreSQL server?

- Easier: My pod could connect to one shared database from different laptops.
- Harder: We'd need a working connection to the server and the right login.
- Failure: If the server process stopped, every connected client could lose
  access. In this exercise, SQLite opened a file directly on my Mac.