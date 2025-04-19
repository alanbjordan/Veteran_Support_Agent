# database_routes.py

from flask import Blueprint, request, jsonify
from helpers.cors_helpers import pre_authorized_cors_preflight
from services.data_service import get_all_data, search_data
from database import db
from sqlalchemy import text

database_bp = Blueprint("database", __name__)

@pre_authorized_cors_preflight
@database_bp.route("/data", methods=["GET"])
def get_inventory():
    """Get all data from the database."""
    try:
        # Get all inventory
        result, status_code = get_all_data()
        return jsonify(result), status_code
    except Exception as e:
        print(f"Error in get_data endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@pre_authorized_cors_preflight
@database_bp.route("/search", methods=["POST"])
def search_cars_endpoint():
    """Search for data based on filter criteria."""
    try:
        data = request.get_json(force=True)
        
        if not data:
            return jsonify({"error": "Missing JSON body"}), 400
        
        # Search for cars
        result, status_code = search_data(data)
        return jsonify(result), status_code
    except Exception as e:
        print(f"Error in search endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500


@pre_authorized_cors_preflight
@database_bp.route("/db-check", methods=["GET"])
def db_check():
    # Get current database name
    result = db.session.execute(text("SELECT current_database();"))
    db_name = result.scalar()
    # Get all tables in public schema
    tables = db.session.execute(
        text("SELECT tablename FROM pg_tables WHERE schemaname='public';")
    ).fetchall()
    table_list = [t[0] for t in tables]
    return jsonify({"database": db_name, "tables": table_list})