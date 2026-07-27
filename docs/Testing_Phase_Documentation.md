# Testing Phase — TrainLink System

---

## Test 1: Unit Testing

**Test name:** Unit Testing

**Objective:** Verify that each model and serializer in the system works correctly on its own.

**Testing method:** Automated tests written using Django `TestCase`. Each test creates test data, runs a check, and compares the result with expected values.

**Test result:** 79 tests passed out of 79 (100%).

**Screenshot(s) showing the testing process or output:**
[Screenshot: terminal running `python manage.py test` showing "Ran 79 tests ... OK"]

---

## Test 2: Functional Testing

**Test name:** Functional Testing

**Objective:** Verify that each API endpoint returns the correct response.

**Testing method:** Sent HTTP requests to each endpoint using `Invoke-RestMethod` in PowerShell and checked the status code (200 for success, 400 for bad request, 401 for unauthorized).

**Test result:** All endpoints responded correctly.

**Screenshot(s) showing the testing process or output:**
[Screenshot: terminal showing API responses with status codes]

---

## Test 3: Integration Testing

**Test name:** Integration Testing

**Objective:** Verify that frontend pages connect to the backend API and display real data.

**Testing method:** Started the Django server (`python manage.py runserver`), opened each page in the browser, and confirmed that data from the database appears on the page.

**Test result:** 33 out of 34 pages loaded with real data successfully.

**Screenshot(s) showing the testing process or output:**
[Screenshot: browser showing a page with real data from the API]

---

## Test 4: System Testing

**Test name:** System Testing

**Objective:** Verify that the full system works end-to-end: registration, login, search, and applying for internships.

**Testing method:** Simulated the complete user workflow through the API: homepage stats → login → token generation → profile access → internship search → apply. Each step tested as a sequence.

**Test result:** All steps completed successfully. The system handles the full workflow without errors.

**Screenshot(s) showing the testing process or output:**
[Screenshot: terminal showing "10/10 Tests PASSED" for full workflow]

---
