#!/usr/bin/env python3

# Import each resource class from its generated module
from imports.azurerm.provider import AzurermProvider
from imports.azurerm.provider import AzurermProviderFeatures
from imports.azurerm.resource_group import ResourceGroup
from imports.azurerm.storage_account import StorageAccount
from imports.azurerm.storage_container import StorageContainer
from imports.azurerm.virtual_network import VirtualNetwork
from imports.azurerm.subnet import Subnet
from imports.azurerm.network_security_group import NetworkSecurityGroup
from imports.azurerm.subnet_network_security_group_association import SubnetNetworkSecurityGroupAssociation
from imports.azurerm.public_ip import PublicIp
from imports.azurerm.nat_gateway import NatGateway
from imports.azurerm.nat_gateway_public_ip_association import NatGatewayPublicIpAssociation
from imports.azurerm.subnet_nat_gateway_association import SubnetNatGatewayAssociation
from imports.azurerm.network_interface import NetworkInterface, NetworkInterfaceIpConfiguration
from imports.azurerm.network_security_group import NetworkSecurityGroupSecurityRule
from imports.azurerm.bastion_host import BastionHost
from imports.azurerm.network_interface_backend_address_pool_association import NetworkInterfaceBackendAddressPoolAssociation
from imports.azurerm.linux_virtual_machine import LinuxVirtualMachine
from imports.azurerm.virtual_machine_extension import VirtualMachineExtension
from imports.azurerm.lb import Lb, LbFrontendIpConfiguration
from imports.azurerm.lb_backend_address_pool import LbBackendAddressPool
from imports.azurerm.lb_probe import LbProbe
from imports.azurerm.lb_rule import LbRule

from imports.random.string_resource import StringResource

__all__ = [
    "AzurermProvider",
    "AzurermProviderFeatures",
    "ResourceGroup",
    "StorageAccount",
    "StorageContainer",
    "VirtualNetwork",
    "Subnet",
    "NetworkSecurityGroup",
    "SubnetNetworkSecurityGroupAssociation",
    "PublicIp",
    "NatGateway",
    "NatGatewayPublicIpAssociation",
    "SubnetNatGatewayAssociation",
    "NetworkInterface",
    "NetworkSecurityGroupSecurityRule",
    "NetworkInterfaceIpConfiguration",
    "BastionHost",
    "NetworkInterfaceBackendAddressPoolAssociation",
    "LinuxVirtualMachine",
    "VirtualMachineExtension",
    "Lb",
    "LbBackendAddressPool",
    "LbProbe",
    "LbRule",
    "LbFrontendIpConfiguration",
    "StringResource"
]
