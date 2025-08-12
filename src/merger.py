import pandas as pd
from .utils import get_db_engine
import sys

if len(sys.argv) != 2:
    print("Usage: python merger.py <downstream_csv>")
    sys.exit(1)
downstream_file = sys.argv[1]

engine = get_db_engine()
api_results = pd.read_sql('SELECT * FROM runs', engine)
downstream = pd.read_csv(downstream_file)
merged = api_results.merge(downstream, on='transaction_id', how='left')
merged.to_csv('../outputs/e2e_results.csv', index=False)
merged.to_sql('runs', engine, if_exists='replace', index=False)
print("Merge complete!")