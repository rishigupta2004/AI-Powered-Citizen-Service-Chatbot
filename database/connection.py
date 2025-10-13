# supabase_upload_standalone.py
import pandas as pd
from supabase import create_client
import os
from database.insert_dummy_data import DummyDataGenerator
def upload_dummy_data():
    """Direct upload without any authentication checks"""
    
    # Your Supabase credentials
    SUPABASE_URL = "your_project_url"
    SUPABASE_KEY = "your_anon_key"
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Generate or load your dummy data
    generator = DummyDataGenerator()
    citizens_data = generator.generate_citizen_data(100)  # Start with 100
    
    try:
        # Direct insert - no auth required for database operations
        response = supabase.table("citizens").insert(citizens_data).execute()
        
        print("✅ Success! Data inserted directly into Supabase")
        print(f"📊 Inserted {len(response.data)} records")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    upload_dummy_data()