from apscheduler.scheduler import Scheduler
import time
import os
import requests
import yaml

def load_config(config_file):
    with open(config_file) as f:
        info = yaml.load(f)
    return info

def main(config_file):
    info = load_config(config_file)

    day_of_week = info['days']
    hour = info['hour']
    minute = info['minute']

    config = {
        'apscheduler.jobstores.file.class': info['scheduler-config']['class'],
        'apscheduler.jobstores.file.path': info['scheduler-config']['path']
    }
    sched = Scheduler(config)

    sched.add_cron_job(run_scraper, day_of_week=day_of_week, hour=hour, minute=minute)

    sched.start()

    print('Press Ctrl+{0} to exit'.format('C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        sched.shutdown()  # Not strictly necessary if daemonic mode is enabled but should be done if possibleisched.start()

def run_scraper(config_file):
    info = load_config(config_file)
    # does this need to be added to the yaml file? 
    r = requests.post(info['url'] + 'consume')
    # print r
    for dirname, dirnames, filenames in os.walk('../archive/'+ str(info['directory']) + '/'):
        # print path to all filenames.
        for filename in filenames:
            if 'raw' in filename:
                with open(os.path.join(dirname, filename), 'r') as f:
                    payload = {'doc': f.read(), 'timestamp': dirname.split('/')[-1]}
                    requests.post(info['url'] + 'process', params=payload)  # TODO

if __name__ == '__main__':
    run_scraper('manifests/plos-manifest.yml')
    # run_scraper('manifests/scitech-manifest.yml')
