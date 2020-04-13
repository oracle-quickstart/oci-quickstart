package test

import (
	"testing"
	"os"
	"github.com/gruntwork-io/terratest/modules/terraform"
)

func TestQuickstartTerraformCode(t *testing.T) {
	t.Parallel()

	terraformOptions := &terraform.Options{
		// The path to where our Terraform code is located
		TerraformDir: os.Getenv("TF_ACTION_WORKING_DIR"),

		// Variables to pass to our Terraform code using -var options
		Vars: map[string]interface{}{
			"region": "us-ashburn-1",
			"ssh_public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDKNF77nMzrf1+wUGJmPe3ZLDD0/xXe4v3QJT0SAeZzlgOEwJFyc7O2a2Fe4pq+g0JIZkNL/ta2KV5YaT6hmbSZRqpjqdld8B6flm7xt7J2MRMPOAADy4eClJNBklnPzhStGzQmV/o0McxIJZbMPUCDK8R6e4yAMva1AX40Ub4+qX2mu48x7229mmSvKM8rzCGYZcu02RC1w7iGg37TVLKn0c0ds18bXkN8zlHhNBMfbSFJ/dZ8lHtPqwjCbL/UFH832tMrUA8D9BvYlfo6/qe2VvsnMxBS+JDu372NbubNh6Caeo7/I/6n3jL0TuJlOEd+TUX0vc39H6+KHaNm3WrX",
			"shape": "VM.Standard2.1",
		},
		NoColor: true,
	}

	// At the end of the test, run `terraform destroy` to clean up any resources that were created
	defer terraform.Destroy(t, terraformOptions)

	// This will run `terraform init` and `terraform apply` and fail the test if there are any errors
	terraform.InitAndApply(t, terraformOptions)
}
