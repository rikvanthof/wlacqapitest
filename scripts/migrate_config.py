"""Migrate existing config to new structured approach"""

import shutil
import os
import pandas as pd
from pathlib import Path

def migrate_config():
    """Migrate existing flat config to structured approach"""
    
    print("🚀 Starting configuration migration...")
    
    # Create new directories
    directories = [
        "config/static",
        "config/credentials", 
        "config/test_suites",
        "config/test_suites/custom"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")
    
    # Move static configuration files
    static_files = [
        'cards.csv', 
        'merchants.csv', 
        'address.csv', 
        'networktoken.csv', 
        'threeddata.csv'
    ]
    
    for file in static_files:
        old_path = f"config/{file}"
        new_path = f"config/static/{file}"
        
        if os.path.exists(old_path):
            shutil.move(old_path, new_path)
            print(f"📁 Moved {file} → static/{file}")
        else:
            print(f"⚠️  File not found: {old_path}")
    
    # Handle environments.csv (needs manual splitting)
    env_file = "config/environments.csv"
    if os.path.exists(env_file):
        print(f"\n🔐 Processing {env_file}...")
        try:
            df = pd.read_csv(env_file)
            
            # Create public environments file (without credentials)
            public_cols = [col for col in df.columns 
                         if col not in ['client_id', 'client_secret']]
            public_df = df[public_cols]
            public_df.to_csv("config/static/environments.csv", index=False)
            print("✅ Created config/static/environments.csv (public)")
            
            # Create credentials file (private)
            if 'client_id' in df.columns and 'client_secret' in df.columns:
                cred_cols = ['env', 'client_id', 'client_secret']
                cred_df = df[cred_cols]
                cred_df.to_csv("config/credentials/secrets.csv", index=False)
                print("🔐 Created config/credentials/secrets.csv (private)")
            else:
                print("⚠️  No credentials found in environments.csv")
            
            # Keep original as backup
            shutil.move(env_file, f"{env_file}.backup")
            print(f"📦 Backed up original as {env_file}.backup")
            
        except Exception as e:
            print(f"❌ Error processing environments.csv: {e}")
            print("💡 You may need to manually split this file")
    
    # Move test files to test_suites
    test_files = ['tests.csv']
    for file in test_files:
        old_path = f"config/{file}"
        
        if os.path.exists(old_path):
            # Rename tests.csv to smoke_tests.csv for better organization
            new_name = "smoke_tests.csv" if file == "tests.csv" else file
            new_path = f"config/test_suites/{new_name}"
            
            shutil.move(old_path, new_path)
            print(f"📋 Moved {file} → test_suites/{new_name}")
            
            # Add tags column if it doesn't exist
            add_tags_column(new_path)
        else:
            print(f"⚠️  File not found: {old_path}")
    
    # Create .gitignore entries
    create_gitignore_entries()
    
    print("\n✅ Migration completed!")
    print("\n📋 Next steps:")
    print("1. Verify config/static/environments.csv has correct public data")
    print("2. Verify config/credentials/secrets.csv has correct credentials")
    print("3. Add tags to config/test_suites/smoke_tests.csv")
    print("4. Commit changes to feature/config-enhancement branch")
    print("5. Add config/credentials/ to your main .gitignore")

def add_tags_column(csv_path):
    """Add tags and defer_execution columns to test CSV if they don't exist"""
    try:
        df = pd.read_csv(csv_path)
        modified = False
        
        if 'tags' not in df.columns:
            df['tags'] = ''  # Empty string for now
            modified = True
            print(f"➕ Added 'tags' column to {csv_path}")
        
        if 'defer_execution' not in df.columns:
            df['defer_execution'] = None  # Null for immediate execution
            modified = True
            print(f"➕ Added 'defer_execution' column to {csv_path}")
        
        if modified:
            df.to_csv(csv_path, index=False)
            print(f"💾 Updated {csv_path} with new columns")
            
    except Exception as e:
        print(f"⚠️  Could not add tags column to {csv_path}: {e}")

def create_gitignore_entries():
    """Create or update .gitignore with credential paths"""
    gitignore_entries = [
        "\n# Configuration credentials (keep private)",
        "config/credentials/",
        "*.env",
        ".env"
    ]
    
    try:
        # Read existing .gitignore
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                existing = f.read()
        else:
            existing = ""
        
        # Add new entries if not already present
        new_entries = []
        for entry in gitignore_entries:
            if entry.strip() and entry.strip() not in existing:
                new_entries.append(entry)
        
        if new_entries:
            with open('.gitignore', 'a') as f:
                f.write('\n'.join(new_entries))
            print("🔒 Updated .gitignore with credential paths")
        else:
            print("ℹ️  .gitignore already contains credential entries")
            
    except Exception as e:
        print(f"⚠️  Could not update .gitignore: {e}")
        print("💡 Manually add 'config/credentials/' to .gitignore")

if __name__ == "__main__":
    migrate_config()