# NL2SQL vs Cortex Analyst — Sigma DataTech Evaluation
Name: Aditya Sah
Date: 2026-05-25

## 5-Question Head-to-Head Results

| # | Question | Module 2 SQL Correct? | Cortex SQL Correct? | Module 2 Time | Cortex Time |
|---|----------|--------------------|---------------------|--------------|-------------|
| 1 | Total transaction count | YES | YES | ~3-5s | ~38.7s |
| 2 | Failed transaction count | YES | YES | ~3-5s | ~172.3s |
| 3 | Highest revenue merchant | YES | YES | ~3-5s | ~31.2s |
| 4 | Failure rate by payment method | YES | NO (syntax error) | ~3-5s | ~288.7s |
| 5 | Total revenue (COMPLETED filter) | YES | YES | ~3-5s | ~76.3s |

---

## Observations

### Where Module 2 NL2SQL was better:
- Much faster response time (3–5s vs up to 288s in Cortex)
- Strong reliability — all 5 queries executed successfully
- Built-in SQL validation blocked dangerous queries (e.g., DROP TABLE)
- No syntax errors observed
- Consistent execution and correct outputs across all queries

---

### Where Cortex Analyst was better:
- Cleaner architecture (no need to manually manage prompts)
- Centralized semantic model (YAML) improves maintainability
- No need for custom validator, executor, or prompt tuning
- Uses structured schema → reduces hallucination risk

---

## Key Issues Observed in Cortex

-  **Performance issue**: Very slow response times (30s–280s)
-  **SQL error** in Question 4:
  - `ELSE0` typo caused query failure
-  No validation layer → incorrect SQL reached execution
-  Less robust compared to controlled pipeline in Module 2

---

## Business Rule Accuracy

Question 5 is the critical test — revenue must only count COMPLETED transactions.

- Module 2:  Correctly used `CASE WHEN STATUS='COMPLETED'`
- Cortex:  Correctly used `WHERE STATUS = 'COMPLETED'`

 Both systems handled business logic correctly in this case.

---

## Key Differences

- Module 2 is **prompt-driven and fully controlled**
- Cortex is **YAML-driven and managed by Snowflake**
- Module 2 provides **better reliability + speed**
- Cortex provides **better scalability + maintainability**
- Cortex lacks validation → prone to execution errors
- Module 2 includes safety checks → production-safe

---

## Your Recommendation

**Recommended Approach: Hybrid (Module 2 NL2SQL + Cortex Analyst)**

**Reason:**

While Cortex Analyst simplifies setup and improves maintainability using a semantic model, it showed significant drawbacks in performance and reliability during testing, including slow response times and SQL errors. 

Module 2 NL2SQL pipeline, on the other hand, demonstrated faster execution, strong validation, and consistent correctness.

A hybrid approach is ideal:
- Use **Cortex Analyst** for standard self-serve analytics (scalable, low maintenance)
- Use **custom NL2SQL pipeline** for critical queries requiring validation, speed, and control

This balances **ease of use + production reliability**.