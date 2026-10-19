import os
from dotenv import load_dotenv
load_dotenv()

def database_url():
    from urllib.parse import quote_plus
    return "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
        quote_plus(os.getenv("PGUSER", "postgres")),
        quote_plus(os.getenv("PGPASSWORD", "")),
        os.getenv("PGHOST", "localhost"),
        os.getenv("PGPORT", "5432"),
        os.getenv("PGDATABASE", "customer_analytics"))

DATA_DIR = os.getenv("DATA_DIR", "data")
