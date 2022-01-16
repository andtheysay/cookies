import logging
from sqlmodel import SQLModel, create_engine
import json
from dataclasses import dataclass
from etl.stores import run as etl_stores
from etl.sales import run as etl_sales
from etl.products import run as etl_products

# config to define variables
@dataclass
class Config:
    stores_url: str
    stores_filepath: str
    db_conn_uri: str
    log_level: str

# TODO convert this to a DAG or a pipeline
if __name__ == '__main__':
    # load the config
    config_dict = {}
    with open('config.json', 'r') as f:
        config_dict = json.load(f)
    if config_dict['log_level'] == 'DEBUG':    
        config_dict['log_level'] = logging.DEBUG
    else:
        config_dict['log_level'] = logging.INFO

    # create the config object
    config = Config(**config_dict)

    # setup logging
    logging.basicConfig()
    logging.getLogger().setLevel(config.log_level)

    # create the database engine
    engine = create_engine(config.db_conn_uri)

    # create the sqlmodel metadata for the engine
    SQLModel.metadata.create_all(engine)

    # handle stores
    etl_stores(config.stores_filepath, config.stores_url, engine)

    # handle products
    etl_products(engine)

    # handle sales data   
    etl_sales(engine)

