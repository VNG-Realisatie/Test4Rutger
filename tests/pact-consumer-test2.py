


import requests
from pactman import Consumer, Provider

pact = Consumer('Consumer').has_pact_with(Provider('Provider'), version="3.0.0", pact_dir="pacts")

def test_interaction():
    expected = {
      'username': 'UserA',
      'id': 123,
      'groups': ['Editors']
    }

    pact.given("UserA exists and is not an administrator") \
        .upon_receiving("a request for UserA") \
        .with_request("get", "/users", query={"username": "userA"}) \
        .will_respond_with(200, body=expected)


    with pact:
        requests.get("/".join([pact.uri, 'users']), params={"username": "userA"})
