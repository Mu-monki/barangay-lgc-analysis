import pandas as pd

def generate_compliance_summary():
    filename = "lgc_tagged_barangays.csv"
    
    print(f"Reading data from '{filename}'...")
    try:
        df = pd.read_csv(filename)
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found in the current directory.")
        return

    # Ensure the compliance column is treated as boolean
    df['analysis_meets_lgc_pop'] = df['analysis_meets_lgc_pop'].astype(str).str.lower().map({'true': True, '1': True, 'false': False, '0': False})
    df['analysis_meets_lgc_pop'] = df['analysis_meets_lgc_pop'].fillna(False).astype(bool)

    # 1. National Compliance
    nat_total = len(df)
    nat_compliant = df['analysis_meets_lgc_pop'].sum()
    nat_rate = (nat_compliant / nat_total) * 100 if nat_total > 0 else 0
    
    df_national = pd.DataFrame([{
        'Level': 'Philippines',
        'Total_Barangays': nat_total,
        'Compliant_Barangays': nat_compliant,
        'Non_Compliant_Barangays': nat_total - nat_compliant,
        'Compliance_Rate_Pct': round(nat_rate, 2)
    }])

    # Helper function for grouping and calculating rates
    def summarize_group(group_col, rename_col):
        # 'code' or 'correspondence_code' represents the unique barangay identifier
        unique_col = 'correspondence_code' if 'correspondence_code' in df.columns else df.columns[0]
        
        summary = df.groupby(group_col).agg(
            Total_Barangays=(unique_col, 'count'),
            Compliant_Barangays=('analysis_meets_lgc_pop', 'sum')
        ).reset_index()
        
        summary = summary.rename(columns={group_col: rename_col})
        summary['Non_Compliant_Barangays'] = summary['Total_Barangays'] - summary['Compliant_Barangays']
        summary['Compliance_Rate_Pct'] = round((summary['Compliant_Barangays'] / summary['Total_Barangays']) * 100, 2)
        
        # Sort by highest compliance rate
        return summary.sort_values(by='Compliance_Rate_Pct', ascending=False)

    # 2. Island Group Compliance
    df_island = summarize_group('island_region', 'Island_Group')

    # 3. Regional Compliance
    df_region = summarize_group('reg', 'Region_Code')
    
    # Official PSGC Region Dictionary Mapping
    psgc_regions = {
        "1": "Region I (Ilocos Region)",
        "2": "Region II (Cagayan Valley)",
        "3": "Region III (Central Luzon)",
        "4": "Region IV-A (CALABARZON)",
        "5": "Region V (Bicol Region)",
        "6": "Region VI (Western Visayas)",
        "7": "Region VII (Central Visayas)",
        "8": "Region VIII (Eastern Visayas)",
        "9": "Region IX (Zamboanga Peninsula)",
        "10": "Region X (Northern Mindanao)",
        "11": "Region XI (Davao Region)",
        "12": "Region XII (SOCCSKSARGEN)",
        "13": "NCR (National Capital Region)",
        "14": "CAR (Cordillera Administrative Region)",
        "15": "BARMM (Bangsamoro Autonomous Region in Muslim Mindanao)",
        "16": "Region XIII (Caraga)",
        "17": "MIMAROPA Region",
        "18": "NIR (Negros Island Region)",
        "19": "Bangsamoro Autonomous Region in Muslim Mindanao)",
    }
    
    # Safely convert Region Code to string (handling potential floats like '13.0') to match the dictionary
    df_region['Region_Code_Str'] = df_region['Region_Code'].astype(str).str.replace(r'\.0$', '', regex=True)
    
    # Map the names
    df_region['Region_Name'] = df_region['Region_Code_Str'].map(psgc_regions).fillna("Unknown Region")
    
    # Rearrange columns to put 'Region_Name' directly after 'Region_Code'
    cols = list(df_region.columns)
    cols.insert(1, cols.pop(cols.index('Region_Name')))
    cols.remove('Region_Code_Str') # Clean up temporary column
    df_region = df_region[cols]

    # 4. HUC / Metropolitan vs Regular City / Municipality Compliance
    df['Area_Classification'] = df['analysis_is_metropolitan'].apply(
        lambda x: 'HUC / Metro Manila' if str(x).lower() in ['true', '1'] else 'Regular City / Municipality'
    )
    df_classification = summarize_group('Area_Classification', 'Area_Classification')

    # Exporting the Data
    output_filename = "lgc_compliance_summary.xlsx"
    print(f"\nGenerating summary sheet: '{output_filename}'...")
    
    try:
        with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
            df_national.to_excel(writer, sheet_name='National_Summary', index=False)
            df_classification.to_excel(writer, sheet_name='HUC_vs_Regular_Summary', index=False)
            df_island.to_excel(writer, sheet_name='Island_Group_Summary', index=False)
            df_region.to_excel(writer, sheet_name='Regional_Summary', index=False)
        print("Success! Excel summary sheets created.")
    except ImportError:
        print("Notice: 'openpyxl' library is not installed. Exporting to separate CSV files instead...")
        df_national.to_csv("summary_national.csv", index=False)
        df_classification.to_csv("summary_huc_vs_regular.csv", index=False)
        df_island.to_csv("summary_island_groups.csv", index=False)
        df_region.to_csv("summary_regions.csv", index=False)
        print("Success! Created separate CSV files for National, HUC vs Regular, Island Groups, and Regions.")

    # Terminal Preview
    print("\n--- NATIONAL SUMMARY PREVIEW ---")
    print(df_national.to_string(index=False))
    
    print("\n--- HUC vs REGULAR CITY/MUNICIPALITY PREVIEW ---")
    print(df_classification.to_string(index=False))
    
    print("\n--- REGIONAL SUMMARY PREVIEW (Top 5) ---")
    print(df_region.head(5).to_string(index=False))

if __name__ == "__main__":
    generate_compliance_summary()