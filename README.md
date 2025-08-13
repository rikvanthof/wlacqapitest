# AcquiringAPI_Tester
Automates Worldline Acquiring API (v1.3.0) tests with CSV-driven one-shot/chained calls, delayed downstream merging, and E2E dashboard.

## Setup
1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate`
3. Install: `pip install -r requirements.txt`
4. Configure CSVs in `config/` (environments, cards, merchants, tests).
5. Run tests: `python -m src.main`
6. Merge: `python src/merger.py config/downstream.csv`
7. Dashboard: `python src/dashboard.py` (open http://localhost:8050)

## Structure
- `config/`: Input CSVs
- `src/`: Python modules
- `outputs/`: Results (CSVs, DB)
- `venv/`: Virtual environment