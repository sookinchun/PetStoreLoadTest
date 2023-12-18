from locust import HttpUser, task, between
from faker import Faker
import json
import time
import logging

fake = Faker()

# Configure the logging settings
logging.basicConfig(filename='locust.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PetstoreUser(HttpUser):
    wait_time = between(1, 5)  # Time between requests
    host = "https://petstore.swagger.io"  # Specify the base host here
    pet_id_counter = 1  # Initialize a counter for pet IDs
    getAPI_results = []  # Initialize an empty list to store GET API results

    @task
    def create_and_get_pet(self):
        # Generate a random pet name
        self.pet_name = fake.name()

        # Create a Pet
        create_payload = {
            "id": self.pet_id_counter,  # Use the current counter value as ID
            "name": self.pet_name,
            "status": "available"
        }
        headers = {'Content-Type': 'application/json'}
        api_name = "Create Pet"

        start_time = time.time()
        response_create = self.client.post("/v2/pet", headers=headers, data=json.dumps(create_payload))
        end_time = time.time()

        duration = end_time - start_time

        log_create = {
            "api_name": api_name,
            "api_status": "success" if response_create.status_code == 200 else "failure",
            "pet_name": self.pet_name,
            "status_code": response_create.status_code,
            "duration_seconds": duration,
            "payload": create_payload,
            "response": response_create.text
        }

        # Log the results
        self.log_request(log_create)

        # Get the Pet
        pet_id = self.pet_id_counter  # Use the same ID as created

        # Customize the name for this specific GET API call
        with self.client.get(f"/v2/pet/{pet_id}", headers=headers, name="Get_API") as response_get:
            start_time = time.time()
            end_time = time.time()
            duration = end_time - start_time

            log_get = {
                "api_name": api_name,
                "api_status": "success" if response_get.status_code == 200 else "failure",
                "pet_name": self.pet_name,
                "status_code": response_get.status_code,
                "duration_seconds": duration,
                "payload": None,  # No payload for GET request
                "response": response_get.text
            }

            # Append the GET API result to the list
            self.getAPI_results.append(log_get)

        # Log the results
        self.log_request(log_get)

        # Increment the pet ID counter for the next iteration
        self.pet_id_counter += 1

    def log_request(self, log_data):
        log_json = json.dumps(log_data, ensure_ascii=False)

        # Log the JSON data to the file
        logger.info(log_json)
