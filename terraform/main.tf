# terraform/main.tf

# Generate random resource group name
resource "random_pet" "rg_name" {
  prefix = var.resource_group_name_prefix
}

resource "azurerm_resource_group" "rg" {
  location = var.resource_group_location
  name     = random_pet.rg_name.id
}


# --- VNet and Subnets ---


resource "azurerm_virtual_network" "vnet" {
  name                = "vnet-shared"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_subnet" "aks_subnet" {
  name                 = "aks-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.2.0/24"]
}


resource "azurerm_subnet" "postgres_subnet" {
  name                 = "postgres-subnet"
  resource_group_name  = azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.1.0/24"]
  delegation {
    name = "delegation"
    service_delegation {
      name = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
      ]
    }
  }
}


# --- AKS ---

resource "random_pet" "azurerm_kubernetes_cluster_name" {
  prefix = "cluster"
}

resource "random_pet" "azurerm_kubernetes_cluster_dns_prefix" {
  prefix = "dns"
}


resource "azurerm_kubernetes_cluster" "k8s" {
  location            = azurerm_resource_group.rg.location
  name                = random_pet.azurerm_kubernetes_cluster_name.id
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = random_pet.azurerm_kubernetes_cluster_dns_prefix.id

  identity {
    type = "SystemAssigned"
  }

  default_node_pool {
    name       = "agentpool"
    vm_size    = "Standard_B2s"
    node_count = var.node_count
    vnet_subnet_id = azurerm_subnet.aks_subnet.id
  }
  # linux_profile {
  #   admin_username = var.username
  # 
  #   ssh_key {
  #     key_data = azapi_resource_action.ssh_public_key_gen.output.publicKey
  #   }
  # }
  network_profile {
    network_plugin    = "azure"
    dns_service_ip = "10.0.10.10"
    service_cidr = "10.0.10.0/24"
    load_balancer_sku = "standard"
  }
}


# --- Private DNS Zone ---
resource "azurerm_private_dns_zone" "postgres_zone" {
  name                = "privatelink.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "dns_link" {
  name                  = "dns-link"
  resource_group_name   = azurerm_resource_group.rg.name
  private_dns_zone_name = azurerm_private_dns_zone.postgres_zone.name
  virtual_network_id    = azurerm_virtual_network.vnet.id
}
