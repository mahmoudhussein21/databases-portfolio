# Round 5 — Price of copying data

| Measurement | Normalized design | Denormalized report |
|---|---:|---:|
| Rows changed when `cnc-02` moves | 1 | 4,000 |
| Data table bytes (`dbstat`; indexes excluded) | 4,071,424 bytes (3,976.0 KiB) | 11,091,968 bytes (10,832.0 KiB) |
| Extra index bytes | 4,096,000 bytes (4,000.0 KiB) | 2,990,080 bytes (2,920.0 KiB) |

On this generated dataset, 400 jobs use `cnc-02`, and each job has ten part links, giving **4,000 report rows** for that machine. One machine row represents the same site fact in 3NF.

**The trade-off:** a reporting copy may make frequent reads simpler, but every update to shared facts must refresh many copies. The report is not the authoritative record. Table bytes in the first comparison exclude indexes; index storage is shown separately rather than hidden.

The query-plan comparison with and without `ix_report_machine` is in `query_plans.txt`. The index was restored after the experiment.
