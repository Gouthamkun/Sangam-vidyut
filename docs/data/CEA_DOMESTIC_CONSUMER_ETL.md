# CEA Domestic Consumer ETL (Phase 4D.11A)

## 1. Provenance Metadata

**Document 1:**
*   **Publisher:** Central Electricity Authority (CEA)
*   **Document:** Status of Consumer Metering in the Country
*   **Publication Date:** 2024
*   **Reference Date:** 31st March 2024
*   **Table:** Annexure-V (Status of Consumer Metering in the Country)
*   **Raw Filename:** `cea_consumer_metering_31mar2024.pdf`
*   **SHA-256:** `c3eb685a18325b21f2a485c8ca37d04cea346a95c23ab49635ef08897b743543`
*   **Extraction Version:** Phase 4D.11A

**Document 2:**
*   **Publisher:** Central Electricity Authority (CEA)
*   **Document:** General Review 2024
*   **Publication Date:** 2024
*   **Reference Date:** 31st March 2024
*   **Raw Filename:** `cea_general_review_2024.pdf`
*   **SHA-256:** `f710de8ee99efb4ae7b3381b32089ae60d766b863d978bff38b4f6354d8dd801`
*   **Extraction Version:** Phase 4D.11A

## 2. Reconciling CEA Sources
*   **Consumer Metering Report:** Explicitly breaks down consumers by Urban/Rural and by Category (Domestic, Commercial, Industrial, Agriculture, etc.). The national `Grand Total` of all consumers is 341.8 million. The explicit sum of the `Domestic` category across all states yields approximately **267.2 million Domestic Consumers** as of 31st March 2024.
*   **General Review 2024:** Provides broad national totals and capacity generation metrics synchronized to the exact same reference date (31st March 2024).
*   **Reconciliation Status:** The two reports are perfectly synchronized temporally. The Consumer Metering Annexure-V is selected as the primary source for the denominator, as it provides the exact State/UT-wise breakdown for the specific `Domestic` consumer tariff category. No inter-report averaging is necessary or permitted.

## 3. Domestic Consumer Extraction Rules
The extraction scripts isolate the `Domestic` row for each `STATE/UTILITY` block in Annexure-V. The `TOTAL` column representing the sum of Urban and Rural consumer counts forms the exact demographic denominator for eligible residential grid connections in that state.
