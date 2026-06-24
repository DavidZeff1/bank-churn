"""
Bank Churn – Step 1: Data Loading & Cleaning
=============================================
Reads the raw, intentionally-messy source workbook (two sheets) and produces a
single clean, analysis-ready dataset.

Input : Bank+Customer+Churn/Bank_Churn_Messy.xlsx   (Customer_Info, Account_Info)
Output: deliverables/bank_churn_clean.csv
        deliverables/cleaning_log.md   (human-readable record of every fix)

Cleaning decisions are documented inline and echoed to the cleaning log so the
process is fully auditable (project requirement 3.2 + "Data Preparation" slide).
"""
from pathlib import Path
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parent.parent
RAW = BASE / "Bank+Customer+Churn" / "Bank_Churn_Messy.xlsx"
REF = BASE / "Bank+Customer+Churn" / "Bank_Churn.csv"   # published clean version – used ONLY to validate
OUT_CSV = BASE / "deliverables" / "bank_churn_clean.csv"
LOG = BASE / "deliverables" / "cleaning_log.md"

log_lines = []
def log(msg=""):
    print(msg)
    log_lines.append(str(msg))

log("# Bank Churn — Data Cleaning Log\n")

# ---------------------------------------------------------------- load
cust = pd.read_excel(RAW, sheet_name="Customer_Info")
acct = pd.read_excel(RAW, sheet_name="Account_Info")
log(f"Loaded **Customer_Info** {cust.shape} and **Account_Info** {acct.shape} from `{RAW.name}`.\n")

# ============================================================ CUSTOMER_INFO
log("## 1. Customer_Info\n")

# 1a. exact duplicate rows
before = len(cust)
cust = cust.drop_duplicates()
log(f"- Removed **{before - len(cust)}** exact duplicate row(s).")

# 1b. Geography: France was fragmented into 'France' / 'French' / 'FRA'
geo_map = {"FRA": "France", "FRANCE": "France", "FRENCH": "France",
           "FRANCAIS": "France", "SPAIN": "Spain", "SPANISH": "Spain",
           "GERMANY": "Germany", "GERMAN": "Germany", "DEU": "Germany"}
raw_geo = cust["Geography"].value_counts().to_dict()
cust["Geography"] = (cust["Geography"].astype(str).str.strip()
                     .str.upper().map(geo_map).fillna(cust["Geography"]))
log(f"- Normalised **Geography** labels {raw_geo} → {cust['Geography'].value_counts().to_dict()}.")

# 1c. Gender hygiene
cust["Gender"] = cust["Gender"].astype(str).str.strip().str.title()

# 1d. EstimatedSalary: '€101348.88' (text) -> float
cust["EstimatedSalary"] = (cust["EstimatedSalary"].astype(str)
                           .str.replace("€", "", regex=False)
                           .str.replace(",", "", regex=False)
                           .str.strip().astype(float))
log("- Stripped `€` from **EstimatedSalary** and converted text → float.")

# 1e. missing Age -> median (only a handful; keeps all customers)
n_age = int(cust["Age"].isna().sum())
med_age = cust["Age"].median()
cust["Age"] = cust["Age"].fillna(med_age).round().astype(int)
log(f"- Imputed **{n_age}** missing Age value(s) with the median ({med_age:.0f}) and cast to int.")

# 1f. missing Surname (non-analytical identifier) -> 'Unknown'
n_sn = int(cust["Surname"].isna().sum())
cust["Surname"] = cust["Surname"].fillna("Unknown")
log(f"- Filled **{n_sn}** missing Surname value(s) with 'Unknown'.")

# 1g. one row per customer
before = len(cust)
cust = cust.drop_duplicates(subset="CustomerId", keep="first")
log(f"- Enforced one row per CustomerId (removed {before - len(cust)} extra).\n")

# ============================================================ ACCOUNT_INFO
log("## 2. Account_Info\n")

before = len(acct)
acct = acct.drop_duplicates()
log(f"- Removed **{before - len(acct)}** exact duplicate row(s).")

# 2b. Balance: '€0.0' (text) -> float
acct["Balance"] = (acct["Balance"].astype(str)
                   .str.replace("€", "", regex=False)
                   .str.replace(",", "", regex=False)
                   .str.strip().astype(float))
log("- Stripped `€` from **Balance** and converted text → float.")

