#!/usr/bin/env bash

set -e

tag=$(date +%Y%m%d%H%M%S)

requirements="requirements-$tag.zip"
code="lambda_code-$tag.zip"

docker run --rm -v "$PWD":/var/task "lambci/lambda:build-python3.8" /bin/sh -c "pip install --upgrade -r requirements.txt -t ./python; exit"

zip -r $requirements ./python
zip -r $code src

# THE PROBLEM CHILD
# aws s3 rm s3://group3-stack-deployment-needed/code/ --recursive --include "*"
aws s3 cp $requirements s3://group3-stack-deployment-needed/code/
aws s3 cp $code s3://group3-stack-deployment-needed/code/

rm $requirements $code

aws cloudformation deploy \
    --stack-name group3-stack-needed \
    --template-file deployment/templates/template-v1-create.yaml \
    --capabilities CAPABILITY_IAM \
    --parameter-override DeploymentRequirements="code/$requirements" DeploymentCode="code/$code"

# Upload our template to S3 for use with --create/update-stack commands
cd deployment/templates
aws s3 cp template-v1-create.yaml s3://group3-stack-deployment-needed/templates/
