from db.dbORM import *


def getFees(cartypeId, count, totalFee):
    count = int(count)
    totalFee = int(totalFee)
    cartypeId = int(cartypeId)
    ct = Cartype.query.filter_by(id=cartypeId).first()
    prefer = ct.Preferential
    if prefer:
        if prefer.status == "normal":
            if prefer.mincount and not prefer.cutfee:
                if count >= prefer.mincount:
                    cutfee = ct.price
                    if prefer.multicount == 1:
                        cutfee = cutfee * count
                    if prefer.maxcutfee:
                        if cutfee > prefer.maxcutfee:
                            cutfee = prefer.maxcutfee
                    newfee = totalFee - cutfee
                    if newfee < 0:
                        newfee = 0

                    return {"name": prefer.name, 'preferid': prefer.id, "oldfee": totalFee, "cutfee": cutfee,
                            "newfee": newfee, 'isprefer': True}
                else:
                    return {"name": "", 'preferid': -1, "oldfee": totalFee, "cutfee": 0, "newfee": totalFee,
                            'isprefer': False}

            else:
                return {"name": "", 'preferid': -1, "oldfee": totalFee, "cutfee": 0, "newfee": totalFee,
                        'isprefer': False}
        else:
            return {"name": "", 'preferid': -1, "oldfee": totalFee, "cutfee": 0, "newfee": totalFee, 'isprefer': False}
    else:
        return {"name": "", 'preferid': -1, "oldfee": totalFee, "cutfee": 0, "newfee": totalFee, 'isprefer': False}
