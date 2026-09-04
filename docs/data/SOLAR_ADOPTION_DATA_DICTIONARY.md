# Solar Adoption Data Dictionary (Phase 4D.5)

This dictionary explicitly distinguishes the varying metrics encountered in official MNRE and parliamentary datasets.

| Metric | Definition | Context | Unit |
| :--- | :--- | :--- | :--- |
| **Installed Capacity** | The total rated electrical output capacity (invertor/panel limits). | Found in historical UQ 1936. This is *not* a household count, and often blends C&I and residential rooftops. | MW |
| **Residential Consumers** | Distinct physical households connected to the grid with a rooftop solar system. | This is the primary ABM target equivalent to `agent.adopted = True`. | Count |
| **Residential Installations** | Synonymous with Residential Consumers in PM Surya Ghar (UQ 1698). Represents completed, commissioned systems. | The primary outcome metric for PM-SGMBY progress. | Count |
| **Households** | In UQ 1698, this denotes "Households (Nos.)" which represents distinct beneficiary households who received subsidies/installations. Often equal or close to installations. | Beneficiary count. | Count |
| **Applications** | Registrations submitted on the national portal. | Represents *intent* or *demand*, not completed adoption. (Not present in UQ 1698 Annexure). | Count |
| **CFA Released** | Central Financial Assistance (Subsidy) disbursed directly into the consumer's bank account. | Fiscal output. | ₹ Crores |
