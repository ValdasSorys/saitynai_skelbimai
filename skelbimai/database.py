def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def check_user(cursor, id):
    cursor.execute("SELECT is_deleted FROM public.user WHERE id = %s", [id])
    row = dictfetchall(cursor)
    if len(row) == 0:
        return False
    if row[0]["is_deleted"] == 1:
        return False
    return True