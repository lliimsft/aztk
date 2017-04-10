import common.util as util

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import os
import datetime
import random
import argparse

import azure.batch.batch_service_client as batch
import azure.batch.batch_auth as batch_auth 
import azure.batch.models as batch_models
import azure.storage.blob as blob

# config file path
_config_path = os.path.join(os.path.dirname(__file__), 'configuration.cfg')

# generate random number for deployment suffix
_deployment_suffix = str(random.randint(0,1000000))

# cluster id
_pool_id = None

if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(prog="az_spark")

    parser.add_argument("--cluster-id", required=True,
                        help="the unique name of your spark cluster")

    args = parser.parse_args()
    
    print()
    if args.cluster_id is not None:
        _pool_id = args.cluster_id
    print("delete cluster id:      %s" % _pool_id)

    # Read config file
    global_config = configparser.ConfigParser()
    global_config.read(_config_path)

    # Set up the configuration
    batch_account_key = global_config.get('Batch', 'batchaccountkey')
    batch_account_name = global_config.get('Batch', 'batchaccountname')
    batch_service_url = global_config.get('Batch', 'batchserviceurl')
    storage_account_key = global_config.get('Storage', 'storageaccountkey')
    storage_account_name = global_config.get('Storage', 'storageaccountname')
    storage_account_suffix = global_config.get('Storage', 'storageaccountsuffix')

    # Set up SharedKeyCredentials
    credentials = batch_auth.SharedKeyCredentials(
        batch_account_name,
        batch_account_key)

    # Set up Batch Client
    batch_client = batch.BatchServiceClient(
        credentials,
        base_url=batch_service_url)

    # delete pool by id
    pool = batch_client.pool.get(_pool_id)
    if batch_client.pool.exists(_pool_id) == True:
        batch_client.pool.delete(_pool_id)
        print("\nThe pool, '%s', is being deleted" % _pool_id)
    else:
        print("\nThe pool, '%s', does not exist" % _pool_id)

