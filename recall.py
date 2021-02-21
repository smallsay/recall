import hoshino
from hoshino import Service
from hoshino.typing import NoticeSession, CQEvent
from .msgsql import mysql

sv = Service('recall', enable_on_default=True, visible=True)

@sv.on_message()
async def get_msg(bot, ev:CQEvent):
    qqid = ev.user_id
    gid = ev.group_id
    msgid = ev.message_id
    msg = ev.message

    sql = f'insert into qqmsg(qqid, gid, msgid, msg) values ({qqid}, {gid}, {msgid}, "{msg}")'

    mysql(sql)

@sv.on_notice('group_recall')
async def recall(session: NoticeSession):
    ss = []
    msgid = session.event.message_id

    if session.event.user_id == hoshino.config.SUPERUSERS[0]:
        print('SUPERUSER PASS')
        return
    if session.event.user_id == session.event.operator_id:
        return

    sql = f'select qqid, msg from qqmsg where msgid = {msgid}'
    result = mysql(sql)
    if not result:
        return
    else:
        for i in result:
            qqid = i[0]
            msg = i[1]
    
    ss.append(f'用户[CQ:at,qq={qqid}]尝试撤回消息:\n')
    ss.append(msg)

    recall_msg = ''.join(ss)
    
    await session.send(recall_msg)

@sv.scheduled_job('cron', minute='*/5')
async def delete():
    sql = 'delete from qqmsg where julianday("now", "localtime") * 1440 - julianday(times) * 1440 > 2;'
    mysql(sql)
    print('删除数据库命令已执行完毕')
