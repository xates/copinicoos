"""
reusable fixtures are here
"""
import json
import os
import shutil
import logging
import sys
import subprocess
import time
from zipfile import ZipFile
import re

import pytest
from PIL import Image

from copinicoos import InputManager
from copinicoos.input_manager import Args 
from copinicoos import WorkerManager
from copinicoos import Worker
from copinicoos import AccountManager

test_dir = os.path.dirname(os.path.realpath(__file__))
test_data_dir = os.path.join(test_dir, "test_data")
log_dir = os.path.join(test_dir, "copinicoos_logs")

query_txt_path = os.path.join(test_data_dir, "query.txt")
secrets1_json_path = os.path.join(test_data_dir, "secrets1.json")
secrets2_json_path = os.path.join(test_data_dir, "secrets2.json")

def close_all_loggers():
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
        logger.handlers = []

@pytest.fixture(scope="session")
def creds():
    return json.load(open(secrets2_json_path))

@pytest.fixture(scope="session")
def worker_list_2_workers(creds):
    """
    Basic worker for querying total results only
    """
    am = AccountManager()
    am.add_two_workers_per_account(creds["u1"], creds["p1"])
    return am.return_worker_list()

@pytest.fixture(scope="session")
def input_manager_with_2_workers(creds):
    im = InputManager()
    im.account_manager.add_two_workers_per_account(creds["u1"], creds["p1"])
    return im

@pytest.fixture(scope="session")
def query():
    return open(os.path.join(test_data_dir, "query.txt")).read()

@pytest.fixture(scope="session")
def formatted_query():
    return 'https://scihub.copernicus.eu/dhus/search?q=( footprint:\"Intersects(POLYGON((91.45532862800384 22.42016942838278,91.34620270146559 22.43895934481047,91.32598614177974 22.336847270362682,91.4350291249018 22.31804599405974,91.45532862800384 22.42016942838278)))\" ) AND ( (platformname:Sentinel-1 AND producttype:GRD))&format=json'

@pytest.fixture(scope="session")
def formatted_query1():
    return 'https://scihub.copernicus.eu/dhus/search?q=( footprint:\"Intersects(POLYGON((91.45532862800384 22.42016942838278,91.34620270146559 22.43895934481047,91.32598614177974 22.336847270362682,91.4350291249018 22.31804599405974,91.45532862800384 22.42016942838278)))\" ) AND ( (platformname:Sentinel-1 AND producttype:GRD))&format=json&rows=1&start='

@pytest.fixture()
def w_args(formatted_query1):
    args = Args()
    args.query = formatted_query1
    args.total_results = 200
    args.download_location = test_dir
    args.offline_retries = 2
    args.polling_interval = 6
    return args

@pytest.fixture()
def wm_args(formatted_query):
    args = Args()
    args.query = formatted_query
    args.total_results = 200
    args.download_location = test_dir
    args.offline_retries = 2
    args.polling_interval = 6
    return args

@pytest.fixture()
def worker_manager(worker_list_2_workers, wm_args):
    return WorkerManager.init_from_args(worker_list_2_workers, wm_args)

@pytest.fixture(autouse=True)
def cleanup():
    yield
    close_all_loggers()
    for item in os.listdir(test_dir):
        if item.startswith("S") and item.endswith(".zip"):
            os.remove(os.path.join(test_dir, item))
        if "_logs" in item:
            shutil.rmtree(os.path.join(test_dir, item))

def init_worker_type(worker_class, creds, creds_index,  w_args, worker_name=None, standalone=False):
    if worker_name == None:
        worker_name = creds["u" + creds_index]
    w = getattr(sys.modules[__name__], worker_class)(worker_name, creds["u" + creds_index], creds["p" + creds_index])
    w.register_settings(w_args.query, w_args.download_location, w_args.polling_interval, w_args.offline_retries)
    if standalone:
        logdir = os.path.join(test_dir, w.name + "_logs")
        if not os.path.exists(logdir):
            os.mkdir(logdir)
        w.setup(logdir)
    return w

@pytest.fixture()
def worker1(creds, w_args):
    w = init_worker_type("Worker", creds, "1", w_args)
    return w

@pytest.fixture()
def worker2(creds, w_args):
    w = init_worker_type("Worker", creds, "2", w_args)
    return w

@pytest.fixture()
def worker_download_offline1(creds, w_args):
    return init_worker_type("MockWokerProductOffline", creds, "1", w_args)
    
@pytest.fixture()
def worker_download_online1(creds, w_args):
    return init_worker_type("MockWokerProductOnline", creds, "1", w_args)

