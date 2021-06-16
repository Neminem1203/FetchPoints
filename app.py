import pymongo
import datetime

uri = "mongodb+srv://admin:7kKFyf3teMtazG8@testcluster.jsoah.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
cluster = pymongo.MongoClient(uri)
db = cluster["Fetch"]
db["points"].drop()
point_collection = db["points"]

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
    remaining = amount                              # used to check if we can pay in full
    paid_in_full = False                            # boolean of whether there's enough points

    for transaction in points_list:
        transaction_list.append(transaction)
        points = transaction["points"]
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
        # print("Paid for with", return_list)
        return return_list
    else:
        end_str = ""
        if payer:
            end_str = " from " + payer
        return [{"error": "Not Enough Points. Missing "+ str(remaining)+ " points" + end_str}]

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
        print(create_transaction(amount, payer, timestamp))


if __name__ == "__main__":
    transaction_history = [
        {"payer": "DANNON", "points": 1000, "timestamp": "2020-11-02T14:00:00Z", },
        {"payer": "UNILEVER", "points": 200, "timestamp": "2020-10-31T11:00:00Z", },
        {"payer": "DANNON", "points": -200, "timestamp": "2020-10-31T15:00:00Z", },
        {"payer": "MILLER COORS", "points": 10000, "timestamp": "2020-11-01T14:00:00Z", },
        {"payer": "DANNON", "points": 300, "timestamp": "2020-10-31T10:00:00Z", },
    ]
    multitransactions(transaction_history)
    print(spend_points(5000))
    print(balance())
    
    # test_cases = [[300, "unknown_user"], [999900, "lol"],[99999], [5500],]
    # for test in test_cases:
    #     amount = test[0]
    #     user = None
    #     if len(test) == 2:
    #         user = test[1]
    #     print(amount, user)
    #     print(spend_points(amount, user))