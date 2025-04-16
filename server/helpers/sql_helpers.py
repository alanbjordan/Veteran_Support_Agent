# server/helpers/sql_helpers.py

import json
from sqlalchemy import or_
from flask import g
from models.sql_models import MyTable

def myFunction():
    """
    Does some querying and filtering on an sql table.
      
    Returns:
        list: A list of filtered results from the table.
    """
    # Use the session attached to Flask's global context.
    session = g.session

    # Start with a base query.
    query = session.query(MyTable)

    return query
