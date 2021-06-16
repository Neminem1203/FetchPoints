import pymongo
import datetime
from flask import Flask, request, json
import requests

debug_mode = True
PORT = 5000
# MONGODB
uri = "mongodb+srv://admin:7kKFyf3teMtazG8@testcluster.jsoah.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
cluster = pymongo.MongoClient(uri)
db = cluster["Fetch"]
point_collection = db["points"]

def reset_db():
    db["points"].drop()
    global point_collection
    point_collection = db["points"]
    # SEED
    transaction_history = [
        {"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z", },
        {"payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z", },
        {"payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z", },
        {"payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z", },
        {"payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z", },
    ]
    multitransactions(transaction_history)

def chronological_points_list(query=None):
    return point_collection.find(query).sort("timestamp")

def spend_points(amount, payer=None):
    '''
    attempt to use amount of points
    :param amount: amount of points that are trying to be spent
    :param payer: if there's a specific user you want to take it from. default to None
    :return: list of points used from each payer
    '''
    query = {'payer':payer} if payer else None      # used for querying database
    points_list = chronological_points_list(query)  # list of points in timestamp order
    transaction_list = []                           # list of transactions we will be using
    remaining = int(amount)                         # used to check if we can pay in full
    paid_in_full = False                            # boolean of whether there's enough points

    for transaction in points_list:
        points = transaction["points"]
        if points == 0:
            continue
        transaction_list.append(transaction)
        if remaining > points:
            remaining -= points
        else: # remaining is less than or eq points, so we know that we have enough points to pay
            paid_in_full = True
            break

    # Confirmed we have enough points to pay in full
    if paid_in_full:
        return_list = []
        for transaction in transaction_list[:-1]:
            payer = transaction["payer"]
            id = transaction["_id"]
            paid = transaction["points"]*-1
            point_collection.update_one({"_id": id}, {"$set": {"points": 0}}, upsert=True)
            return_list.append({payer: paid})
        last_id = transaction_list[-1]["_id"]
        last_payer = transaction_list[-1]["payer"]
        new_points = transaction_list[-1]["points"] - remaining
        point_collection.update_one({"_id": last_id}, {"$set": {"points": new_points}}, upsert=True)
        return_list.append({last_payer: remaining * -1})
        err = {"error": None}
    else:
        end_str = ""
        if payer:
            end_str = " from " + payer
        return_list = None
        err = {"error": "Not Enough Points. Missing "+ str(remaining)+ " points" + end_str}
    return [return_list, err]

def give_points(amount, payer, timestamp=datetime.datetime.now()):
    '''
    gives you points from the payer with the amount at the timestamp
    :param amount: amount of points
    :param payer: person who paid you points
    :param timestamp: timestamp of transaction (default is current time)
    :return: Payer and Amount in a dictionary
    '''
    new_points = {"payer": payer, "points": int(amount), "timestamp":timestamp}
    point_collection.insert_one(new_points)
    return [{payer: amount}]

def balance():
    '''
    get the points given by payers
    :return: dictionary of payers and points
    '''
    payer_points = {}
    points_list = chronological_points_list()
    for points in points_list:
        payer = points["payer"]
        amount = points["points"]
        if payer not in payer_points:
            payer_points[payer] = amount
        else:
            payer_points[payer] += amount
    return payer_points

# DEVELOPER PURPOSES
def create_transaction(amount, payer, timestamp):
    '''
    processes transaction between payer and user
    :param amount: amount of points
    :param payer: the person taking or getting points
    :param timestamp: timestamp of the transaction
    :return: None
    '''
    if amount >= 0:
        return give_points(amount,payer, timestamp)
    else:
        return spend_points(-1*amount, payer)

def multitransactions(transactions):
    '''
    takes an array of transactions and processes them in order of their timestamps
    :param transactions: array of transactions
    :return: None
    '''
    # sort based on the timestamp
    transactions.sort(key=lambda x: x["timestamp"])
    for transaction in transactions:
        amount = transaction["points"]
        payer = transaction["payer"]
        timestamp = transaction["timestamp"]
        resp = create_transaction(amount, payer, timestamp)
        # print("Transaction: ",resp)


# FLASK
app = Flask(__name__)

def json_response(resp, status_code):
    return app.response_class(
        response=json.dumps(resp),
        status=status_code,
        mimetype='application/json'
    )

AMT_VAL_ERR = json_response({"error": "Amount needs to be a number"}, 400)
UNKWN_ERR = json_response({"error": "Unknown error occured"}, 400)

SPEND_ROUTE = "/api/spend_points"
GIVE_ROUTE = "/api/give_points"
BAL_ROUTE = "/api/balance"

@app.route(GIVE_ROUTE)
def give_points_route():
    try:
        amount = request.args.get('amount')
        payer = request.args.get('payer')

        err = []
        if amount == None:
            err.append("Amount is missing")
        if payer == None:
            err.append("Payer is missing")
        if len(err) != 0:
            return json_response({"error": err}, 400)

        return json_response(give_points(amount, payer), 200)
    except ValueError:
        return AMT_VAL_ERR
    except:
        return UNKWN_ERR

@app.route(SPEND_ROUTE)
def spend_points_route():
    try:
        amount = request.args.get('amount')
        if amount == None:
            return json_response({"error": "Missing amount"}, 400)
        status_code = 200
        resp, err = spend_points(amount)
        if err["error"] != None:
            return json_response(err, 400)
        return json_response(resp, status_code)
    except ValueError:
        return AMT_VAL_ERR
    except:
        return UNKWN_ERR
    return UNKNWN_ERR

@app.route(BAL_ROUTE)
def balance_route():
    return json_response(balance(), 200)




if __name__ == "__main__":
    reset_db()
    app.run(port=PORT, debug=debug_mode)