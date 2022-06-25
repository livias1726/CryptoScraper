import datetime
from requests import get

API_KEY = '2ce45601-9a7d-4b94-818f-b87949adff0e'
DEFAULT_CONVERT = 'USD'
DEFAULT_START = datetime.datetime.strptime("2013-4-28", "%Y-%m-%d")
DEFAULT_END = datetime.datetime.today() - datetime.timedelta(days=1)
DEFAULT_OFFSET = 'd'
DEFAULT_STYLE = 'bmh'


# 'bmh', 'ggplot', 'seaborn'


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


def set_size(width, fraction=1):
    # Width of figure
    fig_width_pt = width * fraction

    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    golden_ratio = (5 ** 0.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio

    return fig_width_in, fig_height_in


def get_moving_average(data, n):
    i = 0
    # Initialize an empty list to store moving averages
    moving_averages = []

    # Loop through the data
    while i < len(data) - n + 1:
        # Store elements from i to i+n
        window = data[i: i + n]

        # Compute the average
        window_average = round(sum(window) / n, 2)

        # Store the average
        moving_averages.append(window_average)

        # Slide window
        i += 1

    return moving_averages
