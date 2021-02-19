import sqlite3, os

def mysql(sql):
    path = os.path.dirname(__file__)
    db = sqlite3.connect(f'{path}/msg.db')
    cursor = db.cursor()
    try:
        cursor.execute('''CREATE TABLE qqmsg(
            id      INTEGER         PRIMARY KEY     NOT NULL,
            qqid    INTEGER         NOT NULL,
            gid     INTEGER         NOT NULL,
            msgid   INTEGER         NOT NULL,
            msg     TEXT            NOT NULL,   
            times   DATE       NOT NULL  DEFAULT (datetime('now', 'localtime'))
            )''')
        print('Table created successfully')
    except:
        pass
    for i in ['insert', 'delete']:
        if i in sql:
            try:
                cursor.execute(sql)
                db.commit()
                return True
            except Exception as e:
                print(e)
                db.rollback()
        elif 'select' in sql:
            try :
                cursor.execute(sql)
                results = cursor.fetchall()
                if results:
                    return results
                else:
                    return False
            except Exception as e:
                print(e)
                db.rollback()
    db.close()
