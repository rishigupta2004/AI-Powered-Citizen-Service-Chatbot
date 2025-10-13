# generate_dummy_data.py
import pandas as pd
import random
from faker import Faker
from datetime import datetime
import os
from supabase import create_client, Client
from dotenv import load_dotenv

class DummyDataGenerator:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize Supabase client
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.supabase: Client = None
        
        # Initialize Faker
        self.fake = Faker('en_IN')
        
        self.states_pincodes = {
            'Maharashtra': ['400001', '411001', '422001', '440001', '500001'],
            'Delhi': ['110001', '110002', '110003', '110004', '110005'],
            'Karnataka': ['560001', '560002', '560003', '570001', '575001'],
            'Tamil Nadu': ['600001', '600002', '600003', '625001', '641001'],
            'Uttar Pradesh': ['226001', '221001', '208001', '244001', '250001'],
            'Gujarat': ['380001', '380002', '390001', '395001', '360001'],
            'Rajasthan': ['302001', '313001', '324001', '334001', '341001'],
            'West Bengal': ['700001', '700002', '700003', '711101', '712101'],
            'Kerala': ['682001', '683501', '685001', '686001', '695001'],
            'Punjab': ['141001', '143001', '144001', '145001', '147001']
        }
        self.genders = ['Male', 'Female', 'Other']
        
    def connect_to_supabase(self):
        """Establish connection to Supabase and verify"""
        try:
            if not self.supabase_url or not self.supabase_key:
                print("❌ SUPABASE_URL or SUPABASE_ANON_KEY not found in .env file")
                return False
                
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            
            # Test connection by making a simple query
            test_response = self.supabase.table('citizens').select('count', count='exact').limit(1).execute()
            print("✅ Successfully connected to Supabase!")
            print(f"📊 Current records in database: {len(test_response.data)}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            return False
    
    def upload_to_supabase(self, data):
        """Upload generated data to Supabase"""
        if not self.supabase:
            print("❌ Supabase connection not established. Call connect_to_supabase() first.")
            return False
        
        try:
            print(f"📤 Uploading {len(data)} records to Supabase...")
            
            # Upload in batches to avoid timeout
            batch_size = 50
            total_uploaded = 0
            
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                response = self.supabase.table('citizens').insert(batch).execute()
                
                if hasattr(response, 'data') and response.data:
                    total_uploaded += len(response.data)
                    print(f"✅ Batch {i//batch_size + 1}: Uploaded {len(response.data)} records")
                else:
                    print(f"❌ Batch {i//batch_size + 1}: Failed to upload")
            
            print(f"🎉 Total records uploaded to Supabase: {total_uploaded}")
            return True
            
        except Exception as e:
            print(f"❌ Error uploading to Supabase: {e}")
            return False
    
    def check_existing_data(self):
        """Check if data already exists in Supabase"""
        if not self.supabase:
            return False
            
        try:
            response = self.supabase.table('citizens').select('uid').limit(5).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"⚠️ Could not check existing data: {e}")
            return False
    
    def generate_uid(self):
        """Generate 12-digit UID"""
        return ''.join([str(random.randint(0, 9)) for _ in range(12)])
    
    def generate_citizen_data(self, count=500):
        citizens_data = []
        used_uids = set()
        used_emails = set()
        
        print(f"👥 Generating {count} citizen records...")
        
        for i in range(count):
            # Ensure unique UID
            while True:
                uid = self.generate_uid()
                if uid not in used_uids:
                    used_uids.add(uid)
                    break
            
            # Ensure unique email
            while True:
                email = self.fake.unique.email()
                if email not in used_emails:
                    used_emails.add(email)
                    break
            
            state = random.choice(list(self.states_pincodes.keys()))
            pincode = random.choice(self.states_pincodes[state])
            
            citizen = {
                'uid': uid,
                'email': email,
                'name': self.fake.name(),
                'gender': random.choice(self.genders),
                'age': random.randint(18, 80),
                'address': self.fake.address().replace('\n', ', ')[:200],
                'pincode': pincode,
                'state': state,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            citizens_data.append(citizen)
            
            # Progress indicator
            if (i + 1) % 50 == 0:
                print(f"   Generated {i + 1}/{count} records...")
        
        return citizens_data

    def save_to_csv(self, data, filename='dummy_citizens.csv'):
        """Save data to CSV file"""
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"✅ Data saved to {filename}")
        return df
    
    def generate_sql_inserts(self, data, table_name='citizens'):
        """Generate SQL insert statements"""
        sql_file = 'insert_citizens.sql'
        with open(sql_file, 'w') as f:
            f.write(f"-- SQL Insert statements for {table_name} table\n\n")
            
            for citizen in data:
                columns = ', '.join(citizen.keys())
                
                # FIXED: Proper string escaping
                values_list = []
                for value in citizen.values():
                    if isinstance(value, str):
                        # Escape single quotes by doubling them
                        escaped_value = str(value).replace("'", "''")
                        values_list.append(f"'{escaped_value}'")
                    else:
                        values_list.append(str(value))
                
                values = ', '.join(values_list)
                insert_stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({values});\n"
                f.write(insert_stmt)
        
        print(f"✅ SQL insert statements saved to {sql_file}")
    
    def display_sample_data(self, data, sample_size=5):
        """Display sample generated data"""
        print("\n" + "="*50)
        print("SAMPLE GENERATED DATA")
        print("="*50)
        
        for i, citizen in enumerate(data[:sample_size]):
            print(f"\n--- Citizen {i+1} ---")
            for key, value in citizen.items():
                print(f"{key}: {value}")

def main():
    generator = DummyDataGenerator()
    
    # Connect to Supabase first
    print("🔗 Establishing connection to Supabase...")
    if not generator.connect_to_supabase():
        print("❌ Cannot proceed without Supabase connection.")
        return
    
    # Check if data already exists
    if generator.check_existing_data():
        print("⚠️  Data already exists in Supabase. Consider clearing the table first.")
        user_input = input("Do you want to continue and add more data? (y/n): ")
        if user_input.lower() != 'y':
            print("Operation cancelled.")
            return
    
    # Generate citizens
    print("\n🚀 Generating dummy citizen records...")
    citizens_data = generator.generate_citizen_data(100)  # Start with 100 for testing
    
    # Display sample
    generator.display_sample_data(citizens_data)
    
    # Save to CSV
    df = generator.save_to_csv(citizens_data)
    
    # Generate SQL inserts
    generator.generate_sql_inserts(citizens_data)
    
    # Upload to Supabase
    print("\n📤 Starting Supabase upload...")
    upload_success = generator.upload_to_supabase(citizens_data)
    
    # Print summary
    print("\n" + "="*50)
    print("📊 GENERATION SUMMARY")
    print("="*50)
    print(f"Total records generated: {len(citizens_data)}")
    print(f"Unique UIDs: {len(set(c['uid'] for c in citizens_data))}")
    print(f"Unique emails: {len(set(c['email'] for c in citizens_data))}")
    print(f"Supabase upload: {'✅ SUCCESS' if upload_success else '❌ FAILED'}")
    
    # State distribution
    state_counts = {}
    for citizen in citizens_data:
        state = citizen['state']
        state_counts[state] = state_counts.get(state, 0) + 1
    
    print(f"\nState distribution:")
    for state, count in state_counts.items():
        print(f"  {state}: {count} citizens")

if __name__ == "__main__":
    main()