from apscheduler.scheduler import Scheduler
import time
import sys
import os
sys.path.insert(1, '/home/fabian/cos/scrapi/')
from scrapers.plos import consume, parse


def main():
    config = {
        'apscheduler.jobstores.file.class': 'apscheduler.jobstores.shelve_store:ShelveJobStore',
        'apscheduler.jobstores.file.path': '/tmp/dbfile'
    }
    sched = Scheduler(config)

    sched.add_cron_job(consume.consume, day_of_week='mon-fri', hour=23, minute=59)
    sched.start()

    print('Press Ctrl+{0} to exit'.format('C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()  # Not strictly necessary if daemonic mode is enabled but should be done if possibleisched.start()


def walk():
    for dirname, dirnames, filenames in os.walk('../archive/PLoS/'):
        # print path to all filenames.
        for filename in filenames:
            if 'raw' in filename:
                with open(os.path.join(dirname, filename), 'r') as f:
                    parse.parse(f.read(), dirname)

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if '.git' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('.git')

if __name__ == '__main__':
    consume.consume()
    walk()
