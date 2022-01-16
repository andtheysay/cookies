import random
import logging
from enum import Enum
from sqlmodel import SQLModel, Field, Session
from pydantic import validator
import shortuuid

# Extend the Enum class to have a method to check if the passed value is in the enum
class EnumV(Enum):
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_ 

# Define the valid categories for a product
class ProductCategory(EnumV):
    CANNABIS = 'cannabis'
    CAPS = 'caps'
    OTHER = 'other'

# Define the valid units for a product
class ProductUnit(EnumV):
    GRAM = 'g'
    KILOGRAM = 'kg'
    OUNCE = 'oz'
    POUND = 'lb'
    PKG = 'pkg'

# Define the Product model
# The model is a SQLModel so it gets Pydantic and SQLAlchemy methods
# It will be a SQL table with the name 'product'
class Product(SQLModel, table=True):
    # Define the schema for the Product model
    sku: str = Field(default=None, primary_key=True)
    name: str
    price: float
    category: str
    unit: str
    price: float

    # Verify sku exists
    @validator('sku')
    def validate_sku(cls, v):
        if v is None or len(v) < 1:
            raise ValueError('SKU is required')
        return str(v)
    
    # Verify name exists
    @validator('name')
    def validate_name(cls, v):
        if v is None or len(str(v)) < 1:
            raise ValueError(f'{v} is required')
        return str(v)
    
    # Verify category is in the category enum
    @validator('category')
    def validate_category(cls, v):
        if not ProductCategory.has_value(v):
            raise ValueError(f'{v} is not a valid category')
        return v
    
    # Verify unit is in the unit enum
    @validator('unit')
    def validate_unit(cls, v):
        if not ProductUnit.has_value(v):
            raise ValueError(f'{v} is not a valid unit')
        return v

    # Verify price is a float, greater than 0, and rounded to 2 decimal places
    @validator('price')
    def validate_price(cls, v):
        v = float(v)
        if v < 0:
            raise ValueError(f'{v} is not a valid price')
        return round(v, 2)


# main method to be called by the pipeline
def run(engine):
    # TODO get real product price data abd all products
    # for now random price data and a subset of products will be used
    products = [
        Product(sku=shortuuid.uuid(), name='Berry Pue', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Cereal Milk', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Collins Ave', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Gary Payton', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Gelatti', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Georgia Pie', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Grenadine', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Honey Bun', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='London Pound Cake 75', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='London Chello', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Ocean Beach', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Pancakes', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Pink Rozay', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Pomelo', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Snow Man', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Sticky Buns', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Sweet Tea', price=round(random.uniform(5, 30), 2), category=ProductCategory.CANNABIS.value, unit=ProductUnit.GRAM.value),
        Product(sku=shortuuid.uuid(), name='Bed Head THC Rich', price=48, category=ProductCategory.CAPS.value, unit=ProductUnit.PKG.value),
        Product(sku=shortuuid.uuid(), name='Bed Head CBD Rich', price=55, category=ProductCategory.CAPS.value, unit=ProductUnit.PKG.value),
        Product(sku=shortuuid.uuid(), name='Clarity THC Rich', price=45, category=ProductCategory.CAPS.value, unit=ProductUnit.PKG.value),
        Product(sku=shortuuid.uuid(), name='Clarity CBD Rich', price=55, category=ProductCategory.CAPS.value, unit=ProductUnit.PKG.value),
        Product(sku=shortuuid.uuid(), name='BIC Lighter', price=2, category=ProductCategory.OTHER.value, unit=ProductUnit.PKG.value),
        Product(sku=shortuuid.uuid(), name='Cheap Lighter', price=1, category=ProductCategory.OTHER.value, unit=ProductUnit.PKG.value)
    ]
    logging.debug(p.name for p in products)
    # insert products into the database
    with Session(engine) as session:
        session.add_all(products)
        session.commit()