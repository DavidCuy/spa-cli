import polars as pl

from aws_lambda_powertools import Logger
from core_db.config import CONNECTIONS
from core_db.DBConnection import DBConnection

logger = Logger()

engine_avops = DBConnection(**CONNECTIONS.get('avasaops')).get_engine()
engine_default = DBConnection(**CONNECTIONS.get('default')).get_engine()

df = pl.read_database(query="select id from kavak_list_vehicles", connection=engine_avops)
df = df.with_columns(
    pl.col("id").cast(pl.Int32)
)
df = df.rename({"id": "id_vehicle"})
df = df.with_columns(
    pl.lit(2).alias("id_state")
)

df.write_database(table_name="vehicle_verification_schema.rel_vehicle_state", connection=engine_default, if_table_exists="replace")