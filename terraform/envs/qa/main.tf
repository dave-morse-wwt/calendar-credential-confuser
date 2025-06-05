terraform {
  backend "remote" {
    organization = "morsed-bench-training"

    workspaces {
      name = "ccc-qa"
    }
  }
}

module "infra" {
  source = "../../"

  # later, you can pass variables here like:
  # env = "qa"
}