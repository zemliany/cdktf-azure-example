import os
from cdktf import App, TerraformStack, TerraformVariable, TerraformOutput, Token, Fn, AzurermBackend
from constructs import Construct
from imports.random.provider import RandomProvider
from imports.random.password import Password

from utils.azure_resources import (
    AzurermProvider,
    ResourceGroup,
    StorageAccount,
    StorageContainer,
    VirtualNetwork,
    Subnet,
    NetworkSecurityGroup,
    SubnetNetworkSecurityGroupAssociation,
    PublicIp,
    NatGateway,
    NatGatewayPublicIpAssociation,
    SubnetNatGatewayAssociation,
    NetworkInterface,
    NetworkSecurityGroupSecurityRule,
    BastionHost,
    NetworkInterfaceBackendAddressPoolAssociation,
    NetworkInterfaceIpConfiguration,
    LinuxVirtualMachine,
    VirtualMachineExtension,
    Lb,
    LbFrontendIpConfiguration,
    LbBackendAddressPool,
    LbProbe,
    LbRule,
    StringResource
)


class EnvVariableException(KeyError):
    def __init__(self, message):
        super().__init__(message)


class EmailExceptionVerification(ValueError):
    def __init__(self, message):
        super().__init__(message)


try:
    email = os.environ['EMAIL']
except KeyError as ex:
    raise EnvVariableException(f"Environment Variable {ex} does not exists or empty, please set environment variable with your SET University mail address, e.g export EMAIL='m.zemlianyi@setuniversity.edu.ua'")


if email.split('@')[1] != 'setuniversity.edu.ua':
    raise EmailExceptionVerification(f"Current email {email}, only emails from domain setuniversity.edu.ua is allowed to run this code")

user = str(email.split("@")[0].replace('.',''))


class AzureIntroToCloudBackendStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # Initialize Azure Provider
        AzurermProvider(
            self,
            "azurerm",
            features={},
            subscription_id=os.environ['ARM_SUBSCRIPTION_ID'], # ARM_SUBSCRIPTION_ID
            client_id=os.environ['ARM_CLIENT_ID'], # ARM_CLIENT_ID
            client_secret=os.environ['ARM_CLIENT_SECRET'], # ARM_CLIENT_SECRET
            tenant_id=os.environ['ARM_TENANT_ID'] # ARM_TENANT_ID
        )

        # Create a Resource Group
        resource_group = ResourceGroup(
            self,
            "backend_rg",
            name=f"{user}-azure-cdktf-backend-rg",
            location="eastus"
        )

        # Create a Storage Account
        storage_account = StorageAccount(
            self,
            "backend_storage_account",
            name="cdktfstatebackend",
            resource_group_name=resource_group.name,
            location=resource_group.location,
            account_tier="Standard",
            account_replication_type="LRS"
        )

        # Create a Blob Container
        storage_container = StorageContainer(
            self,
            "backend_storage_container",
            name="tfstate",
            storage_account_name=storage_account.name,
            container_access_type="private"
        )

        # Output the backend details
        TerraformOutput(self, "backend_resource_group_name", value=resource_group.name)
        TerraformOutput(self, "backend_storage_account_name", value=storage_account.name)
        TerraformOutput(self, "backend_container_name", value=storage_container.name)


