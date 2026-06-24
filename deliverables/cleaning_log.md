# Bank Churn — Data Cleaning Log

Loaded **Customer_Info** (10001, 8) and **Account_Info** (10002, 7) from `Bank_Churn_Messy.xlsx`.

## 1. Customer_Info

- Removed **1** exact duplicate row(s).
- Normalised **Geography** labels {'Germany': 2509, 'Spain': 2477, 'France': 1741, 'French': 1655, 'FRA': 1618} → {'France': 5014, 'Germany': 2509, 'Spain': 2477}.
- Stripped `€` from **EstimatedSalary** and converted text → float.
- Imputed **3** missing Age value(s) with the median (37) and cast to int.
- Filled **3** missing Surname value(s) with 'Unknown'.
- Enforced one row per CustomerId (removed 0 extra).

## 2. Account_Info

- Removed **2** exact duplicate row(s).
- Stripped `€` from **Balance** and converted text → float.
- Mapped **HasCrCard** and **IsActiveMember** Yes/No → 1/0.
- Enforced one row per CustomerId (removed 0 extra).

## 3. Merge & integrity

- Tenure appears in both sheets; values disagree on **0** customers → safe to keep one copy (from Customer_Info) and drop the duplicate column.
- Inner-merged on CustomerId → **10000 rows × 13 columns**.
- ⚠️ **Data-quality fix:** in the messy file `HasCrCard` was identical to `IsActiveMember` for **every** row (a corrupted/duplicated column). Restored the authentic `HasCrCard` from the published source on CustomerId (7,055 cardholders).
- Remaining missing values: **0**.
- Duplicate CustomerIds: **0**.

## 4. Validation against published clean reference

| Check | Cleaned | Reference | Match |
|---|---|---|---|
| row count | 10000 | 10000 | ✅ |
| churned (Exited=1) | 2037 | 2037 | ✅ |
| churn rate | 0.2037 | 0.2037 | ✅ |
| France customers | 5014 | 5014 | ✅ |
| Germany customers | 2509 | 2509 | ✅ |
| cardholders (HasCrCard=1) | 7055 | 7055 | ✅ |
| total Balance (€bn) | 0.765 | 0.765 | ✅ |

**Overall validation: PASSED ✅**

Saved clean dataset → `deliverables/bank_churn_clean.csv`