
import pytest
from pactman import Consumer, Provider, Like, Term
import requests
from requests.exceptions import HTTPError

pact = Consumer("ProductConsumer").has_pact_with(Provider("ProductProvider"), pact_dir="pacts")

def test_interaction():
    pact.given("some data exists").upon_receiving("a request") \
        .with_request("get", "/", query={"foo": ["bar"]}).will_respond_with(200)
    with pact:
        requests.get(pact.uri, params={"foo": ["bar"]})
        
