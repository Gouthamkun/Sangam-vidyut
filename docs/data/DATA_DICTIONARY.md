# DATA DICTIONARY: SANGAM VIDYUT INDIA CALIBRATION

## Household Persona Variables
| Variable | Type | Source | Description | ABM Mapping |
| :--- | :--- | :--- | :--- | :--- |
| `state_id` | String | NSSO/NFHS | Standardized state abbreviation (e.g., UP, MH). | Spatial clustering |
| `urban_rural` | Boolean | NSSO/NFHS | 1 = Urban, 0 = Rural | Topology density |
| `mpce_decile` | Integer | NSSO CES | Monthly Per Capita Consumption Expenditure decile (1-10). | `ConsumerAgent.income` |
| `home_owner` | Boolean | NFHS-5 | 1 = Owns dwelling, 0 = Rents/Other | `ConsumerAgent.home_owner` |
| `roof_suitability` | Boolean | NFHS-5 | 1 = Pucca house, 0 = Kachha house | Suitability filter |

## Policy & Economic Variables
| Variable | Type | Source | Description | ABM Mapping |
| :--- | :--- | :--- | :--- | :--- |
| `policy_id` | String | MNRE | Unique identifier for subsidy scheme (e.g., PM_SURYA_GHAR_2024). | `GovernmentAgent` tracking |
| `subsidy_amount_per_kw` | Float | MNRE | Subsidy provided per kW of installed capacity (₹). | `GovernmentAgent.base_subsidy` |
| `benchmark_cost_per_kw` | Float | MNRE/CERC | Standardized installation cost per kW (₹). | `IndustryAgent.base_price` |

## Energy & Environment Variables
| Variable | Type | Source | Description | ABM Mapping |
| :--- | :--- | :--- | :--- | :--- |
| `effective_tariff` | Float | SERC | Average cost per kWh for residential consumer (₹/kWh). | Affordability scaling |
| `grid_emission_factor` | Float | CEA | tCO2 per MWh generated in the regional grid. | `EnvironmentAgent.co2_reduction` |

## Calibration Targets
| Variable | Type | Source | Description | ABM Mapping |
| :--- | :--- | :--- | :--- | :--- |
| `observed_installations` | Integer | MNRE | Total residential rooftop installations by state/year. | Compare vs `new_adoptions` |
| `installed_capacity_mw` | Float | MNRE | Total MW installed. | Compare vs `adoptions * avg_system_size` |
