terraform {
  required_version = ">= 1.12.1"

  required_providers {
    # The below versions are from the tutorial at https://learn.microsoft.com/en-us/azure/aks/learn/quick-kubernetes-deploy-terraform?pivots=development-environment-azure-cli
    # And are not the latest. 

    azurerm = {
      source  = "hashicorp/azurerm"
      # version = "~> 4.31" # latest rn
      version = "~>3.0"
    }
    azapi = {
      source  = "azure/azapi"
      version = "~>1.5"
    }
    random = {
      source  = "hashicorp/random"
      version = "~>3.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "0.9.1"
    }
  }
}

provider "azurerm" {
  features {}
}
