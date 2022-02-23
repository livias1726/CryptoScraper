def __parse_data(json_data):
    item_list = json_data
    while 'data' in item_list:
        item_list = item_list['data']
    return item_list


# Gets coin generalities from 'cryptocurrency/map' call
def parse_all_coins(json_data):
    item_list = __parse_data(json_data)
    res = []
    for item in item_list:
        i = {'id': item['id'], 'name': item['name'], 'symbol': item['symbol']}
        res.append(i)
    return res


# Gets category generalities from 'cryptocurrency/categories' call
def parse_all_categories(json_data):
    item_list = __parse_data(json_data)
    res = []
    for item in item_list:
        i = {'id': item['id'], 'name': item['name'], 'num_tokens': item['num_tokens'], 'market_cap': item['market_cap'],
             'volume': item['volume']}
        res.append(i)
    return res


# Gets all coins from a category with 'cryptocurrency/category' call
def parse_category_coins(json_data, cat_id):
    item_list = __parse_data(json_data)
    item_list = item_list['coins']
    res = []
    for item in item_list:
        i = {'coin_id': item['id'], 'cat_id': cat_id}
        res.append(i)
    return res


# Get cryptocurrencies current data on price, volume, volume change in 24h,
# price percentage change in 24h, market capital
def parse_latest_data(json_data, id_list, convert):
    item_list = __parse_data(json_data)
    res = []
    if id_list is not None:
        for c_id in id_list:
            data = item_list[str(c_id)]['quote'][convert]
            res.append({'id': c_id, 'convert': convert,
                        'price': data['price'],
                        'volume_24h': data['volume_24h'],
                        'volume_change_24h': data['volume_change_24h'],
                        'percent_change_24h': data['percent_change_24h'],
                        'market_cap': data['market_cap'],
                        'last_update': data['last_updated']})
    else:
        if type(item_list) is not list:
            item_list = [item_list]
        for item in item_list:
            data = item['quote'][convert]
            i = {'id': item['id'], 'convert': convert,
                 'price': data['price'],
                 'volume_24h': data['volume_24h'],
                 'volume_change_24h': data['volume_change_24h'],
                 'percent_change_24h': data['percent_change_24h'],
                 'market_cap': data['market_cap'],
                 'last_update': data['last_updated']}
            res.append(i)

    return res
