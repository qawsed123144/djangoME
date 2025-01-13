from locust import HttpUser, task, between
from random import randint


class PTestUser(HttpUser):
    wait_time = between(1, 5)

    @task(2)
    def view_products(self):
        self.client.get("/store/products", name='/store/products')

    @task(4)
    def view_product(self):
        product_id = randint(1,4)
        self.client.get(f"/store/products/{product_id}", name='/store/products/:id')
        
    @task(1)
    def create_product(self):
        product_id = randint(1,4)
        self.client.post(f"/store/carts/{self.cart_id}/cartitem_set/", name='/store/carts/{cart_id}/cartitem_set/',
                         json={"product": product_id, "quantity": 1})
        
    def on_start(self):
        response =self.client.post('/store/carts/')
        result = response.json()
        self.cart_id= result["id"]