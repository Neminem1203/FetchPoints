import importlib
import requests
app = importlib.import_module("app")
PORT = app.PORT
SPEND_ROUTE = app.SPEND_ROUTE
GIVE_ROUTE = app.GIVE_ROUTE
BAL_ROUTE = app.BAL_ROUTE

TEST_URL = "http://localhost:" + str(PORT)
INITIAL_BALANCE = {'DANNON': 1100, 'UNILEVER': 200, 'MILLER COORS': 10000}
spend_test_cases = ["?amount=9000000", "?amount=5000", "?amount=a", ""]
spend_outputs = [
    [{'error': 'Not Enough Points. Missing 8988700 points'}, 400],          # not enough points
    [[{'DANNON': -100}, {'UNILEVER': -200}, {'MILLER COORS': -4700}],200],  # valid transaction
    [{'error': 'Amount needs to be a number'},400],                         # not a number
    [{'error': 'Missing amount'},400],                                      # no arg for amount
]
give_test_cases = ["?amount=9000&payer=NewUser", "?amount=9000", '?payer=UNILEVER', "","?amount=a&payer=tester"]
give_outputs = [
    [[{"NewUser": "9000"}],200],                                            # valid give transaction
    [{"error": ["Payer is missing"]},400],                                  # missing payer
    [{"error": ["Amount is missing"]},400],                                 # missing amount
    [{"error": ["Amount is missing", "Payer is missing"]},400],             # missing both,
    [{"error": "Amount needs to be a number"}, 400]                         # invalid type for amount
]

route_dict = {
    "Spend"     : SPEND_ROUTE,
    "Give"      : GIVE_ROUTE,
    "Balance"   : BAL_ROUTE
}


def test_route(route, queries, outputs):
    test_url = TEST_URL+route_dict[route]
    for query_ind, query in enumerate(queries):
        test_str = f'{route} Test {query_ind}'
        resp = requests.get(test_url+query)
        resp_json = resp.json()
        resp_status_code = resp.status_code
        expected_resp, expected_status_code = outputs[query_ind]
        assert(resp_json == expected_resp), f'{test_str} Failed: Incorrect Ouptut'
        assert(resp_status_code == expected_status_code), f'{test_str} Failed: Incorrect Status Code'
        print(f'{test_str} passed')

def test_cases():
    app.reset_db()
    print("Database Reset")
    initial_balance = requests.get(TEST_URL+BAL_ROUTE).json()
    assert(initial_balance == INITIAL_BALANCE), "Initial Balance Test Failed"
    print("Initial Balance Test Passed")
    # Test Spend Route
    test_route("Spend", spend_test_cases, spend_outputs)
    # # Give function
    test_route("Give", give_test_cases, give_outputs)
    print("All Tests Passed")

if __name__ == "__main__":
    test_cases()