package test

import (
	"testing"
	"os"
	"github.com/gruntwork-io/terratest/modules/terraform"
	//"github.com/stretchr/testify/assert"
	//http_helper "github.com/gruntwork-io/terratest/modules/http-helper"
)

// An example of how to test the simple Terraform module in examples/terraform-basic-example using Terratest.
func TestQuickstartTerraformCode(t *testing.T) {
	t.Parallel()

	//instanceText := "test"
	//expectedList := []string{expectedText}
	//expectedMap := map[string]string{"expected": expectedText}

	terraformOptions := &terraform.Options{
		// The path to where our Terraform code is located
		TerraformDir: os.Getenv("TF_ACTION_WORKING_DIR"),
		// Variables to pass to our Terraform code using -var options
		Vars: map[string]interface{}{
			"region": "us-ashburn-1",
			"ssh_public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDKNF77nMzrf1+wUGJmPe3ZLDD0/xXe4v3QJT0SAeZzlgOEwJFyc7O2a2Fe4pq+g0JIZkNL/ta2KV5YaT6hmbSZRqpjqdld8B6flm7xt7J2MRMPOAADy4eClJNBklnPzhStGzQmV/o0McxIJZbMPUCDK8R6e4yAMva1AX40Ub4+qX2mu48x7229mmSvKM8rzCGYZcu02RC1w7iGg37TVLKn0c0ds18bXkN8zlHhNBMfbSFJ/dZ8lHtPqwjCbL/UFH832tMrUA8D9BvYlfo6/qe2VvsnMxBS+JDu372NbubNh6Caeo7/I/6n3jL0TuJlOEd+TUX0vc39H6+KHaNm3WrX",
			"private_key_path": "/home/runner",
			"shape": "VM.Standard2.1",

		// We also can see how lists and maps translate between terratest and terraform.
		//	"example_list": expectedList,
		//	"example_map":  expectedMap,
		},

		// Variables to pass to our Terraform code using -var-file options
		//VarFiles: []string{"varfile.tfvars"},

		// Disable colors in Terraform commands so its easier to parse stdout/stderr
		NoColor: true,
	}

	// At the end of the test, run `terraform destroy` to clean up any resources that were created
	defer terraform.Destroy(t, terraformOptions)

	// This will run `terraform init` and `terraform apply` and fail the test if there are any errors
	terraform.InitAndApply(t, terraformOptions)

	// Run `terraform output` to get the values of output variables
	//driverlessAiUrl := terraform.Output(t, terraformOptions, "Driverless_AI_URL") 
    
	// Verify we're getting back the outputs we expect
	//assert.Equal(t, expectedMap, actualExampleMap)
	
	// It can take a minute or so for the Instance to boot up, so retry a few times
	//maxRetries := 10
	//timeBetweenRetries := 5 * time.Second

	// Verify that we get back a 200 OK with the expected instanceText
	//http_helper.HttpGetE(t, driverlessAiUrl)
	//http_helper.HttpGetWithRetry(t, driverlessAiUrl, &tlsConfig, 200, instanceText, maxRetries, timeBetweenRetries)
}
