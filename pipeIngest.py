import pandas as pd
import geopandas as gpd
import sqlalchemy as sqlalc
from sqlalchemy import text
from typing import Literal


class LogisticsETL:
    def __init__(self, db_url: str, csv_path: str):
        '''
        Initialize the ETL pipeline with database connection string and source file path.
        '''
        self.db_url = db_url
        self.csv_path = csv_path
        self.engine = None
    
    def _get_engine(self):
        '''Lazy load the SQLAlchemy engine.'''
        if self.engine is None:
            self.engine = sqlalc.create_engine(self.db_url)
        return self.engine
    
    def extract(self) -> pd.DataFrame:
        ''' 
        Extract step: Reads the raw CSV file
        '''
        print(f"Extracting data from {self.csv_path}...")
        try:
            raw_df = pd.read_csv(self.csv_path, low_memory=False)
            print(f"Successfully loaded {len(raw_df)} rows.")
            return raw_df
        except FileNotFoundError:
            print(f"Error: File not found at {self.csv_path}")
            raise

    def transform(self, raw_df: pd.DataFrame, target_cities: list[str] | None = None) -> gpd.GeoDataFrame:
        '''
        Transform step: filters data, creates geometry, and converts to GeoDataFrame.
        '''
        if target_cities is None:
            target_cities = ['Regina']
        
        print(f"Tranforming data for hubs: {target_cities}...")

        # Filter for targe cities using .isin()
        cities_df = raw_df[raw_df['csdname'].isin(target_cities)].copy()
        
        if cities_df.empty:
            print(f"Warning: No data found for cities: {target_cities}")
            return gpd.GeoDataFrame()
        
        #Create a geometry colum
        #Bridge takes two float columnts and creates a spatial object.
        geometry_col = gpd.points_from_xy(cities_df['longitude'], cities_df['latitude'])

        #Crnatn GeoDataFrame
        gdf = gpd.GeoDataFrame(cities_df, geometry=geometry_col)

        #Define Coordinate Reference System
        gdf.set_crs(epsg=4326, inplace=True)

        print(f"Transformation complete. {len(gdf)} spatial records prepared.")
        return gdf
    
    def load(self, gdf: gpd.GeoDataFrame, table_name: str = 'deliveries', if_exists: Literal['fail', 'replace', 'append']= 'replace'):
        """
        Load step: Pushes the GeoDataFrame to PostGIS.
        Args:
            if_exists: 'fail', 'replace', or 'append'. Default 'replace'.
        """
        if gdf.empty:
            print("Skipping load: GeoDataFrame is empty.")
            return

        print(f"Loading data into PostGIS table '{table_name}'...")
        engine = self._get_engine()

        # to_postgis automatically creates/replaces table and spatial index
        gdf.to_postgis(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=True
        )
        print("Data successfully committed to database.")
    
    def validate(self, table_name: str = 'deliveries'):
        '''Validation step that checks if table exists and counts rows '''
        engine = self._get_engine()
        inspector = sqlalc.inspect(engine)
        tables = inspector.get_table_names()

        print(f"Tables found in database: {tables}")

        if table_name in tables:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT count(*) FROK {table_name}"))
                count = result.scalar()
                print(f"Validation Successful: '{table_name}' contains {count} rows.")
        else:
            print(f"Validation Failed: '{table_name}' NOT FOUND.")

    def run(self, target_cities: list[str] | None = None):
        '''Orchestrates the full ETL pipeline'''
        if target_cities is None:
            target_cities = ['Regina']
        try:
            raw_data = self.extract()
            geo_data = self.transform(raw_data, target_cities=target_cities)
            self.load(geo_data, if_exists='replace')
            self.validate()
        except Exception as e:
            print(f"ETL pipeline faild: {e}")