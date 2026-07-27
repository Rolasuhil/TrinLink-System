# Functional Testing

---

**Test Name:** Functional Testing

**Objective:** To verify that each API endpoint in the TrainLink system returns the correct response for valid and invalid requests. This includes testing public endpoints (no auth required), authenticated endpoints (JWT required), login/register endpoints, and protected admin routes.

**Testing Method:** Black Box Testing by sending HTTP requests to each API endpoint using PowerShell's `Invoke-RestMethod` and validating the response status code and data format. Endpoints tested include:
1. GET /api/admin-panel/public-stats/ (Public)
2. GET /api/internships/ (Public)
3. GET /api/internships/categories/ (Public)
4. POST /api/auth/login/ (Public)
5. GET /api/auth/profile/ (Protected - JWT required)
6. GET /api/admin-panel/dashboard/ (Protected - Admin JWT)
7. POST /api/auth/login/ with wrong password (Invalid)
8. POST /api/auth/login/ with wrong email (Invalid)

**Test Result:** All 8 functional tests passed. Each endpoint returned the expected HTTP status code (200 OK for valid requests, 400 Bad Request for invalid data, 401 Unauthorized for missing token). The login endpoint correctly issued JWT tokens for valid credentials and rejected invalid ones.

**Screenshot(s) showing the testing process or output:**
[Screenshot: Terminal output showing API responses - 200 OK for valid endpoints, 400/401 for invalid requests]

---
