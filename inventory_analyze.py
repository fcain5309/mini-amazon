from flask import render_template
from .models.inventory_analyze import Product_Rank
from flask import Blueprint

bp = Blueprint('inventory_analyze', __name__)

@bp.route('/inventory-analyze/<uid>', methods=['GET'])
def inventoryAnalyze(uid):
    top_products = Product_Rank.top_ten_products(uid)
    worst_products= Product_Rank.worst_ten_products(uid)
    lowest_products = Product_Rank.lowest_ten_products(uid)
    return render_template("inventory_analyze.html", top_products=top_products, worst_products = worst_products, lowest_products = lowest_products, uid=uid)