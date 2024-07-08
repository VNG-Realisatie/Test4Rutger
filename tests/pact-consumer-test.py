import pytest
from pact import Consumer, Provider, Like, Term
import requests
from requests.exceptions import HTTPError

@pytest.fixture(scope="module")
def product_api_client():
    class ProductApiClient:
        def __init__(self, base_url):
            self.base_url = base_url

        def get_all_products(self):
            response = requests.get(f'{self.base_url}/products')
            return {'status_code': response.status_code, 'body': response.json()}

        def create_product(self, product):
            response = requests.post(f'{self.base_url}/products', json=product)
            return {'status_code': response.status_code, 'body': response.json()}

        def get_product(self, product_id):
            response = requests.get(f'{self.base_url}/products/{product_id}')
            if response.status_code == 404:
                raise HTTPError(response=response)
            return {'status_code': response.status_code, 'body': response.json()}

    return ProductApiClient(base_url="http://localhost:1234")

@pytest.fixture(scope="module")
def pact():
    pact = Consumer("ProductConsumer").has_pact_with(Provider("ProductProvider"), pact_dir="pacts")
    pact.start_service()
    yield pact
    pact.stop_service()

def test_get_all_products(product_api_client, pact):
    expected_products = [
        {"id": 1, "name": "Product 1", "description": "Description 1", "price": 10.0},
        {"id": 2, "name": "Product 2", "description": "Description 2", "price": 20.0}
    ]

    (pact
     .given("products exist")
     .upon_receiving("a request for all products")
     .with_request("get", "/products")
     .will_respond_with(200, body=expected_products))

    with pact:
        response = product_api_client.get_all_products()
        assert response['status_code'] == 200
        assert response['body'] == expected_products

def test_create_product(product_api_client, pact):
    new_product = {
        "name": "New Product",
        "description": "A brand new product",
        "price": 15.0
    }
    expected_response = {
        "id": 123,
        "name": Like("New Product"),
        "description": "A brand new product",
        "price": Like(15.0)
    }

    (pact
     .given("the API is ready to create a new product")
     .upon_receiving("a request to create a new product")
     .with_request("post", "/products", body=new_product)
     .will_respond_with(201, body=expected_response))

    with pact:
        response = product_api_client.create_product(new_product)
        assert response['status_code'] == 201
        assert 'id' in response['body']
        assert isinstance(response['body']['id'], int)
        assert response['body']['name'] == new_product['name']
        assert response['body']['description'] == new_product['description']
        assert response['body']['price'] == new_product['price']

def test_get_product(product_api_client, pact):
    product_id = 1
    expected_product = {
        "id": 1,
        "name": "Product 1",
        "description": "Description 1",
        "price": 10.0
    }

    (pact
     .given(f"a product with id {product_id} exists")
     .upon_receiving(f"a request for product with id {product_id}")
     .with_request("get", f"/products/{product_id}")
     .will_respond_with(200, body=expected_product))

    with pact:
        response = product_api_client.get_product(product_id)
        assert response['status_code'] == 200
        assert response['body'] == expected_product

def test_get_nonexistent_product(product_api_client, pact):
    product_id = "string_identifier"

    (pact
     .given(f"a product with id {product_id} does not exist")
     .upon_receiving(f"a request for product with id {product_id}")
     .with_request("get", f"/products/{product_id}")
     .will_respond_with(404))

    with pact:
        with pytest.raises(HTTPError) as exc_info:
            product_api_client.get_product(product_id)
        assert exc_info.value.response.status_code == 404
