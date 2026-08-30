import os
from dotenv import load_dotenv
from monday_client import monday_request

load_dotenv()


board_id = os.getenv("DEALS_BOARD_ID")


query = """
query ($board_id: ID!) {
    boards(ids: [$board_id]) {

        id
        name
        items_count

        columns {
            id
            title
            type
        }

        items_page(limit: 10) {

            cursor

            items {
                id
                name

                column_values {
                    id
                    text
                    value
                }
            }
        }
    }
}
"""


variables = {
    "board_id": board_id
}


try:

    data = monday_request(query, variables)

    board = data["boards"][0]

    print("=" * 60)
    print("DEALS BOARD")
    print("=" * 60)

    print("Board ID:", board["id"])
    print("Board Name:", board["name"])
    print("Total Items:", board["items_count"])

    print("\nCOLUMNS")
    print("-" * 60)

    for column in board["columns"]:

        print(
            column["id"],
            "|",
            column["title"],
            "|",
            column["type"]
        )

    print("\nFIRST 10 DEALS")
    print("-" * 60)

    for item in board["items_page"]["items"]:

        print(
            item["id"],
            "|",
            item["name"]
        )


except Exception as e:

    print("=" * 60)
    print("ERROR")
    print("=" * 60)

    print(e)