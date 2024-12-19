### Azure Stack Provision Example via Cloud Development Kit for Terraform (CDKTF)

Example of Azure Stack based on [cdk.tf](https://cdk.tf)

Cloud Development Kit for Terraform (CDKTF) allows you to use familiar programming languages to define and provision infrastructure. This gives you access to the entire Terraform ecosystem without learning HashiCorp Configuration Language (HCL) and lets you leverage the power of your existing toolchain for testing, dependency management, etc.

Current soltuion use pure Python implementation, so you don't need to utilise HCL Terraform approach to deploy infrastructure for Azure, CDKTF trasform Python into terraform-compatible configuration that will execute perfectly without any extra efforts


### Requirements:

* terraform 1.6.0
* Python >= 3.8
* pipenv 2024.0.1
* cdktf 0.20.10
* nodeJS v22.12.0
* azure-cli 2.67.0
* core      2.67.0
* telemetry   1.1.0

### Dependencies

* msal 1.31.0
* azure-mgmt-resource 23.1.1
* cdktf-cdktf-provider-azurerm 12.27.0
* cdktf-cdktf-provider-random  11.0.3

### Quick start

TBD

### Environment setup

TBD

### TODO

* Create Docker image with basic for Quick Start
* Update README.md documentation how to quick start
* Update README.md documentation how to run CDKTF locally
* Python Tests for CDKTF Azure stack

### Acknowledgments
* Much appreciated to [SET University](https://www.setuniversity.edu.ua/en/) in scope of which this library was 
developed as part of final project for Python course as part of Master's deegree program for [ML & Cloud Computing](https://www.setuniversity.edu.ua/en/education/computer-science-machine-learning-cloud-computing/)
* Big kudos to tutor and mentor [Dmytro Hridin](https://github.com/dmytrohridin)

### License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.