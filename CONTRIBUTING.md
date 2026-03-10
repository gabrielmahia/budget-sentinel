# Contributing to Budget Sentinel Kenya

Budget Sentinel is a civic accountability tool. We welcome contributions that
improve data accuracy, expand county coverage, or improve usability.

## How to contribute

- **Data error** — allocation or absorption figure is wrong: open a GitHub Issue
  with the correct figure and a link to the Controller of Budget source PDF.
- **Missing county quarter** — Controller of Budget has published data we haven't
  ingested yet: open a GitHub Issue with the report URL and quarter.
- **Bug report** — open a GitHub Issue with steps to reproduce.
- **Feature suggestion** — open a GitHub Issue describing the use case.

This repository does not accept Pull Requests modifying financial data without
a cited Controller of Budget source. Unverified figures will not be merged.

## Data standards

All allocation and absorption figures must be sourced from:
- Controller of Budget Annual County Budget Implementation Review Reports
- Controller of Budget Quarterly Implementation Reports
- URL: https://cob.go.ke/reports/

All records must include `source` and `verified` columns.
`verified = confirmed` requires a direct COB report citation.

## Contact

contact@aikungfu.dev
