def select_from_table(attributes, table, join, conditions, order_by):
    # Select
    res = "SELECT "
    dim = len(attributes)-1
    for i in range(dim):
        res = res + attributes[i] + ", "
    res = res + attributes[dim]

    # From
    res = res + " FROM '%s'" % table

    # Join
    if join is not None:
        res = res + " JOIN " + join['table']
        if type(join['attribute']) is list:
            res = res + " ON " + join['attribute'][0] + "=" + join['attribute'][1]
        else:
            res = res + " USING (" + join['attribute'] + ")"

    # Where
    if conditions is not None:
        res = res + " WHERE "
        dim = len(conditions)-1
        keys = list(conditions)
        for i in range(dim):
            res = res + keys[i] + "='" + conditions[keys[i]] + "' AND "
        res = res + keys[dim] + "='" + conditions[keys[dim]] + "'"

    # Order by
    if order_by is not None:
        res = res + " ORDER BY %s" % order_by

    return res


def check_if_table_exists(table):
    return "SELECT count(*) from sqlite_master WHERE type = 'table' AND name = '%s'" % table


def create_table(name, columns, pks):
    res = "CREATE TABLE %s (" % name

    dim = len(columns)-1
    keys = list(columns)

    for i in range(dim):
        res = res + keys[i] + " " + columns[keys[i]] + ", "
    res = res + keys[dim] + " " + columns[keys[dim]]

    # Primary Keys
    if pks is not None:
        res = res + ", PRIMARY KEY("
        dim = len(pks)-1
        for i in range(dim):
            res = res + pks[i] + ", "
        res = res + pks[dim] + "))"
    else:
        res = res + ")"

    return res


def insert_into_table(name, dim):
    res = "INSERT INTO '%s' VALUES (" % name
    for i in range(dim-1):
        res = res + "?,"
    res = res + "?)"
    return res


def _validate_input(param):
    if type(param) is str:
        idxs = [i for i, c in enumerate(param) if c == "'"]
        for idx in idxs:
            param = param[:idx] + param[idx+1:]
    else:
        param = str(param)

    return param


def update_table(table, conditions, params):
    # Update
    res = "UPDATE '%s'" % table

    # Set
    res = res + " SET "
    dim = len(params) - 1
    keys = list(params)
    for i in range(1, dim):
        valid_value = _validate_input(params[keys[i]])
        res = res + keys[i] + " = '" + valid_value + "', "

    valid_value = _validate_input(params[keys[dim]])
    res = res + keys[dim] + " = '" + valid_value + "'"

    # Where
    res = res + " WHERE "
    dim = len(conditions) - 1
    keys = list(conditions)
    for i in range(dim):
        res = res + keys[i] + " = '" + str(conditions[keys[i]]) + "' AND "
    res = res + keys[dim] + " = '" + str(conditions[keys[dim]]) + "'"

    return res
