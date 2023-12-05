# JungkoScrapper

모든 중고거래 마켓을 한 곳에 보는 "중코거래" 서비스의 스크래퍼 프로젝트입니다.

AWS Step Functions를 이용하여 주기적으로 상품 정보 스크래핑을 수행하고, 키워드를 추출한 뒤 회원들에게 키워드 알림을 보내는 기능을 수행합니다.

## Prerequisites

- Docker Desktop 설치가 필요합니다.
  https://www.docker.com/products/docker-desktop/
- AWS CLI 설치가 필요합니다.
  https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/cli-chap-install.html
- AWS SAM CLI 설치가 필요합니다.
  https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html
- 중코거래 서버 프로젝트와 클라이언트 프로젝트가 실행되어 있다고 가정합니다.

  서버 프로젝트 레포지토리: https://github.com/TeamJungKo/jungko-server
  클라이언트 프로젝트 레포지토리: https://github.com/TeamJungKo/jungko-client

## Build and Deploy

```bash
aws configure --profile jungko
```

aws configure 명령어를 통해 AWS CLI를 설정합니다. AWS Access Key ID, AWS Secret Access Key, Default region name, Default output format을 입력합니다.

```bash
sam build --template template.yaml
```

⚠️ 중코거래 프로젝트 팀원이 아니라면 template.yaml.example 파일을 참고하여 template.yaml 파일을 생성해야 합니다.

sam build 명령어를 통해 AWS Lambda Function 들을 빌드합니다.

```bash
sam package --template-file .aws-sam/build/template.yaml --output-template-file packaged.yml --s3-bucket jungko-scrapper-deploy-main --profile jungko
```

sam package 명령어를 통해 빌드된 AWS Lambda Function 들을 S3에 업로드합니다.

```bash
sam deploy --template-file packaged.yml --stack-name scheduled-scrapping-task --capabilities CAPABILITY_IAM --profile jungko
```

sam deploy 명령어를 통해 S3에 업로드된 AWS Lambda Function 들을 CloudFormation을 통해 배포합니다.

## Local development

```bash
sam local invoke ScrapProductInfoFunction --event events/event.json --template .aws-sam/build/template.yaml
```

sam local invoke 명령어를 통해 로컬에서 컨테이너 환경 위에 AWS Lambda Function을 실행할 수 있습니다.
sam local invoke의 인자로 실행할 AWS Lambda Function의 이름과 이벤트 파일을 전달합니다.

```bash
aws --profile jungko ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws
```

ECR에 로그인되어 있지 않다면 위 명령어를 통해 public ECR에 로그인이 필요합니다.

`--skip-pull-image` 인자를 통해 이미지 pull을 생략할 수 있습니다.

## Cleanup

```bash
aws cloudformation delete-stack --stack-name "scheduled-scrapping-task" --profile jungko
```

다음 명령어를 통해 배포된 CloudFormation Stack을 삭제할 수 있습니다.
