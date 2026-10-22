import pandas as pd
import json

def convert_for_qgis():
    with open('lgc_tagged_barangays.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    df = pd.DataFrame(data)
    # Drop the nested dictionary column which breaks QGIS imports
    df = df.drop(columns=['populations'], errors='ignore') 
    
    df.to_csv('lgc_tagged_barangays.csv', index=False, encoding='utf-8')
    print("Success! File is ready for QGIS.")

if __name__ == "__main__":
    convert_for_qgis()