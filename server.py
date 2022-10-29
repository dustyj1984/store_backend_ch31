
import re
from colorama import Cursor
from flask import Flask, request, abort 
import json 
from config import me, db
from mock_data import catalog
from bson import ObjectId


app = Flask('Server')


################################################################
#      API ENDPOINTS
#      JSON
###############################################################

@app.get('/api/version')
def version():
    v = {
        "version": "1.0.0",
        "build": 42,
        "name": "sloth",
        "developer": me 
    }
    return json.dumps(v)

def fix_id(obj):
    obj['_id'] = str(obj['_id'])
    return obj


@app.get('/api/catalog')
def get_catalog():
    cursor = db.products.find({}).sort("title")
    results = []
    for prod in cursor:
        results.append(fix_id(prod))
    return json.dumps(results)


@app.post('/api/catalog')
def save_product():
    product= request.get_json()

    if product is None:
        return abort(400, "No Product required")

    product["category"] = product["category"].lower()

    db.products.insert_one(product)
    product["_id"] = str(product["_id"])
    return json.dumps(product)

@app.put("/api/catalog")
def update_product():
    product = request.get_json()
    id = product.pop("_id") # read and remove the id from the product

    db.products.update_one({"_id": ObjectId(id)}, {"$set":product})
    return json.dumps('ok')

@app.delete("/api/catalog/<id>")
def delete_product(id):
    res = db.products.delete_one({"_id": ObjectId(id)})
    return json.dumps({"count": res.deleted_count})


    

@app.get('/api/products/count')
def total_count():
    count = db.products.count_documents({})
    return json.dumps(count)


@app.get('/api/products/total')
def total_price():
    total = 0
    cursor = db.products.find({})
    for prod in cursor:
        total += prod['price']
    return json.dumps(total)

@app.get('/api/products/details/<id>')
def product_details(id):
    prod = db.products.find_one({"_id": ObjectId(id)})
    if prod:
        return json.dumps(fix_id(prod))
    return abort(404, "Product not found")



   

@app.get('/api/catalog/<category>')
def by_category(category):

    results = []
    cursor = db.products.find({"category": category})
    for prod in cursor:
        results.append(fix_id(prod))
    return json.dumps( results )


@app.get('/api/catalog/lower/<amount>')
def lower_than(amount):
    results = []
    cursor = db.products.find({"price": {"$lt": float(amount)}})
    for prod in cursor:
        results.append(fix_id(prod))
    return json.dumps(results)

@app.get('/api/catalog/higher/<amount>')
def higher_than(amount):
    results = []
    cursor = db.products.find({"price": {"$gte": float(amount)}})
    for prod in cursor:
        results.append(fix_id(prod))
    return json.dumps(results)
    
@app.get('/api/categroy/unique')
def unique_cats():
    results = []
    cursor = db.products.distinct("category")
    for cat in cursor:
        results.append(cat)
    return json.dumps( results )



#app.run(debug=True)