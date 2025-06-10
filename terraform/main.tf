# terraform/main.tf

resource "azurerm_resource_group" "test" {
  name     = "tf-test-rg"
  location = "eastus"
}
