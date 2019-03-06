import os
import re

import azure.batch.batch_auth as batchauth
import azure.batch.batch_service_client as batch
import azure.storage.blob as blob
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.batch import BatchManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.storage.common import CloudStorageAccount

from aztk.node_scripts.core import log
from aztk.spark import Client, models

RESOURCE_ID_PATTERN = re.compile("^/subscriptions/(?P<subscription>[^/]+)"
                                 "/resourceGroups/(?P<resourcegroup>[^/]+)"
                                 "/providers/[^/]+"
                                 "/[^/]+Accounts/(?P<account>[^/]+)$")

tenant_id = os.environ.get("SP_TENANT_ID")
client_id = os.environ.get("SP_CLIENT_ID")
credential = os.environ.get("SP_CREDENTIAL")
batch_resource_id = os.environ.get("SP_BATCH_RESOURCE_ID")
storage_resource_id = os.environ.get("SP_STORAGE_RESOURCE_ID")

cluster_id = os.environ.get("AZTK_CLUSTER_ID")
pool_id = os.environ["AZ_BATCH_POOL_ID"]
node_id = os.environ["AZ_BATCH_NODE_ID"]
is_dedicated = os.environ["AZ_BATCH_NODE_IS_DEDICATED"] == "true"

spark_web_ui_port = os.environ["SPARK_WEB_UI_PORT"]
spark_worker_ui_port = os.environ["SPARK_WORKER_UI_PORT"]
spark_job_ui_port = os.environ["SPARK_JOB_UI_PORT"]

storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
storage_account_key = os.environ.get("STORAGE_ACCOUNT_KEY")
storage_account_suffix = os.environ.get("STORAGE_ACCOUNT_SUFFIX")

