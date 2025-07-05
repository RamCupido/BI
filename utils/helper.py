def get_or_insert_dim(cursor, table, unique_cols, values, id_col):
    condition = ' AND '.join(f"{col} = ?" for col in unique_cols)
    cursor.execute(f"SELECT {id_col} FROM {table} WHERE {condition}", values)
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        cols_str = ', '.join(unique_cols)
        q_marks = ', '.join('?' for _ in values)
        cursor.execute(f"INSERT INTO {table} ({cols_str}) VALUES ({q_marks})", values)
        cursor.connection.commit()
        return cursor.execute("SELECT SCOPE_IDENTITY()").fetchone()[0]
