import geopandas as gpd
import pandas as pd
from scipy.spatial import cKDTree
import numpy as np

def calculate_nearest_distance(bgy_centroids, facility_gdf):
    """Uses a KD-Tree to rapidly find the distance to the nearest facility."""
    if facility_gdf.empty:
        return np.full(len(bgy_centroids), np.nan)
        
    facility_coords = np.array([(geom.x, geom.y) for geom in facility_gdf.geometry])
    tree = cKDTree(facility_coords)
    
    # Query the tree for the nearest facility to each barangay centroid
    distances, _ = tree.query(bgy_centroids)
    return distances

def run_systemic_accessibility_analysis():
    # 1. Define File Paths (Update with your actual paths)
    gpkg_path = "./gis/OUTPUT.gpkg"
    bgy_layer = "ph_barangay_lgc_tagged — imtwg_barangaycod_superfinal_utm"
    
    # UP Critical Facilities Layers
    facilities = {
        'Police': 'UP_Critical_Facilities_Police_Stations',
        'Fire': 'UP_Critical_Facilities_Fire_Stations',
        'Hospital': 'UP_Critical_Facilities_Hospitals',
        'School': 'UP_Critical_Facilities_Schools'
    }
    
    output_csv = "systemic_development_priority.csv"
    threshold_meters = 5000  # Adapted 15-minute transit threshold (5 km)

    print("Loading barangay dataset...")
    bgys = gpd.read_file(gpkg_path, layer=bgy_layer)
    
    # Extract valid centroids (ignoring empty geometries)
    bgys['centroid'] = bgys.geometry.centroid
    bgy_coords = np.array([(geom.x, geom.y) for geom in bgys['centroid']])

    # 2. Calculate Distances and Accessibility Scores
    print(f"Calculating distances to critical facilities (Threshold: {threshold_meters/1000} km)...")
    bgys['SAI_Score'] = 0
    
    for fac_name, layer_name in facilities.items():
        try:
            print(f"  -> Processing {fac_name} layer...")
            fac_gdf = gpd.read_file(gpkg_path, layer=layer_name)
            
            # Calculate distance in meters
            dist_col = f'dist_to_{fac_name}_m'
            bgys[dist_col] = calculate_nearest_distance(bgy_coords, fac_gdf)
            
            # Boolean test: Does it meet the 15-minute access threshold?
            access_col = f'has_{fac_name}_access'
            bgys[access_col] = (bgys[dist_col] <= threshold_meters).astype(int)
            
            # Add to the total Service Accessibility Index (SAI)
            bgys['SAI_Score'] += bgys[access_col]
            
        except Exception as e:
            print(f"  [!] Could not process {fac_name}: {e}")

    # 3. Calculate Population Density
    print("Calculating population density...")
    # Safely handle the area calculation (assuming projected EPSG:32651 in meters)
    bgys['area_sqkm'] = bgys.geometry.area / 1_000_000
    
    # Replace 'analysis_pop_2024_cleaned' with your actual population column name
    pop_col = 'analysis_pop_2024_cleaned' 
    if pop_col not in bgys.columns:
        # Fallback if specific column isn't found
        pop_col = [c for c in bgys.columns if 'pop' in c.lower()][0]
        
    bgys['pop_density_sqkm'] = bgys[pop_col] / bgys['area_sqkm']
    
    # Replace infinities/NaNs with 0
    bgys['pop_density_sqkm'] = bgys['pop_density_sqkm'].replace([np.inf, -np.inf], np.nan).fillna(0)

    # 4. Filter for Systemic Development Priority
    # Target: High density (e.g., > 1,000 persons/sqkm) but extremely low access (Score 0 or 1)
    print("Identifying critical development zones...")
    priority_zones = bgys[(bgys['pop_density_sqkm'] >= 1000) & (bgys['SAI_Score'] <= 1)].copy()
    
    # Sort by the most densely populated, least serviced areas first
    priority_zones = priority_zones.sort_values(by=['SAI_Score', 'pop_density_sqkm'], ascending=[True, False])

    # 5. Export Results
    columns_to_export = ['correspondence_code', 'area_name', pop_col, 'area_sqkm', 'pop_density_sqkm', 
                         'dist_to_Police_m', 'dist_to_Fire_m', 'dist_to_Hospital_m', 'dist_to_School_m', 'SAI_Score']
    
    # Only keep columns that actually exist
    columns_to_export = [c for c in columns_to_export if c in priority_zones.columns]
    
    export_df = priority_zones[columns_to_export].drop(columns='geometry', errors='ignore')
    export_df.to_csv(output_csv, index=False)
    
    print(f"\n--- SYSTEMIC ANALYSIS SUMMARY ---")
    print(f"Total Barangays Analyzed: {len(bgys)}")
    print(f"Fully Serviced (Score 4): {len(bgys[bgys['SAI_Score'] == 4])}")
    print(f"Completely Unserviced (Score 0): {len(bgys[bgys['SAI_Score'] == 0])}")
    print(f"Critical Priority Zones (High Density + Low Access): {len(priority_zones)}")
    print(f"Exported priority development targets to '{output_csv}'")

if __name__ == "__main__":
    run_systemic_accessibility_analysis()