@pytest.fixture()
def worker_download_online2(creds, w_args):
    return init_worker_type("MockWokerProductOnline", creds, "2", w_args)

@pytest.fixture()
def worker_download_offline2(creds, w_args):
    return init_worker_type("MockWokerProductOffline", creds, "2", w_args)

###### Workers capable of running in stand alone mode 
@pytest.fixture()
def standalone_worker1(creds, w_args):
    w = init_worker_type("Worker", creds, "1", w_args, standalone=True)
    return w

@pytest.fixture()
def standalone_worker2(creds, w_args):
    w = init_worker_type("Worker", creds, "2", w_args, standalone=True)
    return w

@pytest.fixture()
def standalone_worker_download_offline1(creds, w_args):
    return init_worker_type("MockWokerProductOffline", creds, "1", w_args, standalone=True)
    
@pytest.fixture()
def standalone_worker_download_online1(creds, w_args):
    return init_worker_type("MockWokerProductOnline", creds, "1", w_args, standalone=True)

@pytest.fixture()
def standalone_worker_download_online2(creds, w_args):
    return init_worker_type("MockWokerProductOnline", creds, "2", w_args, standalone=True)

@pytest.fixture()
def standalone_worker_download_offline2(creds, w_args):
    return init_worker_type("MockWokerProductOffline", creds, "2", w_args, standalone=True)
            
class MockWokerProductOffline(Worker):
    def query_product_size(self, product_uri):
        ''' Always query the file size of mock offline product
        Args:
            product uri (str): eg. https://scihub.copernicus.eu/dhus/odata/v1/Products('23759763-91e8-4336-a50a-a143e14c8d69')/$value
        Returns:
            product file size in bytes (int) or None if product_uri query failed
        '''
        product_uri = "https://github.com/potatowagon/copinicoos/blob/remove-dhusget/tests/test_data/S1A_offline.zip?raw=true"
        try:
            cmd = ["wget", "--spider", "--user=" + self.username, "--password=" + self.password, product_uri]
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            m = re.search(r'(?<=Length: )\d+', str(out))
            length = int(m.group(0))
            return length
        except Exception as e:
            self.logger.error(e)
            self.logger.error("Error in querying product size for " + product_uri)
            return None

    def download_product(self, file_path, product_uri):
        try:
            product_uri =  "https://github.com/potatowagon/copinicoos/blob/remove-dhusget/tests/test_data/S1A_offline.zip?raw=true"
            cmd = ["wget", "-O", file_path, "--continue", product_uri]
            self.logger.info(cmd)
            subprocess.call(cmd)
        except Exception as e:
            raise

class MockWokerProductOnline(Worker):
    def query_product_size(self, product_uri):
        ''' Always query the file size of mock online product
        Args:
            product uri (str): eg. https://scihub.copernicus.eu/dhus/odata/v1/Products('23759763-91e8-4336-a50a-a143e14c8d69')/$value
        Returns:
            product file size in bytes (int) or None if product_uri query failed
        '''
        product_uri = "https://github.com/potatowagon/copinicoos/blob/remove-dhusget/tests/test_data/S1A_online.zip?raw=true"
        try:
            cmd = ["wget", "--spider", "--user=" + self.username, "--password=" + self.password, product_uri]
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            m = re.search(r'(?<=Length: )\d+', str(out))
            length = int(m.group(0))
            return length
        except Exception as e:
            self.logger.error(e)
            self.logger.error("Error in querying product size for " + product_uri)
            return None

    def download_product(self, file_path, product_uri):
        try:
            product_uri =  "https://github.com/potatowagon/copinicoos/blob/remove-dhusget/tests/test_data/S1A_online.zip?raw=true"
            cmd = ["wget", "-O", file_path, "--continue", product_uri]
            self.logger.info(cmd)
            subprocess.call(cmd)
        except Exception as e:
            raise

def check_online_file_downloaded_correctly():
    '''Fail test case if mock online file cannot be opened
    
    Returns:
        count (int): number of mock online files downloaded if all downloaded correctly 
    '''
    count = 0
    for item in os.listdir(test_dir):
        if item.startswith("S") and item.endswith(".zip"):
            count += 1
            mock_product = ZipFile(os.path.join(test_dir, item))
            with mock_product.open("S1A_online/tiny_file.txt") as txt_file:
                txt = str(txt_file.read())
                assert "this is just to occupy disk space." in txt
                txt_file.close()

            with mock_product.open('S1A_online/fatter_file.png') as img_file:
                try:
                    img = Image.open(img_file)
                    img.verify()
                    img_file.close()
                except Exception as e:
                    pytest.fail(e)
    return count