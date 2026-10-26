# Performance testing recipe: Python

Common choice: Locust (load scripts in Python). Use what the project already has.

## Locust user

```python
from locust import HttpUser, task, between

class Buyer(HttpUser):
    wait_time = between(2, 5)                     # think time

    def on_start(self):
        self.client.headers["Authorization"] = f"Bearer {get_token()}"

    @task(3)
    def create_and_pay(self):
        with self.client.post("/orders", json={"sku": f"SKU-{uuid.uuid4()}", "quantity": 1},
                              catch_response=True, name="create order") as res:
            if res.status_code != 201:
                res.failure(f"status {res.status_code}")
                return
            order_no = res.json()["orderNo"]
        self.client.post(f"/orders/{order_no}/pay", name="pay")

    @task(1)
    def browse(self):
        self.client.get("/products?page=1", name="browse")
```

Run without the UI for a pipeline: `locust -f locustfile.py --headless -u 200 -r 10 -t 20m --host $BASE_URL --csv results`.

Locust users are a closed model by default. For a target arrival rate, use a custom load shape, or report the achieved throughput next to the latency.
