# HCES 2023–24 VARIABLE MAPPING & INSPECTION REPORT (PHASE 4D.2)

## 1. Dataset Overview
The Household Consumption Expenditure Survey (HCES) 2023-24 provides high-resolution microdata on Indian household consumption, demographics, and energy use. The raw data package is located in `data/raw/households/hces_2023_24/` and comprises 14 multi-gigabyte JSON files mapping to specific survey levels and sections.

**Total Households Sampled:** 261,953
**Status:** UNTOUCHED / INSPECTED VIA STREAMING

## 2. Level Inventory & Representation
| Level | Section | Unit of Observation | Key Fields | Record Count | Sangam Relevance | Recommended Handling |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **01** | Sec 1 & 1.1 | Household | Identification, Multiplier | ~261k | Master Frame | Merge 1-to-1 |
| **02** | Sec 3 | Person | Person_Serial_No, Age, Gender | ~1.1M | Demographics | Aggregate to HH / Ignore |
| **03** | Sec 3 (HH) | Household | HH_Size, Type_of_Dwelling, Energy_Source_Lighting | ~261k | High (Dwelling, Access) | Merge 1-to-1 as Core |
| **04** | Sec 4.1 | Household | Ration access, Online food | ~261k | Low | Ignore |
| **05** | Sec 5 & 6 | Item (Food) | Item_Code, Qty, Value | Huge (6.8GB) | Low | Ignore |
| **06** | Sec 7 | Item (Fuel/Light) | Item_Code, Qty, Value | Huge | High (Electricity Cost) | Filter for Electricity Item_Code, aggregate to HH |
| **07** | Sec 4.2 | Household | Free_electricity, Subsidies | ~261k | High (Policy Context) | Merge 1-to-1 |
| **08** | Sec 8.1 | Item (Clothing) | Item_Code, Qty, Value | Huge | Low | Ignore |
| **09** | Sec 9,10,11 | Item (Misc) | Item_Code, Value | Huge (3.5GB) | Low | Ignore |
| **10** | Sec 12 | Item | Item_Code, Qty, Value | Large | Low | Ignore |
| **12** | Sec 13 | Item | ITEM_CODE, Qty, Value | Huge | Low | Ignore |
| **13** | Sec 14 | Item (Durables) | ITEM_CODE, Purchase_Value | 2.8GB | High (Appliance Proxy) | Filter for AC/White Goods |
| **14** | Sec A1, B1, C1 | Item | ITEM_CODE, VALUE_RS | 3.4GB | Low | Ignore |
| **15** | Sec 1.1, A2 | Household | MONTHLY_CONSUMPTION_EXP | ~261k | High (Income Proxy) | Merge 1-to-1 |

## 3. Linking Structure
**Household Identification Key:**
A unique household is identified by the composite key of:
`FSU_Serial_No` + `Second_Stage_Stratum_No` + `Sample_Household_No`.
*(Additional contextual keys like `State`, `Sector`, `NSS_Region`, `District`, `Stratum`, `Sub_stratum`, `Panel`, `Sub_sample` are duplicated across all levels).*

**Item/Person Linking:**
Levels 02 (Persons) and 05-14 (Items) represent a one-to-many relationship with the Household Master. They must be grouped/filtered by the Household Identification Key before merging.

## 4. Household Master-Level Recommendation
**Recommendation:** **Level 03** should be treated as the substantive Household Master, joined 1-to-1 with **Level 01** (for base identifiers) and **Level 15** (for aggregate MPCE).

## 5. ConsumerAgent Variable Mapping
### A. Geographic Context
- **State:** `State` (Level 01/03) - Needs mapping to standard state abbreviations using `tabulation_state_code.xlsx`.
- **Urban/Rural:** `Sector` (Level 01/03) - Code 1=Rural, 2=Urban.
- **District:** `District` (Level 01/03) - Directly usable for spatial mapping.

### B. Household Structure
- **Household Size:** `HH_Size_FDQ` (Level 03).

### C. Economic Variables (Income Proxy)
- **Direct Income:** *NOT AVAILABLE.* HCES is a consumption survey.
- **Proxy:** `MONTHLY_CONSUMPTION_EXP` (Level 15). Dividing this by `HH_Size_FDQ` yields MPCE (Monthly Per Capita Consumption Expenditure), the official proxy for income deciles.

### D. Housing Variables
- **Dwelling Exists:** `Dwelling_Unit_Exists` (Level 03).
- **Dwelling Type (Roof Proxy):** `Type_of_Dwelling_Unit` (Level 03). Proxies Kachha vs Pucca for structural rooftop solar suitability.

### E. Energy Variables
- **Electricity Access:** `Energy_Source_Lighting` (Level 03).
- **Free Electricity Context:** `Free_electricity` (Level 07).
- **Electricity Expenditure:** `Total_Consumption_Value` in **Level 06** (Filtered where `Item_Code` = Electricity).

### F. Durable Goods (Proxy for Load)
- **AC/High-Load Appliance Ownership:** Extracted from **Level 13** (Section 14 Durables) by filtering for specific appliance `ITEM_CODE`s.

### G. Survey Weights
- **Field:** `Multiplier` (Present in all levels).
- **Role:** Crucial for translating the 261k sample into a representative Indian population (~300M households) during the statistical KDE generation. Must divide by 100 per official NSSO methodology.

## 6. Memory/Performance Assessment
- **Total Raw Size:** ~20 GB JSON.
- **Strategy:** DO NOT use `pandas.read_json` on Levels 05, 06, 09, 13, 14. 
- **Recommended ETL:** 
  1. Load Levels 01, 03, 07, 15 (all ~250MB - 500MB) directly using pandas. Merge on HH keys.
  2. Stream process Level 06 (Fuel/Light) using `ijson` or chunked reading, keeping ONLY records where `Item_Code` corresponds to Electricity. Aggregate to HH level.
  3. Stream process Level 13 (Durables), filtering for target appliances (AC/Fridge), flagging ownership.
  4. Merge aggregated item metrics into the master HH dataframe.

## 7. Scientific Safety & Model Compatibility Check
- **Leakage Risk:** `MONTHLY_CONSUMPTION_EXP` inherently includes the cost of electricity. If a household already has solar (post-treatment), their MPCE might drop artificially. We must flag households where `Energy_Source_Lighting` = Solar (if available) to avoid calibration bias.
- **ABM Compatibility:** The ConsumerAgent currently relies on an abstract 0-1 `income` percentile. The MPCE distribution will perfectly supply a CDF to map real households onto this 0-1 percentile.

## 8. Final Recommendation & Next Steps
- **Required Levels for ETL:** Level 03 (Core), Level 15 (MPCE), Level 06 (Electricity Expenditure), Level 07 (Policy).
- **Unavailable Variables:** True Income, True Roof Area, Direct Social Network Edges.
- **Next Step:** Authorize the creation of `scripts/data/process_hces_household_master.py` to execute the memory-safe ETL joining Levels 03, 15, and 07, without modifying the ABM.

STATUS: **PHASE 4D.2 = INSPECTION COMPLETE / AWAITING REVIEW**
