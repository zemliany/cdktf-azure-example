#!/bin/bash -e

function check_azure_creds() {
    _RAND_PREFIX=$(echo $(cat /proc/sys/kernel/random/uuid) | awk -F '-' '{print $1}')
    _EMAIL=$2
    _USER=$(echo ${_EMAIL} | awk -F "@" '{print $1}' | sed 's/\.//g')
    _DOMAIN=$(echo ${_EMAIL} | awk -F "@" '{print $2}')
    _NAME_FOR_RBAC="${_USER}-cdktf-automation-${_RAND_PREFIX}"

    if [ "${_DOMAIN}" != "setuniversity.edu.ua" ]; then
        echo "${_DOMAIN} not equal to setuniversity.edu.ua. Only setuniversity.edu.ua email's is supported"
        exit 1
    fi

    if ! az account show -o json > /dev/null 2>&1; then
        echo "Azure CLI credentials are invalid or missing. Triggering az login..."
        az login
    else
        echo "Azure CLI credentials are valid."
    fi

    if [ $? -eq 0 ]; then 
        if [ -z "${_AZURE_RBAC_CREDS}" ]; then
            echo "Azure RBAC Creds is not set or is empty. Setting it now..."
            _SUBSCRIPTION_ID=$(az account show -o jsonc | jq -r '.id')
            echo "Sleep 10..."
            sleep 10
            export _AZURE_RBAC_CREDS=$(az ad sp create-for-rbac --name "${_NAME_FOR_RBAC}" --role Contributor --scopes /subscriptions/${_SUBSCRIPTION_ID})
            export ARM_SUBSCRIPTION_ID="${_SUBSCRIPTION_ID}"
            export ARM_CLIENT_ID=$(jq '.appId' <<< ${_AZURE_RBAC_CREDS})
            export ARM_CLIENT_SECRET=$(jq '.password' <<< ${_AZURE_RBAC_CREDS})
            export ARM_TENANT_ID=$(jq '.tenant' <<< ${_AZURE_RBAC_CREDS})
        else
            echo "Azure RBAC Creds is already set and not empty."
        fi
    fi

    export EMAIL=${_EMAIL}
}

function cdktf_azure_example_checkout() {
    if [ ! -d "app/cdktf-azure-example" ]; then
        echo "Cloning 'cdktf-azure-example'..."
        cd /app
        git clone https://github.com/zemliany/cdktf-azure-example.git
    fi
    sed -i "s/client_id=.*/client_id=${ARM_CLIENT_ID},/" /app/cdktf-azure-example/main.py
    sed -i "s/client_secret=.*/client_secret=${ARM_CLIENT_SECRET},/" /app/cdktf-azure-example/main.py
    sed -i "s/tenant_id=.*/tenant_id=${ARM_TENANT_ID},/" /app/cdktf-azure-example/main.py
    sed -i "s/subscription_id=.*/subscription_id=\"${ARM_SUBSCRIPTION_ID}\",/" /app/cdktf-azure-example/main.py
}

function cdktf_imports_init() {
    if [ ! -d "app/cdktf-azure-example/imports" ]; then
        echo "Running 'cdktf get' as it has not been executed yet..."
        cd /app/cdktf-azure-example
        pipenv install 
        echo "Sleep 10..."
        sleep 10
        cdktf get
    fi
}

function cleanup() {
    echo "Cleanup triggered"
    sleep 3
    if az ad sp list --all -o table | grep "${ARM_CLIENT_ID}" > /dev/null 2>&1; then
        echo "Deleting Azure RBAC credentials with ${ARM_CLIENT_ID}..."
        echo "Deleting Azure RBAC credentials..."
        az ad sp delete --id ${ARM_CLIENT_ID}
    fi
    sleep 3
    if [[ -d ${HOME}/.azure/ && $(ls -A "${HOME}/.azure/") ]]; then
        echo "Cleanup Azure CLI credentials..."
        rm -rf ${HOME}/.azure/*
    fi
}

trap 'cleanup' EXIT

case "$1" in
    apply|destroy|plan)
        check_azure_creds "$@"
        cdktf_azure_example_checkout
        cdktf_imports_init
        cdktf "$1" --auto-approve
        cleanup
        ;;
    -*)
        cdktf "$@"
        ;;
    *)
        echo $"Usage: $0 {apply|destroy|plan} mymail@exammple.com"
        exit 1
        ;;
esac