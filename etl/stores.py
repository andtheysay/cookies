import requests
import logging
import us
from pydantic import validator
from sqlmodel import Field, SQLModel, Session, create_engine
import json
from os.path import exists

# Define the Store model
# The model is a SQLModel so it gets Pydantic and SQLAlchemy methods
# It will be a SQL table with the name 'store'
class Store(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str
    state: str
    latitude: float
    longitude: float

    # Grab the needed fields from the data from the API
    def __init__(self, source_data):
        self.id = source_data['key']['id']
        self.name = source_data['name']['label']
        self.state = source_data['location']['address']['administrativeArea']
        self.latitude = source_data['location']['geo']['latitude']
        self.longitude = source_data['location']['geo']['longitude']

    # Verify that the State is a valid US state or territory
    @validator('state')
    def validate_state(cls, v):
        v = us.states.lookup(v)
        if v not in us.states.STATES_AND_TERRITORIES:
            raise ValueError(f'{v} is not a valid state')
        return v

    # Verify that the latitude is a float and between -90 and 90
    @validator('latitude')
    def validate_latitude(cls, v):
        v = float(v)
        if v < -90 or v > 90:
            raise ValueError(f'{v} is not a valid latitude')
        return v

    # Verify that the longitude is a float and between -180 and 180
    @validator('longitude')
    def validate_longitude(cls, v):
        v = float(v)
        if v < -180 or v > 180:
            raise ValueError(f'{v} is not a valid longitude')
        return v

    # Verify that the name is a string and not empty
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 1:
            raise ValueError(f'{v} is not a valid name')
        return v

# read the store data from the provided filepath or if the file does not exist pull the store data from the API
def extract(filepath: str, url: str) -> dict:
    # try filepath
    if exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    
    # try API
    try:
        r = requests.get(url)
        r.raise_for_status()
        logging.info('Successfully retrieved stores data')
        return r.json()
    except Exception as e:
        logging.warning(f'Error getting stores data: {e}')
        return None

# transform the data into a list of Store objects
def transform(data: dict) -> dict:
    stores = []
    if 'store' in data:
        for s in data['store']:
            try:
                stores.append(Store(s))
            except Exception as e:
                logging.warning(f'Error transforming store: {e}')
        return stores
    return None

# load the data into the database
def load(stores: list, engine) -> None:
    if not stores:
        logging.warning('No stores to load')
        return
    try:
        # Create a session to connect to the database
        with Session(engine) as session:
            # add the stores to the database
            session.add_all(stores)
            session.commit()
            logging.info(f'Successfully loaded {len(stores)} stores')
    except Exception as e:
        logging.warning(f'Error loading stores: {e}')

# main function to be called by the pipeline
def run(filepath: str, stores_url: str, engine):
    data = extract(filepath, stores_url)
    logging.debug(data.keys())
    stores = transform(data)
    load(stores, engine)