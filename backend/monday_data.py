import os
from dotenv import load_dotenv
from monday_client import monday_request

load_dotenv()


def get_board_items(board_id):

    all_items = []
    cursor = None

    while True:

        query = """
        query ($board_id: ID!, $cursor: String) {

            boards(ids: [$board_id]) {

                items_page(
                    limit: 100
                    cursor: $cursor
                ) {

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
            "board_id": board_id,
            "cursor": cursor
        }

        data = monday_request(query, variables)

        page = data["boards"][0]["items_page"]

        all_items.extend(page["items"])

        cursor = page["cursor"]

        if not cursor:
            break

    return all_items


def get_deals():

    board_id = os.getenv("DEALS_BOARD_ID")

    return get_board_items(board_id)


def get_work_orders():

    board_id = os.getenv("WORK_ORDERS_BOARD_ID")

    return get_board_items(board_id)