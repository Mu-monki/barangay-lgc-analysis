import geopandas as gpd
import pandas as pd
from scipy.spatial import cKDTree
import numpy as np

def calculate_nearest_distance(bgy_centroids, facility_gdf):
    """Uses a KD-Tree to rapidly find the distance to the nearest facility in meters."""
    if facility_gdf.empty:
        return np.full(len(bgy_centroids), np.nan)
        
    facility_coords = np.array([(geom.x, geom.y) for geom in facility_gdf.geometry])
    tree = cKDTree(facility_coords)
    distances, _ = tree.query(bgy_centroids)
    return distances

def run_comprehensive_accessibility_analysis():
    gpkg_path = "./gis/OUTPUT.gpkg"
    # Targeting the newly repaired map layer
    bgy_layer = "ph_barangay_lgc_tagged_fixed"
    
    facilities = {
        'Police': 'UP_Critical_Facilities_Police_Stations',
        'Fire': 'UP_Critical_Facilities_Fire_Stations',
        'Hospital': 'UP_Critical_Facilities_Hospitals',
        'School': 'UP_Critical_Facilities_Schools'
    }
    
    output_csv = "comprehensive_systemic_accessibility.csv"
    threshold_meters = 5000  # 5 km transit threshold

    print(f"Loading repaired barangay geometries from '{bgy_layer}'...")
    try:
        bgys = gpd.read_file(gpkg_path, layer=bgy_layer)
    except Exception as e:
        print(f"Error loading barangay layer: {e}")
        return

    # ID Column setup
    id_col = 'PHCode_Bgy' if 'PHCode_Bgy' in bgys.columns else (
        'correspondence_code' if 'correspondence_code' in bgys.columns else bgys.columns[0])

    # Safely identify the population column (if the merge worked)
    pop_cols = [c for c in bgys.columns if 'pop' in c.lower() and '2024' in c.lower()]
    pop_col = pop_cols[0] if pop_cols else ([c for c in bgys.columns if 'pop' in c.lower()][0] if any('pop' in c.lower() for c in bgys.columns) else None)

    # 1. Calculate Area and Population Density
    print("Calculating spatial parameters...")
    bgys['area_sqkm'] = bgys.geometry.area / 1_000_000
    
    if pop_col and bgys[pop_col].notna().any():
        bgys['pop_density_sqkm'] = bgys[pop_col] / bgys['area_sqkm']
        bgys['pop_density_sqkm'] = bgys['pop_density_sqkm'].replace([np.inf, -np.inf], np.nan).fillna(0).round(2)
    else:
        bgys['pop_density_sqkm'] = 0
        print("Note: Population data missing from merge. Density set to 0.")

    bgys['centroid'] = bgys.geometry.centroid
    bgy_coords = np.array([(geom.x, geom.y) for geom in bgys['centroid']])

    # 2. Process Facilities and Compile Distances
    print(f"Calculating network proximities (Threshold: {threshold_meters/1000} km)...")
    bgys['SAI_Score'] = 0
    
    for fac_name, layer_name in facilities.items():
        try:
            print(f"  -> Processing {fac_name} layer...")
            fac_gdf = gpd.read_file(gpkg_path, layer=layer_name)
            
            dist_col = f'dist_to_{fac_name}_m'
            access_col = f'has_{fac_name}_access'
            
            # Get exact distance to nearest facility
            bgys[dist_col] = calculate_nearest_distance(bgy_coords, fac_gdf).round(1)
            
            # Evaluate if distance is within the 5km threshold
            bgys[access_col] = (bgys[dist_col] <= threshold_meters).astype(int)
            bgys['SAI_Score'] += bgys[access_col]
            
        except Exception as e:
            print(f"  [!] Could not process {fac_name}: {e}")

    # 3. Sort for Systemic Prioritization
    # Priority targets: lowest score, highest density. 
    bgys = bgys.sort_values(by=['SAI_Score', 'pop_density_sqkm'], ascending=[True, False])

    # 4. Generate Terminal Report
    print(f"\n--- COMPREHENSIVE ACCESSIBILITY SUMMARY ---")
    print(f"Total Barangays Analyzed: {len(bgys)}")
    print(f"  Score 4 (Full Access): {len(bgys[bgys['SAI_Score'] == 4])}")
    print(f"  Score 3 (Missing 1):   {len(bgys[bgys['SAI_Score'] == 3])}")
    print(f"  Score 2 (Missing 2):   {len(bgys[bgys['SAI_Score'] == 2])}")
    print(f"  Score 1 (Missing 3):   {len(bgys[bgys['SAI_Score'] == 1])}")
    print(f"  Score 0 (No Access):   {len(bgys[bgys['SAI_Score'] == 0])}")

    print("\n--- SERVICE DEFICIT BREAKDOWN ---")
    for fac_name in facilities.keys():
        dist_col = f'dist_to_{fac_name}_m'
        if dist_col in bgys.columns:
            lacking = bgys[bgys[dist_col] > threshold_meters]
            count_lacking = len(lacking)
            if count_lacking > 0:
                avg_dist_km = (lacking[dist_col].mean() / 1000).round(2)
                max_dist_km = (lacking[dist_col].max() / 1000).round(2)
                print(f"{fac_name.upper()}:")
                print(f"  - Barangays without access: {count_lacking:,}")
                print(f"  - Average distance for those lacking: {avg_dist_km} km (Max: {max_dist_km} km)")
            else:
                print(f"{fac_name.upper()}: All barangays possess compliant access.")

    # 5. Export to CSV
    # Ensure area_name exists safely
    area_name_col = 'area_name' if 'area_name' in bgys.columns else (
        'Bgy_Name' if 'Bgy_Name' in bgys.columns else None)
    
    cols_to_export = [id_col]
    if area_name_col: cols_to_export.append(area_name_col)
    if pop_col and bgys[pop_col].notna().any(): cols_to_export.append(pop_col)
    cols_to_export.extend(['area_sqkm', 'pop_density_sqkm', 'SAI_Score'])
    
    for fac_name in facilities.keys():
        if f'dist_to_{fac_name}_m' in bgys.columns:
            cols_to_export.append(f'dist_to_{fac_name}_m')
            cols_to_export.append(f'has_{fac_name}_access')

    cols_to_export = [c for c in cols_to_export if c in bgys.columns]
    
    export_df = bgys[cols_to_export].drop(columns='geometry', errors='ignore')
    export_df.to_csv(output_csv, index=False)
    print(f"\nExported complete master list to '{output_csv}'")

if __name__ == "__main__":
    run_comprehensive_accessibility_analysis()