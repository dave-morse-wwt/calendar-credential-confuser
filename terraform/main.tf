# terraform/main.tf
resource "null_resource" "hello" {
  provisioner "local-exec" {
    command = "echo 'Terraform config is wired up!'"
  }
}
