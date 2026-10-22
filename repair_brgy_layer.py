import geopandas as gpd
import pandas as pd

def lossless_spatial_merge():
    # 1. Define File Paths
    gpkg_path = "./gis/OUTPUT.gpkg"
    raw_layer = "IMTWG_BarangayCOD_superfinal_utm"
    csv_path = "lgc_tagged_for_qgis.csv" # REPLACE with your actual CSV filename
    output_layer = "ph_barangay_lgc_tagged_fixed"

    print(f"Loading raw map geometries from '{raw_layer}'...")
    map_gdf = gpd.read_file(gpkg_path, layer=raw_layer)

    print(f"Loading demographic data from '{csv_path}'...")
    try:
        demographics_df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: Could not find '{csv_path}'. Please check the filename.")
        return

    print("Repairing stripped leading zeros in PSGC codes...")
    # Replace 'PSGC_Code' with the actual column name in your CSV
    csv_id_col = 'PSGC_Code' if 'PSGC_Code' in demographics_df.columns else demographics_df.columns[0]
    
    # Convert to string, remove decimals if it was read as a float, and pad to 9 digits
    demographics_df[csv_id_col] = demographics_df[csv_id_col].astype(str).str.split('.').str[0].str.zfill(9)

    print("Executing lossless Left Join...")
    # Find the matching ID column in the raw map
    map_id_col = 'PHCode_Bgy' if 'PHCode_Bgy' in map_gdf.columns else map_gdf.columns[0]
    
    # The 'left' merge ensures all 42,058 map geometries are kept, even if demographics are missing
    repaired_gdf = map_gdf.merge(demographics_df, how='left', left_on=map_id_col, right_on=csv_id_col)

    print("Exporting repaired layer to GeoPackage...")
    repaired_gdf.to_file(gpkg_path, layer=output_layer, driver="GPKG")
    
    print("\n--- REPAIR SUMMARY ---")
    print(f"Original Map Polygons: {len(map_gdf)}")
    print(f"Repaired Layer Polygons: {len(repaired_gdf)}")
    
    # Count how many map polygons still failed to find demographic data
    unmatched = repaired_gdf[csv_id_col].isna().sum()
    print(f"Barangays mapped but missing demographic data: {unmatched}")
    print(f"\nSuccess! Load '{output_layer}' into QGIS to run the systemic analysis.")

if __name__ == "__main__":
    lossless_spatial_merge()