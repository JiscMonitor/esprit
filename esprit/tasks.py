from esprit import raw, models

def copy(source_conn, source_type, target_conn, target_type, limit=None, batch_size=1000, method="POST", q=None):
    if q is None:
        q = models.Query.match_all()
    batch = []
    for r in iterate(source_conn, source_type, q, page_size=batch_size, limit=limit, method=method):
        batch.append(r)
        if len(batch) >= batch_size:
            print "writing batch of", len(batch)
            resp = raw.bulk(target_conn, target_type, batch)
            batch = []
    if len(batch) > 0:
        print "writing batch of", len(batch)
        resp = raw.bulk(target_conn, target_type, batch)

def iterate(conn, type, q, page_size=1000, limit=None, method="POST"):
    q["size"] = page_size
    q["from"] = 0
    if "sort" not in q: # to ensure complete coverage on a changing index, sort by id is our best bet
        q["sort"] = [{"id" : {"order" : "asc"}}]
    counter = 0
    while True:
        # apply the limit
        if limit is not None and counter >= int(limit):
            break
        
        res = raw.search(conn, type=type, query=q, method=method)
        rs = raw.unpack_result(res)
        
        if len(rs) == 0:
            break
        for r in rs:
            # apply the limit (again)
            if limit is not None and counter >= int(limit):
                break
            counter += 1
            yield r
        q["from"] += page_size

