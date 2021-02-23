import time

classification = {"a": "Good",
                  "b":"Good"}

def classify(data):
    time.sleep(4)
    return classification.get(data) if classification.get(data) else "Bad"