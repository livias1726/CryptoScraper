def format_date(json_date):
    split = json_date.split('T')
    date = split[0]
    time = split[1].split('.')[0]

    return "[" + date + ", " + time + "]"
