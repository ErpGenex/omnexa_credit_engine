# SAP Parity — omnexa_credit_engine

**SAP reference:** SAP FS-CML · **Family:** fs · **Target:** ≥95%

| # | Capability | Status | Evidence |
|---|------------|--------|----------|
| 1 | Contract / facility lifecycle | Implemented | DocTypes |
| 2 | Schedule / calc engine | Implemented | finance_engine bridge |
| 3 | GL posting matrix preview | Implemented | preview_gl_posting |
| 4 | Live JE posting (flag OFF default) | Implemented | fs_live_gl_posting |
| 5 | Regulatory dashboard API | Implemented | get_regulatory_dashboard |
| 6 | omnexa_finance_engine integration | Implemented | fs_parity_bridge |
| 7 | SAP parity GL test | Implemented | test_sap_parity_gl.py |
| 8 | Checklist score ≥95% | Implemented | SAP_PARITY_CHECKLIST |
| 9 | SAP HANA scale-out | N/A | MariaDB / bench stack |
| 10 | SAP STMS transport | N/A | Git + bench deploy |

**Metrics:** 16 DocTypes · 14 tests · 10 reports

**Checklist product score:** **95%** (signed omnexa_credit_engine)
