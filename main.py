import os
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute.models import DiskCreateOption, HardwareProfile, NetworkInterfaceReference, OSProfile, \
    StorageAccountTypes, StorageProfile, VirtualHardDisk, VirtualMachine, \
    VirtualMachineIdentity, VirtualMachineSizeTypes

def create_resource_group(resource_group_name, location, resource_client):
    resource_client.resource_groups.create_or_update(
        resource_group_name,
        {'location': location}
    )
    print(f'Created resource group: {resource_group_name}')

def create_virtual_network(resource_group_name, location, network_client):
    vnet_params = {
        'address_space': {
            'address_prefixes': ['10.0.0.0/16']
        },
        'subnets': [{
            'name': 'mysubnet',
            'address_prefix': '10.0.0.0/24'
        }]
    }
    virtual_network_poller = network_client.virtual_networks.begin_create_or_update(
        resource_group_name,
        'myvnet',
        {
            'location': location,
            'address_space': vnet_params['address_space'],
            'subnets': vnet_params['subnets']
        }
    )
    virtual_network = virtual_network_poller.result()
    print(f'Created virtual network: {virtual_network.name}')

    subnet = network_client.subnets.get(resource_group_name, virtual_network.name, 'mysubnet')
    return subnet

def create_network_interface(resource_group_name, location, subnet, network_client):
    nic_poller = network_client.network_interfaces.begin_create_or_update(
        resource_group_name,
        'mynic',
        {
            'location': location,
            'ip_configurations': [{
                'name': 'myipconfig',
                'subnet': {
                    'id': subnet.id
                }
            }]
        }
    )
    nic = nic_poller.result() # Get the actual NIC object
    print(f'Created network interface: {nic.name}')

    return nic

def create_virtual_machine(resource_group_name, location, compute_client, network_client, nic):
    vm_name = 'myvm'
    vm_size =  'Standard_B1ls'#'Standard_D1_v2'
    image_reference = {
        'publisher': 'Canonical',
        'offer': 'UbuntuServer',
        'sku': '18.04-LTS',
        'version': 'latest'
    }

    # Create the hardware profile for the VM
    hardware_profile = HardwareProfile(
        vm_size=vm_size
    )
    # Set the admin username and password for the VM
    admin_username = '<admin_username>'
    admin_password = 'passw0rd#1'
    # Create the OS profile for the VM
    os_profile = OSProfile(
        computer_name=vm_name,
        admin_username=admin_username,
        admin_password=admin_password
    )

    vm_poller = compute_client.virtual_machines.begin_create_or_update(
        resource_group_name,
        vm_name,
        {
            'location': location,
            'hardware_profile': hardware_profile,
            'os_profile': os_profile,
            'storage_profile': {
                'image_reference': image_reference
            },
            'network_profile': {
                'network_interfaces': [{
                    'id': nic.id
                }]
            }
        }
    )
    vm = vm_poller.result() # Get the actual VM object
    print(f'Created virtual machine: {vm.name}')

def delete_resources(resource_group_name, compute_client, network_client, resource_client):
    vm_name = 'myvm'
    nic_name = 'mynic'
    vnet_name = 'myvnet'

    # Delete the VM
    print(f'Deleting VM: {vm_name}')
    compute_client.virtual_machines.begin_delete(resource_group_name, vm_name).wait()

    # Delete the NIC
    print(f'Deleting NIC: {nic_name}')
    network_client.network_interfaces.begin_delete(resource_group_name, nic_name).wait()

    # Delete the virtual network
    print(f'Deleting virtual network: {vnet_name}')
    network_client.virtual_networks.begin_delete(resource_group_name, vnet_name).wait()

    # Delete the resource group
    print(f'Deleting resource group: {resource_group_name}')
    resource_client.resource_groups.begin_delete(resource_group_name).wait()

def main():
    # Set up the Azure API client
    credentials = DefaultAzureCredential()

    subscription_id = 'a7ef3688-af58-4835-953c-e51f219fbd0f'

    compute_client = ComputeManagementClient(credentials, subscription_id)
    resource_client = ResourceManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)

    # Create a new resource group
    resource_group_name = 'myresourcegroup'
    location = 'eastus'
    create_resource_group(resource_group_name, location, resource_client)
    subnet = create_virtual_network(resource_group_name, location, network_client)
    nic = create_network_interface(resource_group_name, location, subnet, network_client)
    vm = create_virtual_machine(resource_group_name, location, compute_client, network_client, nic)
    delete_resources(resource_group_name, compute_client, network_client, resource_client)

if __name__ == "__main__":
    main()

