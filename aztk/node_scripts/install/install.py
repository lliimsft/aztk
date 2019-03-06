import os

from aztk.internal import cluster_data
from aztk.models.plugins import PluginTarget
from aztk.node_scripts.core import config
from aztk.node_scripts.install import (plugins, spark, spark_container)
import time

def read_cluster_config():
    data = cluster_data.ClusterData(config.blob_client, config.cluster_id)
    cluster_config = data.read_cluster_config()
    print("Got cluster config", cluster_config)
    return cluster_config


def setup_host(docker_repo: str, docker_run_options: str):
    """
    Code to be run on the node (NOT in a container)
    :param docker_repo: location of the Docker image to use
    :param docker_run_options: additional command-line options to pass to docker run
    """
    is_master = os.environ.get("AZ_BATCHAI_SPARK_MASTER") == "true"
    is_worker = not is_master

    if is_master:
        os.environ["AZTK_IS_MASTER"] = "true"
    else:
        os.environ["AZTK_IS_MASTER"] = "false"
    if is_worker:
        os.environ["AZTK_IS_WORKER"] = "true"
    else:
        os.environ["AZTK_IS_WORKER"] = "false"


    cluster_info_file = os.environ.get('AZ_BATCHAI_SPARK_CLUSTER_INFO_FILE')
    master_ip = ''
    def wait_and_get_master():
        while True:
            with open(cluster_info_file) as fp:
                line = fp.readline()
                while line:
                    parts = line.split(':')
                    if len(parts) > 1 and parts[1].startswith('master'):
                        return parts[0]
                    line = fp.readline()
            time.sleep(2)

    if is_master:
        import socket
        master_ip = socket.gethostbyname(socket.gethostname())
        with open(cluster_info_file, 'a') as the_file:
            the_file.write(master_ip+':master\n')
    else:
        master_ip = wait_and_get_master()

    os.environ["AZTK_MASTER_IP"] = master_ip

    # TODO pass azure file shares
    spark_container.start_spark_container(
        docker_repo=docker_repo,
        docker_run_options=docker_run_options,
        gpu_enabled=os.environ.get("AZTK_GPU_ENABLED") == "true",
        plugins=cluster_conf.plugins,
    )
    plugins.setup_plugins(target=PluginTarget.Host, is_master=is_master, is_worker=is_worker)


def setup_spark_container():
    """
    Code run in the main spark container
    """
    is_master = os.environ.get("AZTK_IS_MASTER") == "true"
    is_worker = os.environ.get("AZTK_IS_WORKER") == "true"
    print("Setting spark container. Master: ", is_master, ", Worker: ", is_worker)

    print("Copying spark setup config")
    spark.setup_conf()
    print("Done copying spark setup config")

    spark.setup_connection()

    if is_master:
        spark.start_spark_master()

    if is_worker:
        spark.start_spark_worker()

    plugins.setup_plugins(target=PluginTarget.SparkContainer, is_master=is_master, is_worker=is_worker)

    open("/tmp/setup_complete", "a").close()
