from datetime import datetime
import logging
from typing import List, Optional
from pydantic import BaseConfig
from sqlmodel import Field, SQLModel, Session
import shortuuid
import random
from faker import Faker

# Line items that would be on a receipt
# Each line item has an id, sku, price, quantity, and transaction_id
class LineItem(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    sku: str = Field(foreign_key="product.sku")
    price: float
    quantity: int
    transaction_id: int = Field(foreign_key="transaction.id")

# Each transaction has an id, store_id, date, and total
class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    store_id: str = Field(foreign_key="store.id")
    date: datetime
    total: float


# TODO extract real sales data, transform it, and load into db
# for now random data in the correct format will do.
def run(engine):
    # Allow arbitary types for Pydantic validation
    BaseConfig.arbitrary_types_allowed = True

    # Create a fake data generator
    fake = Faker()

    # Create a session to interact with the database
    with Session(engine) as session:
        # Get all of the store ids
        store_ids = session.exec(f'SELECT id FROM store').fetchall()
        logging.debug(store_ids)
        # Get all of the products
        products = session.exec(f'SELECT * FROM product').fetchall()
        logging.debug(p.name for p in products)
        # Define a list of transactions and sales
        transactions = List(Transaction)
        sales = List(LineItem)
        # generate 100k random transactions
        for i in range(0, 100000):
            # lineitems is a temp list to hold the line items for this transaction
            lineitems = List(LineItem)
            # temp_products is a temp copy of the products list to prevent picking the same product twice in the same transaction
            # [:] it to make a copy and not a reference
            temp_products = products[:]
            # shuffle the temp products list to make it random
            random.shuffle(temp_products)
            # add a random amount of line items to the transaction (no more than the total aount of products to prevent index out of range)
            for j in range(0, random.randint(0, len(products)-1)):
                # pick the next product from the temp products list and remove it from the list (pop)
                p = temp_products.pop()
                # create a new line item with the current transaction id, product p, and a random quantity
                lineitems.append(LineItem(transaction_id=i, id=shortuuid.uuid(), price=p.price, quantity=random.randint(1, 10), sku=p.sku))
            # add the line items for this transaction to the sales list
            sales.extend(lineitems)
            # create a new transaction with a random store id (from the list of store ids), date, and total
            transactions.append(Transaction(
                store_id=random.choice(store_ids)[0],
                date=fake.date_time_between(start_date="-1y", end_date="now"),
                total=sum(item.price * item.quantity for item in lineitems),
                id=i
            ))
        # insert the transactions into the database
        session.add_all(transactions)
        session.commit()
        # insert the sales into the database
        session.add_all(sales)
        session.commit()
