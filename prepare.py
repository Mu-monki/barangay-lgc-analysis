import pandas as pd
import json
import os

def prepare_csv_for_qgis():
    input_file = 'lgc_tagged_barangays.json'
    output_file = 'lgc_tagged_for_qgis.csv'
    
    if not os.path.exists(input_file):
        print(f"Error: Could not find '{input_file}'.")
        return
        
    print(f"Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    
    # 1. Create the matching column for the Shapefile
    print("Adding 'PH' prefix to match shapefile codes...")
    # Ensures the code is treated as a string, preventing leading zeros from disappearing
    df['PHCode_Bgy_match'] = "PH" + df['correspondence_code'].astype(str)
    
    # 2. Drop the nested JSON array which breaks QGIS attribute tables
    if 'populations' in df.columns:
        df = df.drop(columns=['populations'])
        
    # 3. Export to CSV
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Success! Saved formatted data to '{output_file}'.")

if __name__ == "__main__":
    prepare_csv_for_qgis()