import pymongo
import datetime

uri = "mongodb+srv://admin:7kKFyf3teMtazG8@testcluster.jsoah.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
cluster = pymongo.MongoClient(uri)
db = cluster["Fetch"]
point_collection = db["points"]

def use_points(amount, payer=None):
    '''
    attempt to use amount of points
    :param amount: amount of points that are trying to be spent
    :param payer: if there's a specific user you want to take it from. default to None
    :return: list of points used from each payer
    '''
    query = None
    if payer:
        query = {'payer':payer}
    list_of_points = point_collection.find(query)
    for i in list_of_points:
        print(i)
    return

def give_points(amount, payer, timestamp=datetime.datetime.now()):
    '''
    gives you points from the payer with the amount at the timestamp
    :param amount: amount of points
    :param payer: person who paid you points
    :param timestamp: timestamp of transaction (default is current time)
    :return: None
    '''
    new_points = {"payer": payer, "points": amount, "timestamp":timestamp}
    point_collection.insert_one(new_points)

def get_points():
    '''
    get the points given by payers
    :return: dictionary of payers and points
    '''
    payer_points = {}
    points_list = point_collection.find().sort("timestamp")
    for points in points_list:
        payer = points["payer"]
        amount = points["points"]
        if payer not in payer_points:
            payer_points[payer] = amount
        else:
            payer_points[payer] += amount
    return payer_points

def transaction(amount, payer, timestamp):
    '''
    processes transaction between payer and user
    :param amount: amount of points
    :param payer: the person taking or getting points
    :param timestamp: timestamp of the transaction
    :return: None
    '''
    if amount > 0:
        give_points(amount,payer, timestamp)
    else:
        use_points(amount, payer)

def multitransactions(transactions):
    '''
    takes an array of transactions and processes them in order of their timestamps
    :param transactions: array of transactions
    :return: None
    '''
    # sort based on the timestamp
    transactions.sort(key=lambda x: x["timestamp"])
    for transaction in transactions:
        print(transaction)
        amount = transaction["points"]
        payer = transaction["payer"]
        timestamp = transaction["timestamp"]
        # transaction(amount, payer, timestamp)


if __name__ == "__main__":
    transaction_history = [
        {"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z", },
        {"payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z", },
        {"payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z", },
        {"payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z", },
        {"payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z", },
    ]
    multitransactions(transaction_history)

    print(get_points())
    use_points(300, "omg")
    print()
    use_points(500)