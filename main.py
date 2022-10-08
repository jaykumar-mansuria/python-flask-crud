from flask import Flask, request, json, Response
from pymongo import MongoClient
import logging as log

app = Flask(__name__)


class MongoAPI:
    def __init__(self, data):
        log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s:\n%(message)s\n')
        self.client = MongoClient("mongodb://localhost:27017/")

        self.database = self.client['company']
        self.collection = self.database['emp']
        self.data = data

    def read(self):
        log.info('Reading All Data')
        # print(self.data)
        documents = self.collection.find(self.data)
        output = [{item: data[item] for item in data if item != '_id'} for data in documents]
        return output

    def get(self):
        log.info('Getting Data')
        response = self.collection.find_one(self.data)
        # print(response)
        if response:
            return {item: response[item] for item in response if item != '_id'}
        else:
            return "No data found"

    def write(self):
        log.info('Writing Data')
        response = self.collection.insert_one(self.data)
        output = {'Status': 'Successfully Inserted',
                  'Document_ID': str(response.inserted_id)}
        return output

    def update(self):
        log.info('Updating Data')
        updated_data = {"$set": self.data['data']}
        response = self.collection.update_one(self.data['filter'], updated_data)
        output = {'Status': 'Successfully Updated' if response.modified_count > 0 else "Nothing was updated."}
        return output

    def delete(self):
        log.info('Deleting Data')
        response = self.collection.delete_one(self.data)
        output = {'Status': 'Successfully Deleted' if response.deleted_count > 0 else "Document not found."}
        return output

    def check_data(self):
        if self.data:
            return [True, ""]
        else:
            return [False, Response(response=json.dumps({"Error": "Please provide data in your request"}),
                                    status=400, mimetype='application/json')]


@app.route('/')
def home():
    return Response(response=json.dumps({"Status": "UP", "other_message": "To perform crud on employee go to /emp"}),
                    status=200, mimetype='application/json')


@app.route('/emp', methods=['GET', 'POST', 'PUT', 'DELETE'])
def employee_crud():
    data = request.json
    obj1 = MongoAPI(data)
    response = None
    if request.method in ['POST', 'PUT', 'DELETE']:
        valid_data = obj1.check_data()
        if not valid_data[0]:
            return valid_data[1]
    if request.method == 'GET':
        response = obj1.read()
    elif request.method == 'POST':
        response = obj1.write()
    elif request.method == 'PUT':
        response = obj1.update()
    elif request.method == 'DELETE':
        response = obj1.delete()
    return Response(response=json.dumps(response), status=200, mimetype='application/json')


@app.route('/emp/<int:emp_id>', methods=['GET'])
def mongo_get(emp_id):
    data = {"EMPLOYEE_ID": emp_id}
    obj1 = MongoAPI(data)
    response = obj1.get()
    return Response(response=json.dumps(response), status=200,  mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
