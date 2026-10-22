import geopandas as gpd

def diagnose_missing_barangays():
    gpkg_path = "./gis/OUTPUT.gpkg"
    
    # 1. Load the raw, unfiltered government map
    raw_layer = "IMTWG_BarangayCOD_superfinal_utm"
    print(f"Loading raw layer '{raw_layer}'...")
    raw_gdf = gpd.read_file(gpkg_path, layer=raw_layer)
    
    # 2. Load your processed, tagged map
    tagged_layer = "ph_barangay_lgc_tagged — imtwg_barangaycod_superfinal_utm"
    print(f"Loading tagged layer '{tagged_layer}'...")
    tagged_gdf = gpd.read_file(gpkg_path, layer=tagged_layer)
    
    print("\n--- DIAGNOSTIC REPORT ---")
    print(f"Total Barangays in Raw Map: {len(raw_gdf)}")
    print(f"Total Barangays in Tagged Map: {len(tagged_gdf)}")
    print(f"Missing Barangays: {len(raw_gdf) - len(tagged_gdf)}")
    
    # Check for Null Geometries in the raw map
    null_geoms = raw_gdf.geometry.is_empty | raw_gdf.geometry.isna()
    print(f"Raw map rows missing physical polygons (Null Geometry): {null_geoms.sum()}")

if __name__ == "__main__":
    diagnose_missing_barangays()