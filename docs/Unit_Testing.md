# Unit Testing

---

**Test Name:** Unit Testing

**Objective:** To verify that each individual component (models, serializers, views) of the TrainLink system functions correctly in isolation. This includes testing database models for correct field storage, default values, constraints, and relationships; testing serializers for valid data acceptance and rejection; and testing custom user model behavior.

**Testing Method:** White Box Testing using Django's built-in `TestCase` framework. Automated test cases were written for each of the 7 Django apps (accounts, internships, community, messaging, admin_panel, ai_engine, performance). Each test creates test data, performs operations, and uses assertions (assertEqual, assertTrue, assertRaises, etc.) to verify expected outcomes. Tests were executed using the command: `python manage.py test`

**Test Result:** All 79 unit tests passed successfully. Breakdown by app:
- accounts: 24/24 passed
- internships: 14/14 passed
- community: 8/8 passed
- messaging: 14/14 passed
- admin_panel: 3/3 passed
- ai_engine: 5/5 passed
- performance: 10/10 passed

**Screenshot(s) showing the testing process or output:**
[Screenshot: Terminal output showing "Ran 79 tests in 4.721s OK"]

---
