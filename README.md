# Azure-Python-SDK-Guide-for-Beginners
In this simple blog, we will learn how to provision virtual machines on Azure using the Python SDK, the steps are nearly the same for the other languages, once you grasp the general idea you will be able to other languages easily.

![image](https://user-images.githubusercontent.com/56788883/234921673-c3ed0c29-a092-4d21-8af6-3780cf15588d.png)

## Why the Azure Python SDK?
There are several reasons why you might want to use the Azure Python SDK:
1. Automate Azure operations: The Azure Python SDK provides a convenient and programmatic way to automate Azure operations using Python scripts. This means you can write scripts to create and manage Azure resources, monitor and optimize your Azure infrastructure, and perform other administrative tasks.
2. Seamless integration with Python: Python is a popular programming language with a large community and a wide range of libraries and frameworks. By using the Azure Python SDK, you can leverage the power and flexibility of Python to build and deploy Azure applications and services.
3. Cross-platform support: The Azure Python SDK supports multiple platforms, including Windows, macOS, and Linux. This means you can write Python scripts that can run on any platform and manage your Azure resources from anywhere.
4. Rich functionality: The Azure Python SDK provides access to a wide range of Azure services, including compute, storage, networking, security, and more. This means you can build complex and sophisticated applications that take advantage of Azure’s rich functionality and features.
5. Faster development: By using the Azure Python SDK, you can save time and effort in developing Azure applications and services. The SDK provides a high-level, Pythonic interface that makes it easy to work with Azure resources and services, reducing the amount of boilerplate code you need to write.


### Step 1: Add the required imports
```python
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute.models import HardwareProfile, OSProfile
```

### Step 2: Create a resource group
This function creates a new resource group with the given name and location using the ResourceManagementClient.

```python
def create_resource_group(resource_group_name, location, resource_client):
    resource_client.resource_groups.create_or_update(
        resource_group_name,
        {'location': location}
    )
    print(f'Created resource group: {resource_group_name}')
```

### Step 3: Create the virtual network
This function creates a new virtual network with the given name and location using the NetworkManagementClient. It also creates a subnet with the name “`mysubnet`” and the address prefix “`10.0.0.0/24`” within the virtual network.

```python
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
```

### Step 4: Create the network interface
This function creates a new network interface with the given name and location using the NetworkManagementClient. It uses the subnet created in the previous function.

```python
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
```

### Step 5: Create the virtual machine
This function creates a new virtual machine with the given name and location using the ComputeManagementClient. It uses the virtual network and network interface created in the previous functions. It also sets the virtual machine’s size, operating system, administrator username, and password.


```python
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
    admin_password = '<strong_password>'
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
```

### Step 6: Call them all
Set up the Azure API client, calls the create/delete functions in order, and pass the necessary parameters.
```python
if __name__ == "__main__":
    # Set up the Azure API client
    credentials = DefaultAzureCredential()
    subscription_id = '<subscription_id>'

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
```

You can also check that the resources were created by running: `az resource list --output table`

### Step 7: delete the resources
This function deletes the virtual machine, network interface, virtual network, and resource group created in the previous functions using their respective management clients.

```python
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
```

Don't forget to star the repo if you found this useful!
