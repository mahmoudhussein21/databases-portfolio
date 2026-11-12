# Optional Task 5 — BEFORE versus AFTER INSERT

I tested the same vibration-alarm logic with a `BEFORE INSERT` trigger and an `AFTER INSERT` trigger. Both created one alarm when a valid high vibration reading was inserted. The difference was *when the reading became visible inside the trigger*: with `BEFORE`, the database table did not yet contain it; with `AFTER`, it did.

I also attempted an invalid reading of `9000`. It was rejected by the `CHECK` constraint, and neither trigger left an extra alarm. This is because the failed SQL statement was rolled back.

`AFTER INSERT` is a clear default for creating an alarm linked to a successfully inserted reading. For input validation, a `BEFORE` trigger can still be appropriate if the rule needs more than a `CHECK` can express.

The code is in [optional_task5.py](optional_task5.py) and the checked results are in [task5_results.txt](task5_results.txt).
