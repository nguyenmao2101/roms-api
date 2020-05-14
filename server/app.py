import toml
from flask import Flask
from flask import jsonify
from flask import make_response

import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors


with open('./db.toml', 'r') as f:
    database_config = toml.load(f).get('Database')


client = cosmos_client.CosmosClient(database_config.get("ACCOUNT_URI"), {
                                    'masterKey': database_config.get("ACCOUNT_KEY")})

app = Flask(__name__)


database_id = "Roms"
categories_container_id = "categories"
roms_container_id = "roms"
regions_container_id = "regions"


@app.route('/categories/<int:offset>/<int:limit>')
def list_categories(offset, limit):
    query = "select c.id, c.title from c offset {} limit {}".format(
        offset, limit)
    options = {'enableCrossPartitionQuery': True}
    categories = client.QueryItems(
        "dbs/" + database_id + "/colls/" + categories_container_id, query, options)
    out = list(categories)
    return jsonify(data=out)


@app.route('/roms/<string:category>/<string:region>/<int:offset>/<int:limit>')
def list_roms(category: str, region: str, offset: int, limit: int):
    query = "select c.link, c.title, c.file, c.logo, c.region from c where c.category='{}' and c.region='{}' offset {} limit {}".format(
        category, region, offset, limit)
    options = {'enableCrossPartitionQuery': True}
    roms = client.QueryItems("dbs/" + database_id +
                             "/colls/" + roms_container_id, query, options)
    out = list(roms)
    return jsonify(data=out)

@app.route('/regions')
def list_regions():
    query = "select c.id, c.title from c"
    options = {'enableCrossPartitionQuery': True}
    regions = client.QueryItems("dbs/" + database_id + "/colls/" + regions_container_id, query, options)
    out = list(regions)
    return jsonify(data=out)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify(error="Not found"), 404)


@app.errorhandler(500)
def server_error(error):
    return make_response(jsonify(error="Internal server error"), 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2020, debug=True)
