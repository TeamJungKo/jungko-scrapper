#!/bin/bash

cp scrapper-config/template-main.yaml template.yaml

sam build --template template.yaml

sam package --template-file .aws-sam/build/template.yaml --output-template-file packaged.yml --s3-bucket jungko-scrapper-deploy-main --profile jungko

sam deploy --template-file packaged.yml --stack-name scheduled-scrapping-task --capabilities CAPABILITY_IAM --profile jungko
