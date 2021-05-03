# K8S Ecr Renew Token

This is gcavalcante8808/ecr-renew-token [helm chart](https://helm.sh/) that aims to provide a helper to create AWS ECR Image Pull secrets token on kubernetes clusters as the tokens are valid for only 12 hours.

More info about ECR Tokens: [Authenticating Amazon ECR Repositories for Docker CLI with Credential Helper | AWS Compute Blog](https://aws.amazon.com/blogs/compute/authenticating-amazon-ecr-repositories-for-docker-cli-with-credential-helper/)

## Requirements & Usage

To use this project, you'll need the following software:

- Git (to clone this repo :D);
  
- Helm 3;
  
- A kubernetes cluster;
  
- An AWS Programmatic credential ("Aws keys") with proper IAM permissions to pull docker images from the target ECR repo. More info at [Amazon Elastic Container Registry Identity-Based Policy Examples - Amazon ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/security_iam_id-based-policy-examples.html) and [Repository policy examples - Amazon ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/repository-policy-examples.html)
  

With that information in mind, you can a command like the following to install the helm chart from a local folder (after cloning the repository):

```bash
cd charts/ecr-renew-token
helm upgrade --install my-release \
--namespace some-namespace \
--create-namespace=true . \
--set-string aws.access_key_id="SOME_ACCESS_KEY_ID" \
--set-string aws.secret_access_key="SOME_SECRET_ACCESS_KEY" \
--set-string aws.region="us-east-1" \
--set-string secret_name="my-ecr-docker-config-json" \
--set-string cronjob_schedule="0 */1 * * *" # Run every hour at minute 0
```

### Information about needed values

Those are the required values that need to be set:

| Value | Description |
| --- | --- |
| aws.access_key_id | AWS_ACCESS_KEY_ID value as stated in https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html |
| aws.secret_access_key | AWS_SECRET_ACCESS_KEY value as stated in https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html |
| aws.region | AWS_REGION value as stated in https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html |

You should take a look at the following values as well, as they define secret name and schedule:

| Value | Description |
| --- | --- |
| secret_name | The name of the secret that will be created in the namespace where the helm chart was installed. Default: "ecr-token" |
| cronjob_schedule | The schedule for the cronjob. By default it runs at minute 0 past every 4th hour ("0 */4 * * *"). |

## Important Notes

By default, as soon the pod is created by the kubernetes job, it will install `python-kubernetes` and `boto3` libraries from pypi,
so outgoing connection is required to run the project.

Author
------

Author: Gabriel Abdalla Cavalcante Silva (gabriel.cavalcante88@gmail.com)
