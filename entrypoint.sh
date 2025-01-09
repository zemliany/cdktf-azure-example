#!/bin/bash -e

function check_azure_creds() {
    _RAND_PREFIX=$(echo $(cat /proc/sys/kernel/random/uuid) | awk -F '-' '{print $1}')
    _EMAIL=$2
    _STACK_TO_DESTROY=
    _USER=$(echo ${_EMAIL} | awk -F "@" '{print $1}' | sed 's/\.//g')
    _DOMAIN=$(echo ${_EMAIL} | awk -F "@" '{print $2}')
    _NAME_FOR_RBAC="${_USER}-cdktf-automation-${_RAND_PREFIX}"
    _CDKTF_APP_STACK="${_USER}-azure-stack"
    _CDKTF_BACKEND_STACK="${_USER}-azure-backend-stack"
    _CDKTF_BACKEND_RG="${_USER}-azure-cdktf-backend-rg"


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
    export CDKTF_APP_STACK=${_CDKTF_APP_STACK}
    export CDKTF_BACKEND_STACK=${_CDKTF_BACKEND_STACK}
    export CDKTF_BACKEND_RG=${_CDKTF_BACKEND_RG}
}

function cdktf_azure_example_checkout() {
    if [ ! -d "app/cdktf-azure-example" ]; then
        echo "Cloning 'cdktf-azure-example'..."
        cd /app
        git clone --branch feature/SETI2C-14 https://github.com/zemliany/cdktf-azure-example.git
    fi
    sed -i "s/client_id=.*/client_id=${ARM_CLIENT_ID},/" /app/cdktf-azure-example/main.py
    sed -i "s/client_secret=.*/client_secret=${ARM_CLIENT_SECRET},/" /app/cdktf-azure-example/main.py
    sed -i "s/tenant_id=.*/tenant_id=${ARM_TENANT_ID},/" /app/cdktf-azure-example/main.py
    sed -i "s/subscription_id=.*/subscription_id=\"${ARM_SUBSCRIPTION_ID}\",/" /app/cdktf-azure-example/main.py
    export _APP_ID=${ARM_CLIENT_ID}
    for ARM_VAR in $(env | grep 'ARM' | awk -F '=' '{print $1}' | xargs); do unset ${ARM_VAR}; done
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

function azure_cli_cleanup() {
    if az account show -o json > /dev/null 2>&1; then
        if [[ -d "${HOME}/.azure/" && "$(ls -A "${HOME}/.azure/")" ]]; then
            echo "Cleanup Azure CLI credentials..."
            rm -rf ${HOME}/.azure/*
        fi
    fi
}

function azure_rbac_cleanup() {
    echo "RBAC Cleanup triggered"
    sleep 3
    if az ad sp list --all -o jsonc | jq -e "[.[] | select(.appId == ${_APP_ID})] | length > 0" > /dev/null; then
        echo "Service Principal with ID ${_APP_ID} exists."
        echo "Deleting Azure RBAC credentials with ${_APP_ID}..."
        az ad sp delete --id ${_APP_ID//\"/}
    else
        echo "Service Principal with appId ${_APP_ID} does NOT exist OR already deleted."
    fi
    unset ${_APP_ID}
}

function cdktf_execute() {
    _STACK_PATH=/app/cdktf-azure-example/cdktf.out/stacks/${CDKTF_APP_STACK}/
    _STACK_TO_RUN=${CDKTF_APP_STACK}
    if [ "$(az group exists --name ${CDKTF_BACKEND_RG})" == "false" ]; then
        _STACK_TO_RUN=${CDKTF_BACKEND_STACK}
        echo "Initial Azure Backend for CDKTF is not deployed, so ${_STACK_TO_RUN} will be executed firstly. If you're using plan you need to deploy backend stack at first to move forward to deploy Azure Infrastructure"
        echo -e "List of available stacks:\n"
        cdktf list
    fi
    cdktf "$1" ${_STACK_TO_RUN} --auto-approve
}

case "$1" in
    apply|destroy|plan)
        check_azure_creds "$@"
        cdktf_azure_example_checkout
        cdktf_imports_init
        # cdktf "$1" --auto-approve
        cdktf_execute $1
        azure_rbac_cleanup
        # azure_cli_cleanup
        ;;
    -*)
        cdktf "$@"
        ;;
    *)
        echo $"Usage: $0 {apply|destroy|plan} mymail@exammple.com"
        exit 1
        ;;
esac