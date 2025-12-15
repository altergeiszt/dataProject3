from pipeIngest import LogisticsETL

# Configuration constants
DB_CONNECTION_URL = "postgresql://aaron:HueManatee!2395@localhost:5432/regina_logistics"
SOURCE_CSV = "dataset/ODA_SK/ODA_SK.csv"

def main():
    print("Starting Logistics Engine...")

    # 1. Instantiate the ETL pipeline
    etl_pipeline = LogisticsETL(DB_CONNECTION_URL, SOURCE_CSV)
    
    # 2. Run the pipeline for specific hubs
    # We can easily add 'Moose Jaw' or 'Prince Albert' here in the future
    target_hubs = ['Regina', 'Saskatoon']
    etl_pipeline.run(target_cities=target_hubs)

    print("Batch processing complete.")

if __name__ == "__main__":
    main()