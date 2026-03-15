# 🛡️ Hesabu — County Budget Intelligence Kenya

County development fund absorption tracker — powered by Controller of Budget data.

[![Live App](https://img.shields.io/badge/Live%20App-budget--sentinel.streamlit.app-FF4B4B?logo=streamlit)](https://budget-sentinel.streamlit.app)
[![CI](https://github.com/gabrielmahia/budget-sentinel/actions/workflows/ci.yml/badge.svg)](https://github.com/gabrielmahia/budget-sentinel/actions)
[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC_BY--NC--ND_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)

> **Hesabu** /hesɑːbu/ — *Kiswahili*: accounts, arithmetic, reckoning.

---

Kenya's 47 county governments collectively manage **KES 400+ billion** annually in
devolved funds. The Controller of Budget publishes absorption rates for every county
every year. Budget Sentinel turns those PDFs into a searchable, comparable dashboard
that answers: **Where are development funds going unspent — and by how much?**

## What it tracks

| Metric | Source |
|--------|--------|
| Development fund absorption rate | COB Annual County Budget Implementation Review |
| Unspent development funds (KES) | Derived from COB data |
| Health, education, infrastructure as % of total | COB sector breakdowns |
| Per-capita allocation by county | COB × KNBS 2019 census |
| County own-revenue vs national transfer dependence | COB revenue data |

## Audience

- **Civil society / NGO monitors** — track county performance on key sectors
- **Journalists** — identify counties with persistent low absorption for investigation
- **County assembly members** — compare peers and benchmark performance
- **Diaspora Kenyans** — understand where their home county's resources go
- **Researchers** — download clean, cited COB data for policy analysis

## Trust principles

- All figures are from **COB published reports** (public domain). Source column in every CSV.
- Low absorption is a **factual observation**, not an accusation. Multiple causes exist.
- This tool does not name individuals or make forensic accounting conclusions.
- Verify originals at [cob.go.ke](https://cob.go.ke/reports/county-budget-implementation-review/).

## Local setup

```bash
git clone https://github.com/gabrielmahia/budget-sentinel.git
cd budget-sentinel
pip install -r requirements.txt
streamlit run app.py
```

## Data

`data/allocations/county_budgets_fy2223.csv` — 46 counties, FY 2022/23.
All figures in KES millions. Each row has `source` and `verified` columns.

Annual updates will be added as COB publishes new reports.

## IP & Collaboration

**Owner:** Gabriel Mahia | contact@aikungfu.dev  
**License:** CC BY-NC-ND 4.0 — share with attribution, no commercial use, no derivatives.  
Not affiliated with the Controller of Budget or any county government.

## Security

See [SECURITY.md](SECURITY.md). Report errors to contact@aikungfu.dev — do not open public issues.
---

## Portfolio

Part of a suite of civic and community tools built by [Gabriel Mahia](https://github.com/gabrielmahia):

| App | What it does |
|-----|-------------|
| [🌊 Mafuriko](https://floodwatch-kenya.streamlit.app) | Flood risk & policy enforcement tracker — Kenya |
| [💧 WapiMaji](https://wapimaji.streamlit.app) | Water stress & drought intelligence — 47 counties |
| [🏛️ Macho ya Wananchi](https://civic-decoder.streamlit.app) | MP voting records, CDF spending, bill tracker |
| [🌾 JuaMazao](https://mazao-intel.streamlit.app) | Live food price intelligence for smallholders |
| [🏦 ChaguaSacco](https://sacco-scout.streamlit.app) | Compare Kenya SACCOs on dividends & loan rates |
| [🛡️ Hesabu](https://budget-sentinel.streamlit.app) | County budget absorption tracker |
| [🗺️ Hifadhi](https://hifadhi.streamlit.app) | Riparian encroachment & Water Act compliance map |
| [💰 Hela](https://hela.streamlit.app) | Chama management for the 21st century |
| [💸 TumaPesa](https://remit-lens.streamlit.app) | True cost remittance comparison — diaspora to Kenya |
| [📊 Msimamo](https://quantum-maestro.streamlit.app) | Macro risk & trade intelligence terminal |
| [🦁 Dagoretti](https://dagoretti-community-hub.streamlit.app) | Alumni atlas & community hub for Dagoretti High |
| [⛪ Jumuia](https://catholicparishsteward.streamlit.app) | Catholic parish tools — church finder, pastoral care |

