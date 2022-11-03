
import re
from colorama import Cursor
from flask import Flask, request, abort 
import json 
from config import me, db
from mock_data import catalog
from bson import ObjectId
from flask_cors import CORS


app = Flask('Server')
CORS(app) # disable CORS, enable on PROD




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
    
    if not "title" in product:
        return abort(400, "No Title")
        
    if len(product["title"]) < 5:
        return abort(400, "Title too short")
    
    if not "category" in product:
        return abort(400, "No Category")
    
    if not "price" in product:
        return abort(400, "No Price")

    if (not isinstance(product["price"], float)) and not isinstance(product["price"], int):
        return abort(400, "Price must be a number")
    
    if product["price"] < 1:
        return abort(400, "Invalid Price")



    

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
    
@app.post('/api/coupons')
def save_coupon():
    coupon = request.get_json()
    if not coupon:
        return abort(400, "No Coupon required")
    
    if not "code" in coupon:
        return abort(400, "No Coupon code required")
    
    if not "discount" in coupon:
        return abort(400, "No Coupon discount required")
    
    if (not isinstance ( coupon["discount"], float)) and not isinstance ( coupon["discount"], int):
        return abort(400, "Coupon discount must be a number")
    db.coupons.insert_one(coupon)
    fix_id(coupon)
    return json.dumps(coupon)


@app.get('/api/coupons')
def get_coupons():
    cursor = db.coupons.find({})
    results = []
    for coupon in cursor:
        results.append(fix_id(coupon))
    return json.dumps(results)

@app.get('/api/coupons/<code>')
def get_coupon(code):
    coupon = db.coupons.find_one({"code": code})
    if coupon:
        return json.dumps(fix_id(coupon))
    return abort(404, "Coupon not found")



   









#app.run(debug=True)