class AzureIntroToCloud(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)


        """Init Azure and Random Provider in CDKTF"""
        AzurermProvider(
            self,
            "azurerm",
            features={},
            subscription_id=os.environ['ARM_SUBSCRIPTION_ID'], # ARM_SUBSCRIPTION_ID
            client_id=os.environ['ARM_CLIENT_ID'], # ARM_CLIENT_ID
            client_secret=os.environ['ARM_CLIENT_SECRET'], # ARM_CLIENT_SECRET
            tenant_id=os.environ['ARM_TENANT_ID'] # ARM_TENANT_ID
        )

        # Use remote state outputs for backend configuration
        AzurermBackend(self,
                       resource_group_name=f"{user}-azure-cdktf-backend-rg",
                       storage_account_name="cdktfstatebackend",
                       container_name="tfstate",
                       key="terraform.tfstate"
                       )

        RandomProvider(self, "random")


        random_string=StringResource(
            self, "my_random_string", length=8, upper=False, special=False
        )
        
        random_password = Password(self, "random_pass",
            length=16,
            override_special="^!#$%&*()-_=+[]{}<>:?",
            special=False,
            lower=True,
            upper=True,
            numeric=True
        )

        # nonsensitive_password = Fn.nonsensitive(random_password.result)


        """Defining Basic TF Variables"""
        public_ip_name = TerraformVariable(self, "public_ip_name", default=f"{user}-azure-cdktf-public-ip", type="string")
        resource_group_location = TerraformVariable(self, "resource_group_location", default="eastus", type="string")
        virtual_network_name = TerraformVariable(self, "virtual_network_name", default=f"{user}-azure-cdktf-vnet", type="string")
        subnet_name = TerraformVariable(self, "subnet_name", default=f"{user}-azure-cdktf-subnet", type="string")
        network_interface_name = TerraformVariable(self, "network_interface_name", default=f"{user}-azure-cdktf-nsg", type="string")
        network_security_group_name = TerraformVariable(self, "network_security_group_name", default=f"{user}-azure-cdktf-nsg", type="string")
        nat_gateway_name = TerraformVariable(self, "nat_gateway", default=f"{user}-azure-cdktf-nat", type="string")
        bastion_name = TerraformVariable(self, "bastion_name", default=f"{user}-azure-cdktf-bastion", type="string")
        virtual_machine_name = TerraformVariable(self, "virtual_machine_name", default=f"{user}-azure-cdktf-vm", type="string")
        virtual_machine_size = TerraformVariable(self, "virtual_machine_size", default="Standard_B1ms", type="string")
        disk_name = TerraformVariable(self, "disk_name", default=f"{user}-azure-cdktf-disk", type="string")
        redundancy_type = TerraformVariable(self, "redundancy_type", default="Standard_LRS", type="string")
        load_balancer_name = TerraformVariable(self, "load_balancer_name", default=f"{user}-azure-cdktf-lb", type="string")
        username = TerraformVariable(self, "username", default=user, type="string")
        password = TerraformVariable(self, "password", default=Fn.nonsensitive(random_password.result), type="string")

        """cloud tags"""
        general_tags = {
                "Environment": "dev",
                "Student": f"{user}",
                "StudentEmail": f"{email}",
                "ManagedBy": "Python CDKTF",
                "Institution": "SET University",
                "Course": "Introduction to Cloud",
                "Task": "Practical Task"
        }


        """Azure Resource Group"""
        resource_group = ResourceGroup(
            self,
            "my_resource_group",
            name=f"{public_ip_name.string_value}-{random_string.result}",
            location=resource_group_location.string_value,
            tags=general_tags,
        )

        """Azure VMNet"""
        virtual_network = VirtualNetwork(
            self,
            "my_virtual_network",
            name=virtual_network_name.string_value,
            address_space=["10.0.0.0/16"],
            location=resource_group.location,
            resource_group_name=resource_group.name,
            tags=general_tags,
        )

        # Subnets
        subnet = Subnet(
            self,
            "my_subnet",
            name=subnet_name.string_value,
            resource_group_name=resource_group.name,
            virtual_network_name=virtual_network.name,
            address_prefixes=["10.0.1.0/24"],
        )

        """Azure Bastion Subnet for Intranet SSH Connect"""
        bastion_subnet = Subnet(
            self,
            "my_bastion_subnet",
            name="AzureBastionSubnet",
            resource_group_name=resource_group.name,
            virtual_network_name=virtual_network.name,
            address_prefixes=["10.0.2.0/24"],
        )

        """Azure NSG"""
        nsg = NetworkSecurityGroup(
            self,
            "my_nsg",
            name=network_security_group_name.string_value,
            location=resource_group.location,
            resource_group_name=resource_group.name,
            tags=general_tags,
            security_rule=[
                NetworkSecurityGroupSecurityRule(
                    name="ssh",
                    priority=1022,
                    direction="Inbound",
                    access="Allow",
                    protocol="Tcp",
                    source_port_range="*",
                    destination_port_range="22",
                    source_address_prefix="*",
                    destination_address_prefix="10.0.1.0/24",
                ),
                NetworkSecurityGroupSecurityRule(
                    name="web",
                    priority=1080,
                    direction="Inbound",
                    access="Allow",
                    protocol="Tcp",
                    source_port_range="*",
                    destination_port_range="80",
                    source_address_prefix="*",
                    destination_address_prefix="10.0.1.0/24",
                )
            ]
        )

        SubnetNetworkSecurityGroupAssociation(
            self,
            "my_nsg_association",
            subnet_id=subnet.id,
            network_security_group_id=nsg.id,
        )


        public_ip = [
            PublicIp(
                self,
                f"my_public_ip_{i}",
                name=f"{public_ip_name.string_value}-{i}",
                location=resource_group.location,
                resource_group_name=resource_group.name,
                allocation_method="Static",
                sku="Standard",
            )
            for i in range(2)
        ]

        """Azure NATGW"""
        nat_gateway = NatGateway(
            self,
            "my_nat_gateway",
            name=nat_gateway_name.string_value,
            location=resource_group.location,
            resource_group_name=resource_group.name,
            sku_name="Standard",
            tags=general_tags,
        )

        NatGatewayPublicIpAssociation(
            self,
            "my_nat_gateway_ip_association",
            nat_gateway_id=nat_gateway.id,
            public_ip_address_id=public_ip[0].id,
        )

        SubnetNatGatewayAssociation(
            self,
            "my_nat_gateway_subnet_association",
            subnet_id=subnet.id,
            nat_gateway_id=nat_gateway.id,
        )

        """Azure Network Interfaces"""
        network_interfaces = [
            NetworkInterface(
                self,
                f"my_nic_{i}",
                name=f"{network_interface_name.string_value}-{i}",
                location=resource_group.location,
                resource_group_name=resource_group.name,
                tags=general_tags,
                ip_configuration=[
                    NetworkInterfaceIpConfiguration(
                            name=f"ipconfig-{i}",
                            private_ip_address_allocation="Dynamic",
                            subnet_id=subnet.id,
                            primary=True
                        )
                ],
            )
            for i in range(3)
        ]


        """Azure Bastion Resource Creation"""
        bastion_host = BastionHost(
            self,
            "my_bastion",
            name=bastion_name.string_value,
            location=resource_group.location,
            resource_group_name=resource_group.name,
            sku="Standard",
            tags=general_tags,
            ip_configuration={
                "name": "ipconfig",
                "subnet_id": bastion_subnet.id,
                "public_ip_address_id": public_ip[1].id,
            },
            
        )

        """Azure VMs provisioning"""
        virtual_machines = [
            LinuxVirtualMachine(
                self,
                f"my_vm_{i}",
                name=f"{virtual_machine_name.string_value}-{i}",
                location=resource_group.location,
                resource_group_name=resource_group.name,
                network_interface_ids=[network_interfaces[i].id],
                size=virtual_machine_size.string_value,
                os_disk={
                    "name": f"{disk_name.string_value}-{i}",
                    "caching": "ReadWrite",
                    "storage_account_type": redundancy_type.string_value,
                },
                source_image_reference={
                    "publisher": "Canonical",
                    "offer": "0001-com-ubuntu-server-jammy",
                    "sku": "22_04-lts-gen2",
                    "version": "latest",
                },
                admin_username=username.default,
                admin_password=password.default,
                disable_password_authentication=False,
                tags=general_tags,
            )
            for i in range(3)
        ]

        """Azure VMs Extension to setup NGINX"""
        vm_extensions = [
            VirtualMachineExtension(
                self,
                f"my_vm_extension_{i}",
                name="Nginx",
                virtual_machine_id=virtual_machines[i].id,
                publisher="Microsoft.Azure.Extensions",
                type="CustomScript",
                type_handler_version="2.0",
                settings="""{
                  "commandToExecute": "sudo apt-get update && sudo apt-get install nginx -y && echo \\\"Greetings from the Azure VM with hostname: $(hostname)\\\" > /var/www/html/index.html && sudo systemctl restart nginx"
                }""",
            )
            for i in range(2)
        ]

        """Azure Internal LoadBalancer"""
        lb = Lb(
            self,
            "my_lb",
            name=load_balancer_name.string_value,
            location=resource_group.location,
            resource_group_name=resource_group.name,
            sku="Standard",
            tags=general_tags,
            frontend_ip_configuration=[
                LbFrontendIpConfiguration(
                    name="frontend-ip",
                    subnet_id=subnet.id,
                    private_ip_address_allocation="Dynamic",
                )
            ]
        )

        lb_pool = LbBackendAddressPool(
            self,
            "my_lb_pool",
            loadbalancer_id=lb.id,
            name="test-pool",
        )

        lb_probe = LbProbe(
            self,
            "my_lb_probe",
            loadbalancer_id=lb.id,
            name="test-probe",
            port=80,
            resource_group_name=resource_group.name,
        )

        nic_lb_pool_associations = [
            NetworkInterfaceBackendAddressPoolAssociation(
                self,
                f"my_nic_lb_pool_{i}",
                network_interface_id=network_interfaces[i].id,
                ip_configuration_name=f"ipconfig-{i}",
                backend_address_pool_id=lb_pool.id,
            )
            for i in range(2)
        ]

        lb_rule = LbRule(
            self,
            "my_lb_rule",
            loadbalancer_id=lb.id,
            name="test-rule",
            protocol="Tcp",
            frontend_port=80,
            backend_port=80,
            disable_outbound_snat=True,
            frontend_ip_configuration_name="frontend-ip",
            probe_id=lb_probe.id,
            backend_address_pool_ids=[lb_pool.id],
            resource_group_name=resource_group.name,
        )

        TerraformOutput(
            self,
            "private_ip_address",
            value=f"http://{lb.private_ip_address}"
        )

        TerraformOutput(
            self,
            "bastion_username",
            value=username,
            sensitive=False
        )

        TerraformOutput(
            self,
            "bastion_generated_password",
            value=Fn.nonsensitive(password.default),
            sensitive=False
        )

app = App()
AzureIntroToCloudBackendStack(app, f"{user}-azure-backend-stack")
AzureIntroToCloud(app, f"{user}-azure-stack")
app.synth()
