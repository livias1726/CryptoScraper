import datetime

from requests import get

API_KEY = '2ce45601-9a7d-4b94-818f-b87949adff0e'
DEFAULT_CONVERT = 'USD'
DEFAULT_START = '2013-4-28'
DEFAULT_END = datetime.date.today()


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
        if hasattr(e, "message"):
            print("Error message (get_url_data) :", e.message)
        else:
            print("Error message (get_url_data) :", e)
        raise e
