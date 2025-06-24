from utils import auth_utils

# Create a test user
result, error = auth_utils.register_user('mongo@example.com', 'password123', 'MongoUser')

if error:
    print(f"Error creating user: {error}")
else:
    print(f"User created successfully!")
    print(f"Email: mongo@example.com")
    print(f"Password: password123")
    print(f"Token: {result['token']}") 