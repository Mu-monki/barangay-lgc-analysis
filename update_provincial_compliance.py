import pandas as pd

def update_provincial_compliance_with_names():
    input_csv = "lgc_tagged_for_qgis.csv"
    output_csv = "lgc_provincial_compliance_named.csv"

    print(f"Loading dataset: '{input_csv}'...")
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: Could not find '{input_csv}'.")
        return

    # 1. PSGC Province & HUC Mapping Dictionary
    # Maps the standard 1-86 province codes and the new 300/800-level HUC codes
    # 1. Comprehensive PSGC Province & HUC Mapping Dictionary
    psgc_prov_map = {
        # Provinces
        1: 'Abra', 2: 'Agusan del Norte', 3: 'Agusan del Sur', 4: 'Aklan', 5: 'Albay', 
        6: 'Antique', 7: 'Basilan', 8: 'Bataan', 9: 'Batanes', 10: 'Batangas', 
        11: 'Benguet', 12: 'Bohol', 13: 'Bukidnon', 14: 'Bulacan', 15: 'Cagayan', 
        16: 'Camarines Norte', 17: 'Camarines Sur', 18: 'Camiguin', 19: 'Capiz', 
        20: 'Catanduanes', 21: 'Cavite', 22: 'Cebu', 23: 'Davao del Norte', 
        24: 'Davao del Sur', 25: 'Davao Oriental', 26: 'Eastern Samar', 27: 'Ifugao', 
        28: 'Ilocos Norte', 29: 'Ilocos Sur', 30: 'Iloilo', 31: 'Isabela', 32: 'Kalinga', 
        33: 'La Union', 34: 'Laguna', 35: 'Lanao del Norte', 36: 'Lanao del Sur', 
        37: 'Leyte', 38: 'Maguindanao', 39: 'Manila (Legacy)', 40: 'Marinduque', 41: 'Masbate', 
        42: 'Misamis Occidental', 43: 'Misamis Oriental', 44: 'Mountain Province', 
        45: 'Negros Occidental', 46: 'Negros Oriental', 47: 'Cotabato', 48: 'Northern Samar', 
        49: 'Nueva Ecija', 50: 'Nueva Vizcaya', 51: 'Occidental Mindoro', 52: 'Oriental Mindoro', 
        53: 'Palawan', 54: 'Pampanga', 55: 'Pangasinan', 56: 'Quezon', 57: 'Quirino', 
        58: 'Rizal', 59: 'Romblon', 60: 'Samar', 61: 'Siquijor', 62: 'Sorsogon', 
        63: 'South Cotabato', 64: 'Southern Leyte', 65: 'Sultan Kudarat', 66: 'Sulu', 
        67: 'Surigao del Norte', 68: 'Surigao del Sur', 69: 'Tarlac', 70: 'Tawi-Tawi', 
        71: 'Zambales', 72: 'Zamboanga del Norte', 73: 'Zamboanga del Sur', 
        77: 'Aurora', 78: 'Biliran', 79: 'Guimaras', 80: 'Sarangani', 81: 'Apayao', 
        82: 'Davao de Oro', 83: 'Zamboanga Sibugay', 85: 'Dinagat Islands', 
        86: 'Davao Occidental', 97: 'Maguindanao del Norte', 98: 'Maguindanao del Sur',
        
        # 300-Level Independent / Highly Urbanized Cities outside Metro Manila
        301: 'Angeles City', 302: 'Bacolod City', 303: 'Baguio City', 304: 'Butuan City',
        305: 'Cagayan de Oro City', 306: 'Cebu City', 307: 'Cotabato City', 
        308: 'General Santos City', 309: 'Iligan City', 310: 'Iloilo City', 
        311: 'Mandaue City', 312: 'Ormoc City', 313: 'Lapu-Lapu City', 
        314: 'Puerto Princesa City', 315: 'Santiago City', 316: 'Zamboanga City', 
        317: 'Davao City', 318: 'Lucena City', 319: 'Tacloban City',
        
        # 800-Level Metro Manila Local Government Units
        801: 'Caloocan City', 802: 'Las Piñas City', 803: 'Makati City', 804: 'Malabon City', 
        805: 'Mandaluyong City', 806: 'City of Manila', 807: 'Marikina City', 808: 'Muntinlupa City', 
        809: 'Navotas City', 810: 'Parañaque City', 811: 'Pasay City', 812: 'Pasig City', 
        813: 'Quezon City', 814: 'San Juan City', 815: 'Taguig City', 816: 'Valenzuela City', 
        817: 'Pateros',

        # Special Administrative Regions & Recent Splits
        87: 'Maguindanao del Norte', 
        88: 'Maguindanao del Sur',
        901: 'Isabela City', 
        999: 'Special Geographic Area (BARMM)'
    }

    # 2. Standardize population thresholds and evaluate LGC compliance
    df['Updated_LGC_Threshold'] = df['analysis_is_metropolitan'].apply(lambda x: 5000 if x else 2000)
    df['analysis_pop_2024_cleaned'] = df['analysis_pop_2024_cleaned'].fillna(0)
    df['Is_Compliant'] = df['analysis_pop_2024_cleaned'] >= df['Updated_LGC_Threshold']

    # Map the text names, with a dynamic fallback just in case a new HUC code exists
    df['Province_Name'] = df['prv'].map(psgc_prov_map).fillna(df['prv'].apply(lambda x: f"HUC / Prov Code {x}"))

    print("Aggregating LGC compliance by Province/HUC...\n")
    
    # 3. Group by the translated Province Name
    summary = df.groupby('Province_Name').agg(
        Total_Barangays=('code', 'count'),
        Compliant_Barangays=('Is_Compliant', 'sum')
    ).reset_index()

    # Calculate Non-Compliant counts and Compliance Rates
    summary['Non_Compliant_Barangays'] = summary['Total_Barangays'] - summary['Compliant_Barangays']
    summary['Compliance_Rate'] = (summary['Compliant_Barangays'] / summary['Total_Barangays'] * 100)

    # 4. Sort to rank the worst compliance rates at the top
    summary = summary.sort_values(by=['Compliance_Rate', 'Total_Barangays'], ascending=[True, False])

    # Calculate National Totals
    total_brgys = summary['Total_Barangays'].sum()
    total_compliant = summary['Compliant_Barangays'].sum()
    total_non_compliant = summary['Non_Compliant_Barangays'].sum()
    total_rate = (total_compliant / total_brgys) * 100

    # Format the numbers for terminal output
    summary_print = summary.copy()
    summary_print['Total_Barangays'] = summary_print['Total_Barangays'].apply(lambda x: f"{x:,}")
    summary_print['Compliant_Barangays'] = summary_print['Compliant_Barangays'].apply(lambda x: f"{x:,}")
    summary_print['Non_Compliant_Barangays'] = summary_print['Non_Compliant_Barangays'].apply(lambda x: f"{x:,}")
    summary_print['Compliance_Rate'] = summary_print['Compliance_Rate'].apply(lambda x: f"{x:.2f}%")

    print("--- 5 PROVINCES/HUCs WITH LOWEST COMPLIANCE ---")
    print(summary_print.head(5).to_string(index=False))
    
    print("\n--- 5 PROVINCES/HUCs WITH HIGHEST COMPLIANCE ---")
    print(summary_print.tail(5).to_string(index=False))

    print("\n" + "-" * 85)
    print(f"{'NATIONAL TOTAL':<25} {total_brgys:<16,} {total_compliant:<20,} {total_non_compliant:<20,} {total_rate:.2f}%")

    # 5. Export the readable master list
    summary.to_csv(output_csv, index=False)
    print(f"\nSuccessfully exported mapped provincial ranking to '{output_csv}'")

if __name__ == "__main__":
    update_provincial_compliance_with_names()