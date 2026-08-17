# Base de Données — GEOS

## PostgreSQL 16

### Schéma Principal (14 tables)
```sql
provinces        → id, name, area_km2, population, literacy_rate, internet_pct, security_index
citizens         → id, name, province_id, status, satisfaction_score
companies        → id, name, sector, revenue, production_cost, tax_burden, admin_cost, corruption_cost
ministries       → id, name, budget, performance_score, corruption_risk
budgets          → id, ministry_id, year, allocated, spent, efficiency
resources        → id, name, type, annual_production_tons, market_value_per_ton, local_processing_pct
taxes            → id, name, type, base, rate, compliance_pct, estimated_revenue
projects         → id, name, type, budget, status, snn_contribution
infrastructures  → id, name, type, province_id, cost, status, beneficiaries
public_services  → id, name, province_id, quality_score, willingness_to_pay, actual_price, access_pct
contracts        → id, project_id, company_id, value, corruption_risk_score
payments         → id, contract_id, amount, date, anomaly_score
markets          → id, name, location, products, price, demand, supply
indicators       → id, name, value, unit, year, province_id
```

### Auth Tables (Keycloak + local)
```sql
users           → id, username, email, hashed_password, role, is_active, created_at
```

### Index
- `idx_provinces_name` UNIQUE
- `idx_users_username` UNIQUE
- `idx_payments_anomaly` → détection fraude
- `idx_projects_snn` → optimisation rapide
- `idx_resources_production` → NRV calcul
