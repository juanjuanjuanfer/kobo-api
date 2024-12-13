from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["kobo-responses"]

@app.route('/', methods=['POST'])
def kobo_endpoint():
    try:
        data = request.get_json(silent=True)

        if data is None:
            data = {"raw_data": request.data.decode('utf-8')}

        doc_id = data.get("_id")
        if doc_id is None:
            return jsonify({"error": "Missing _id field in the received data."}), 400

        coll_name = data.get("_xform_id_string")
        collection = db[coll_name]
        existing_doc = collection.find_one({"_id": doc_id})

        if existing_doc:
            print(f"Document with _id {doc_id} already exists.")
            return jsonify({"message": "Document already exists in MongoDB."}), 200
        else:
            collection.insert_one(data)
            print(f"Document with _id {doc_id} inserted into MongoDB.")
            return jsonify({"message": "Document inserted into MongoDB."}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Railway provides the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
