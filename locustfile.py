from locust import HttpUser, task

class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/products")
        self.client.post("/create")
        self.client.post("/buy-products")
        self.client.get("/categories")
        self.client.post("/category")