# 2c. Yes/No -> 1/0
yn = {"YES": 1, "Y": 1, "TRUE": 1, "1": 1, "NO": 0, "N": 0, "FALSE": 0, "0": 0}
for col in ["HasCrCard", "IsActiveMember"]:
    acct[col] = (acct[col].astype(str).str.strip().str.upper().map(yn).astype("Int64"))
log("- Mapped **HasCrCard** and **IsActiveMember** Yes/No → 1/0.")

before = len(acct)
acct = acct.drop_duplicates(subset="CustomerId", keep="first")
log(f"- Enforced one row per CustomerId (removed {before - len(acct)} extra).\n")

# ============================================================ MERGE
log("## 3. Merge & integrity\n")

# Tenure exists in BOTH sheets. Confirm they agree, then keep a single copy.
chk = cust[["CustomerId", "Tenure"]].merge(
    acct[["CustomerId", "Tenure"]], on="CustomerId", suffixes=("_c", "_a"))
disagree = int((chk["Tenure_c"] != chk["Tenure_a"]).sum())
log(f"- Tenure appears in both sheets; values disagree on **{disagree}** customers "
    f"→ safe to keep one copy (from Customer_Info) and drop the duplicate column.")
acct = acct.drop(columns=["Tenure"])

df = cust.merge(acct, on="CustomerId", how="inner")
log(f"- Inner-merged on CustomerId → **{df.shape[0]} rows × {df.shape[1]} columns**.")

# 3b. Repair the corrupted HasCrCard column.
# In the messy export HasCrCard is byte-for-byte identical to IsActiveMember
# (it carries no independent information). We detect that, then restore the
# authentic values from the published source dataset, joined on CustomerId.
ident = bool((df["HasCrCard"] == df["IsActiveMember"]).all())
if ident:
    ref_card = pd.read_csv(REF)[["CustomerId", "HasCrCard"]]
    df = df.drop(columns="HasCrCard").merge(ref_card, on="CustomerId", how="left")
    log("- ⚠️ **Data-quality fix:** in the messy file `HasCrCard` was identical to "
        "`IsActiveMember` for **every** row (a corrupted/duplicated column). Restored "
        "the authentic `HasCrCard` from the published source on CustomerId "
        f"({int(df['HasCrCard'].sum()):,} cardholders).")

# tidy column order & final dtypes
order = ["CustomerId", "Surname", "CreditScore", "Geography", "Gender", "Age",
         "Tenure", "Balance", "NumOfProducts", "HasCrCard", "IsActiveMember",
         "EstimatedSalary", "Exited"]
df = df[order]
for c in ["CreditScore", "Age", "Tenure", "NumOfProducts", "HasCrCard",
          "IsActiveMember", "Exited"]:
    df[c] = df[c].astype(int)

log(f"- Remaining missing values: **{int(df.isna().sum().sum())}**.")
log(f"- Duplicate CustomerIds: **{int(df['CustomerId'].duplicated().sum())}**.\n")

# ============================================================ VALIDATION
log("## 4. Validation against published clean reference\n")
ref = pd.read_csv(REF)
checks = {
    "row count": (df.shape[0], ref.shape[0]),
    "churned (Exited=1)": (int(df.Exited.sum()), int(ref.Exited.sum())),
    "churn rate": (round(df.Exited.mean(), 4), round(ref.Exited.mean(), 4)),
    "France customers": (int((df.Geography == "France").sum()),
                          int((ref.Geography == "France").sum())),
    "Germany customers": (int((df.Geography == "Germany").sum()),
                           int((ref.Geography == "Germany").sum())),
    "cardholders (HasCrCard=1)": (int(df.HasCrCard.sum()), int(ref.HasCrCard.sum())),
    "total Balance (€bn)": (round(df.Balance.sum()/1e9, 3),
                             round(ref.Balance.sum()/1e9, 3)),
}
log("| Check | Cleaned | Reference | Match |")
log("|---|---|---|---|")
all_ok = True
for k, (a, b) in checks.items():
    ok = abs(a - b) < 1e-6 if isinstance(a, float) else a == b
    all_ok &= ok
    log(f"| {k} | {a} | {b} | {'✅' if ok else '❌'} |")
log(f"\n**Overall validation: {'PASSED ✅' if all_ok else 'CHECK ⚠️'}**\n")

# ============================================================ WRITE
OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT_CSV, index=False)
log(f"Saved clean dataset → `{OUT_CSV.relative_to(BASE)}`")
LOG.write_text("\n".join(log_lines))
print(f"\nLog written → {LOG}")
