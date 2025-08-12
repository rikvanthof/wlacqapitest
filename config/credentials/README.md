# Credentials Configuration

## Setup
1. Copy `secrets.csv.template` to `secrets.csv`
2. Replace placeholder values with your actual credentials
3. Never commit `secrets.csv` (it's gitignored)
4. Don't use this tool with production credentials

## Format
```csv
env,client_id,client_secret
dev,your-actual-client-id,your-actual-secret