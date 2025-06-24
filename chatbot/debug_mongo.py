from pymongo import MongoClient
from services import config
import bcrypt
import pprint

# Connect to MongoDB
print("Connecting to MongoDB...")
client = MongoClient(config.MONGO_URI)
db = client.get_database()

# Check connection
try:
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("MongoDB connection successful!")
except Exception as e:
    print(f"MongoDB connection failed: {str(e)}")
    exit(1)

# List collections
print("\nCollections in database:")
collections = db.list_collection_names()
for collection in collections:
    print(f"- {collection}")

# Check users collection
print("\nUsers in database:")
users = list(db.users.find())
if not users:
    print("No users found in the database.")
else:
    for user in users:
        # Don't print the full password hash for security
        password = user.get('password', '')
        user['password'] = f"{password[:10]}..." if password else "None"
        pprint.pprint(user)

# Create a test user with known credentials
print("\nCreating a test user...")
email = "test@example.com"
password = "password123"
username = "TestUser"

# Check if user already exists
existing_user = db.users.find_one({"email": email})
if existing_user:
    print(f"User {email} already exists.")
else:
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create user
    user_data = {
        "_id": "test123",
        "email": email,
        "password": password_hash,
        "name": username,
        "username": username
    }
    
    result = db.users.insert_one(user_data)
    print(f"User created with ID: {result.inserted_id}")
    
    # Verify the user was created
    created_user = db.users.find_one({"_id": "test123"})
    if created_user:
        print("User successfully created and retrieved!")
    else:
        print("Failed to retrieve the created user.")

# Test password verification
print("\nTesting password verification...")
test_user = db.users.find_one({"email": email})
if test_user:
    stored_password = test_user['password']
    provided_password = password
    
    # Verify password
    is_valid = bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
    print(f"Password verification result: {is_valid}")
else:
    print(f"Could not find user with email {email}") 