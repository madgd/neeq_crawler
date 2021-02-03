"""
output diff logs

the format is:
op \t type \t pk \t info \t [old_info]

op: db operation, + for add, - for del, m for modify
type: data type, like neeq_rules, neeq_announce etc.
pk: primary key in database
info: json dict contains all data updated
old_info: json dict contains old data
"""
import datetime
import json


diffRootPath = "./log/difflog/"

class DiffLog():
    """
    write diff to log.
    other module can read this log and make updates.
    """

    logfile = None
    diffType = None

    def __init__(self, diffType):
        """
        make a log file if not exist
        """
        if not self.diffType:
            self.diffType = diffType
        if not self.logfile:
            now = '{0:%Y%m%d%H%M}'.format(datetime.datetime.now())
            self.logfile = diffRootPath + self.diffType + '_' + now

    def WriteDiffRow(self, op, pk, info, old_info={}):
        """
        write one diff log
        """
        if op not in ['+', '-', 'm']:
            return False, "op wrong"
        if not pk:
            return False, "pk wrong"
        if not info:
            return False, "info empty"
        if op == 'm' and not old_info:
            return False, "modify op old_info empty"
        with open(self.logfile, 'a') as f:
            f.write("%s\t%s\t%s\t%s\t%s\n" % (op, self.diffType, pk, json.dumps(info, ensure_ascii=False), json.dumps(old_info, ensure_ascii=False)))
        return True, "ok"