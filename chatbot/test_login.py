from utils import auth_utils

# Test login with the test user we created
email = "test@example.com"
password = "password123"

print(f"Testing login for {email}...")
result, error = auth_utils.login_user(email, password)

if error:
    print(f"Login failed: {error}")
else:
    print("Login successful!")
    print(f"User ID: {result['id']}")
    print(f"Email: {result['email']}")
    print(f"Name: {result['name']}")
    print(f"Token: {result['token'][:20]}...")

# Test login with the mongo user we created earlier
email = "mongo@example.com"
password = "password123"

print(f"\nTesting login for {email}...")
result, error = auth_utils.login_user(email, password)

if error:
    print(f"Login failed: {error}")
else:
    print("Login successful!")
    print(f"User ID: {result['id']}")
    print(f"Email: {result['email']}")
    print(f"Name: {result['name']}")
    print(f"Token: {result['token'][:20]}...") 