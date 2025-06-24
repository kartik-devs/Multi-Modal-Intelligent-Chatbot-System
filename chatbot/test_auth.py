from utils import auth_utils

# Create a test user
result, error = auth_utils.register_user('test@example.com', 'password123', 'TestUser')

if error:
    print(f"Error creating user: {error}")
else:
    print(f"User created successfully!")
    print(f"Email: test@example.com")
    print(f"Password: password123")
    print(f"Token: {result['token']}") 