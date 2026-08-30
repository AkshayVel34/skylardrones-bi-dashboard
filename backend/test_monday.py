from monday_client import monday_request

print("Starting Monday API test...")


query = """
query {
    me {
        id
        name
        email
    }
}
"""


try:

    print("Sending request to monday.com...")

    data = monday_request(query)

    print("=" * 50)
    print("SUCCESS: Connected to monday.com")
    print("=" * 50)

    print("User ID:", data["me"]["id"])
    print("Name:", data["me"]["name"])
    print("Email:", data["me"]["email"])

except Exception as e:

    print("=" * 50)
    print("ERROR: Could not connect to monday.com")
    print("=" * 50)

    print("Error:", e)