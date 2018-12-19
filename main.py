import os  # os.sep
import sys  # sys.exit
import subprocess
from threading import Thread
import secrets
import re

def runQuery(worker_username, worker_password, lonlat, start_date, end_date, log):
    cmd = './dhusget.sh -u ' + str(worker_username) + ' -p ' + str(worker_password) + ' -T GRD -m "Sentinel-1" -c "' + str(lonlat) + '" -S ' + start_date + ' -E ' + end_date
    subprocess.call(cmd, stdout=log, stderr=log, shell=True)

def runWorker(worker_username, worker_password, lonlat, start_date, end_date, max, log):
    cmd = './dhusget.sh -u ' + str(worker_username) + ' -p ' + str(worker_password) + ' -T GRD -m "Sentinel-1" -c "' + str(lonlat) + '" -S ' + start_date + ' -E ' + end_date + ' -l 1 -P ' + page + ' -o product -O ' + dir_path + ' -w 5 -W 10'
    subprocess.call(cmd, stdout=log, stderr=log, shell=True)

def runUpload(dir_path, log):
    cmd = "git status -s | grep '?? " + dir_path + "' | awk '{ print $2 }' | xargs git add" 
    subprocess.call(cmd, stdout=log, stderr=log, shell=True)
    cmd = "git commit 'add file'" 
    subprocess.call(cmd, stdout=log, stderr=log, shell=True)
    cmd = "git push" 
    subprocess.call(cmd, stdout=log, stderr=log, shell=True)

def get_total_results(dir_path):
    cmd = "cat " + dir_path + "/OSquery-result.xml | grep 'subtitle'"
    out = subprocess.call(cmd, stdout=subprocess.PIPE, shell=True)
    out = out.stdout.read()
    p = re.compile("of (.*) total")
    p.search(out)
    return _.group(1)

def main():
    lonlat = "-6.117176708154047,35.429154357361384:-5.998938062810441,35.579892441113685" #morocco, allysah
    
    #YYYY-MM-DDThh:mm:ss.cccZ
    start_2014 = "2014-01-01T00:00:00.000Z"
    end_2014 = "2014-12-31T23:59:59.000Z"

    start_2015 = "2015-01-01T00:00:00.000Z"
    end_2015 = "2015-12-31T23:59:59.000Z"

    start_2016 = "2016-01-01T00:00:00.000Z"
    end_2016 = "2016-12-31T23:59:59.000Z"

    start_2017 = "2017-01-01T00:00:00.000Z"
    end_2017 = "2017-12-31T23:59:59.000Z"

    # ommit './'
    dir_path_2014 = "morocco/2014"
    dir_path_2015 = "morocco/2015"
    dir_path_2016 = "morocco/2016"
    dir_path_2017 = "morocco/2017"
   
    query_log = open('query_log.txt', 'r')
    worker_log = open('worker_log.txt', 'r')
    upload_log = open('upload_log.txt', 'r')

    runQuery(secrets.worker1_username, secrets.worker1_password, lonlat, start_2014, end_2014, query_log)
    max2014 = get_total_results(".")
    runQuery(secrets.worker2_username, secrets.worker2_password, lonlat, start_2015, end_2015, query_log)
    max2015 = get_total_results(".")
    #thread_2014 = Thread(target=runWorker, args=(secrets.worker1_username, secrets.worker1_password, lonlat, )) 

    #server.start()

if __name__ == "__main__":
    main()