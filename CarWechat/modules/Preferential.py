from db.dbORM import *


def getFees(cartypeId, count, totalFee):
    count = int(count)
    totalFee = int(totalFee)
    cartypeId = int(cartypeId)
    ct = Cartype.query.filter_by(id=cartypeId).first()
    prefer = ct.Preferential
    cutfee = 0
    newfee = totalFee
    isprefer = False
    if prefer:
        if prefer.status == "normal":
            if prefer.mincount and not prefer.cutfee:
                if count >= prefer.mincount:
                    isprefer = True
                    cutfee = ct.price
                    if prefer.multicount == 1:
                        cutfee = cutfee * count
                    if prefer.maxcutfee:
                        if cutfee > prefer.maxcutfee:
                            cutfee = prefer.maxcutfee
                    newfee = totalFee - cutfee
                    if newfee < 0:
                        newfee = 0
            if prefer.discount:
                newfee = newfee * prefer.discount
                cutfee = totalFee - newfee

    if isprefer:
        return {"name": prefer.name, 'preferid': prefer.id, "oldfee": totalFee, "cutfee": cutfee,
                "newfee": newfee, 'isprefer': True}

    else:
        return {"name": "", 'preferid': -1, "oldfee": totalFee, "cutfee": 0, "newfee": totalFee, 'isprefer': False}
