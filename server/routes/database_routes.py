from flask import Blueprint, request, jsonify
from helpers.cors_helpers import pre_authorized_cors_preflight
from services.data_service import get_all_data, search_data

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

