import pandas as pd
import geopandas as gpd
import sqlalchemy as sqlalc


DB_CONNECTION_URL = "postgresql://aaron:HueManatee!2395@localhost:5432/regina_logistics"

def main():
    '''
    This is the ingestion script for our Postgis database.
    We'll extract, transform and load it step by step.
    '''

    # Extract
    # Read the messy CSV file
    raw_df = pd.read_csv("dataset/ODA_SK/ODA_SK.csv", low_memory=False)

    
    # Transform (Clean and Spatialize)
    # We'll filter for our target city immedidately to save memory.
    regina_df = raw_df[raw_df['csdname'] == 'Regina']

    # Then we'll create a "Geometry" Column.
    # This act as a bridge which takes two floats columns and creates a spatial object.
    geometry_col = gpd.points_from_xy(regina_df['longitude'], regina_df['latitude'])

    # Then we'll transform  the standard DataFrame to a GeoDataFrame.
    # A geodataframe looks like a table, but understands spatial operations.
    gdf = gpd.GeoDataFrame(regina_df, geometry = geometry_col)

    # We'll define the Coordinate Reference System (CRS)
    gdf.set_crs(epsg=4326, inplace=True) #EPSG is the standard code for GPS Latitude/Longitude

    # Load and push to PostGIS
    # First, we'll create the SQL Engine
    engine = sqlalc.create_engine(DB_CONNECTION_URL)
    
    # Then we write to the Database
    # to_postgis method is from GeoPandas and GeoAlchemy2
    # It automatically creates the table and spatial index
    gdf.to_postgis( 
        name = 'deliveries', # table to create in Postgres
        con= engine,         # The connection object
        if_exists='replace',  # If the table exists, drop it and replace
        index=True            # Create an index for faster lookups
    )

    print("Regina address data ingested to PostGIS container.")
    
    # We'll use this to check if the table was created or not
    inspector = sqlalc.inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables found in the database: {tables}")

    # We can target the 'deliveries' table and print the row count if it exists.
    if 'deliveries' in tables:
        with engine.connect() as conn:
            result = conn.execute(sqlalc.text("SELECT count(*) FROM deliveries"))
            print(f"Row count: {result.scalar()}")
    else:
        print("Table NOT found. Ingestion srcipt failed to save.")

   

main()