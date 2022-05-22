import datetime
from requests import get

API_KEY = '2ce45601-9a7d-4b94-818f-b87949adff0e'
DEFAULT_CONVERT = 'USD'
DEFAULT_START = datetime.datetime.strptime("2013-4-28", "%Y-%m-%d")
DEFAULT_END = datetime.datetime.today()
DEFAULT_OFFSET = 'd'


def format_date(json_date):
    split = json_date.split('T')
    date = split[0]
    time = split[1].split('.')[0]

    return "[" + date + ", " + time + "]"


# Downloads the data of the web page.
def get_url_data(url):
    try:
        response = get(url)
        return response
    except Exception as e:
        error_msg(e)


# Error handling
def json_error_handling(json_data):
    status = json_data["status"]
    if status["error_code"] != 0:
        raise Exception(status["error_message"])


def error_msg(e):
    if hasattr(e, "message"):
        print("Error:", e.message)
    else:
        print("Error:", e)
