from nonebot import get_bot
import hoshino, os, sqlite3
from hoshino import Service
from hoshino.typing import NoticeSession, CQEvent

sv = Service('防撤回', enable_on_default=False, visible=True)
SQL = os.path.expanduser('~/.hoshino/msg.db')

bot = get_bot()

class sql():
    def __init__(self):
        os.makedirs(os.path.dirname(SQL), exist_ok=True)
        self.makesql()

    def con(self):
        return sqlite3.connect(SQL)
    
    def makesql(self):
        try:
            self.con().execute('''CREATE TABLE qqmsg(
            id      INTEGER         PRIMARY KEY     NOT NULL,
            qqid    INTEGER         NOT NULL,
            gid     INTEGER         NOT NULL,
            msgid   INTEGER         NOT NULL,
            msg     TEXT            NOT NULL,   
            times   DATE       NOT NULL  DEFAULT (datetime('now', 'localtime'))
            )''')
        except Exception as e:
            print(e)
    
    def addmsg(self, uid, gid, msgid, msg):
        with self.con() as db:
            sql = f'insert into qqmsg(qqid, gid, msgid, msg) values ({uid}, {gid}, {msgid}, "{msg}")'
            db.execute(sql)

    def qmsg(self, msgid):
        with self.con() as db:
            sql = f'select qqid, gid, msg from qqmsg where msgid = {msgid}'
            result = db.execute(sql)
            for i in result:
                uid = i[0]
                gid = i[1]
                msg = i[2]
            return uid, gid, msg
    
    def delmsg(self):
        with self.con() as db:
            sql = 'delete from qqmsg where julianday("now", "localtime") * 1440 - julianday(times) * 1440 > 2;'
            db.execute(sql)

mysql = sql()

async def get_group_user_info(gid, uid):
    qqinfo = await bot.get_group_member_info(group_id=gid, user_id=uid)
    return qqinfo['card'] or qqinfo['nickname']

@sv.on_message()
async def get_msg(bot, ev:CQEvent):
    uid = ev.user_id
    gid = ev.group_id
    msgid = ev.message_id
    msg = ev.message
    mysql.addmsg(uid, gid, msgid, msg)

@sv.on_notice('group_recall')
async def recall(session: NoticeSession):
    ss = []
    msgid = session.event.message_id

    if session.event.user_id == hoshino.config.SUPERUSERS[0]:
        return
    if session.event.user_id != session.event.operator_id:
        return

    uid, gid, msg = mysql.qmsg(msgid)
    name = await get_group_user_info(gid, uid)
    
    ss.append(f'用户 {name} 撤回消息:\n')
    ss.append(msg)

    recall_msg = ''.join(ss)
    await session.send(recall_msg)

@sv.scheduled_job('cron', minute='*/5')
async def delete():
    mysql.delmsg()
    print('删除数据库命令已执行完毕')
