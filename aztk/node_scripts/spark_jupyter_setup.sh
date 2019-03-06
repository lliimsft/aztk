#!/bin/bash

# install jupyter notebook
pip install jupyter notebook jupyter_enterprise_gateway==1.1.1 tornado==5.1.1 --upgrade

# disable password/token on jupyter notebook
jupyter notebook --generate-config --allow-root
JUPYTER_CONFIG='/root/.jupyter/jupyter_notebook_config.py'
echo >> $JUPYTER_CONFIG
echo -e 'c.NotebookApp.token=""' >> $JUPYTER_CONFIG
echo -e 'c.NotebookApp.password=""' >> $JUPYTER_CONFIG

export KERNELS_FOLDER=/opt/conda/share/jupyter/kernels
export KERNEL_NAME=spark_python_standalone

rm -rf $KERNELS_FOLDER/*
mkdir -p $KERNELS_FOLDER/$KERNEL_NAME/scripts/
mkdir -p $KERNELS_FOLDER/$KERNEL_NAME/bin/
wget -O $KERNELS_FOLDER/$KERNEL_NAME/scripts/launch_ipykernel.py https://raw.githubusercontent.com/jupyter/enterprise_gateway/v1.1.1/etc/kernel-launchers/python/scripts/launch_ipykernel.py
chmod 777 $KERNELS_FOLDER/$KERNEL_NAME/scripts/launch_ipykernel.py
wget -O $KERNELS_FOLDER/$KERNEL_NAME/bin/run.sh https://raw.githubusercontent.com/jupyter/enterprise_gateway/v1.1.1/etc/kernelspecs/spark_python_yarn_client/bin/run.sh
chmod 777 $KERNELS_FOLDER/$KERNEL_NAME/bin/run.sh

touch $KERNELS_FOLDER/$KERNEL_NAME/kernel.json
cat << EOF > $KERNELS_FOLDER/$KERNEL_NAME/kernel.json
{
  "language": "python",
  "display_name": "Spark - Python (Standalone)",
  "process_proxy": {
    "class_name": "enterprise_gateway.services.processproxies.distributed.DistributedProcessProxy"
  },
  "env": {
	"SPARK_HOME": "$SPARK_HOME",
    "PYSPARK_PYTHON": "python",
    "SPARK_OPTS": "--master spark://$AZTK_MASTER_IP:7077 --name \${KERNEL_ID:-ERROR__NO__KERNEL_ID} --conf spark.yarn.submit.waitAppCompletion=false --conf spark.dynamicAllocation.enabled=true --conf spark.shuffle.service.enabled=true",
    "LAUNCH_OPTS": ""
  },
  "argv": [
    "$KERNELS_FOLDER/$KERNEL_NAME/bin/run.sh",
    "{connection_file}",
    "--RemoteProcessProxy.response-address",
    "{response_address}",
    "--RemoteProcessProxy.port-range",
    "{port_range}",
    "--RemoteProcessProxy.spark-context-initialization-mode",
    "lazy"
  ]
}
EOF

# Start Jupyter Enterprise Gateway
jupyter enterprisegateway --ip=0.0.0.0 --port_retries=0 --port=8880 &


# Start Jupyter Notebook Server

pip install nb2kg tornado==5.1.1 --upgrade
jupyter serverextension enable --py nb2kg --sys-prefix

export KG_URL=http://127.0.0.1:8880
export KG_HTTP_USER=guest
export KG_HTTP_PASS=guest-password
export KG_REQUEST_TIMEOUT=30
export KERNEL_USERNAME=${KG_HTTP_USER}
cd /mnt
jupyter notebook --no-browser --port=8888 --allow-root --NotebookApp.session_manager_class=nb2kg.managers.SessionManager --NotebookApp.kernel_manager_class=nb2kg.managers.RemoteKernelManager --NotebookApp.kernel_spec_manager_class=nb2kg.managers.RemoteKernelSpecManager &