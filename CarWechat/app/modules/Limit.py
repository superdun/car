from ..models.dbORM import *
from datetime import datetime

def dateCounvert(datetimeStr):
     #    2018-05-31T21:29:42
     if len(datetimeStr)==16:
        return datetime.strptime(datetimeStr.split('.')[0], '%Y-%m-%dT%H:%M')
     elif len(datetimeStr)>=19:
        return datetime.strptime(datetimeStr.split('.')[0], '%Y-%m-%dT%H:%M:%S')
     else:
        return datetime.strptime(datetimeStr.split('T')[0], '%Y-%m-%d')


def checkLimit(cartypeId, count,book_at=""):
    cartypeId = int(cartypeId)
    count = int(count)
    ct = Cartype.query.filter_by(id=cartypeId).first()
    limit = ct.Limit
    if limit:
        start_at = limit.start_at
        end_at = limit.end_at
        mincount = limit.mincount
        if not mincount:
            mincount=0
        maxcount = limit.maxcount
        if not maxcount:
            maxcount = float('inf')
        if book_at=="":
            checkedDatetime = datetime.now()
        else:
            checkedDatetime = dateCounvert(book_at)
        if checkedDatetime > start_at and checkedDatetime < end_at and (count < mincount or count > maxcount):
            return {'limit': True, 'msg': limit.name}
        else:
            return {'limit': False, 'msg': ""}

    else:
        return {'limit': False, 'msg': ""}
