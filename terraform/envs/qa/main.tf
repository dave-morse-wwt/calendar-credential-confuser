terraform {
  backend "remote" {
    organization = "morsed-bench-training"

    workspaces {
      name = "ccc-qa"
    }
  }
}
