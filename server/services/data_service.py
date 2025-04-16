# server/services/inventory_service.py

from models.sql_models import MyTable

def get_all_data():
    """Get all data from the database."""
    """Return some data objects"""

    # Query all cars from the inventory
    query = MyTable.query.all()
        
        
    return query, 200

def search_data(data):
    """Search for data based on filter criteria."""
    """Return some data objects"""

    # Query all cars from the inventory
    query = MyTable.query.all()     

    return query, 200