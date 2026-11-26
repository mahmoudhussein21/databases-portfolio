# Reflection 06b — Choosing a database for the job

## Take-away
I would check the query plan before assuming a query uses an index.
In my JSON test, two ways of reading the vendor gave different plans.

## What was good?
I saw SEARCH when the query used `json_extract` and SCAN when it used
`->>`. The plan showed me which version used the vendor index.

## What was difficult?
I typed COMMIT in the second Terminal window and got
`no transaction is active`. I had started the transaction in the first
window. Once I committed there, the second update worked and the count was 2.

## Exploration and show stoppers
The two-window exercise showed how SQLite makes writers take turns.
The key-value test gave me a different trade-off to think about.
Shelve read a little faster on my Mac, and SQLite wrote the batch much
faster. I chose SQLite for the dashboard sessions.

## Interaction with peers and instructors
I followed the course handout and ran the SQLite two-writer exercise
using two Terminal windows on my Mac.

## How did you verify AI suggestions?
I used ChatGPT for help with Terminal commands and organizing these
notes. I ran the exercises myself and checked the lock error, the final
count, both query plans, and the four timings against my Terminal output.

## Help and extra work
I saved the benchmark output with the module so I can check where the
numbers in my decision record came from.