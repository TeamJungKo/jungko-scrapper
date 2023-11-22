#!/bin/bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
RESET='\033[0m'

echo -e $GREEN "이 스크립트는 jungko-scrapper 루트 디렉토리에서 실행되어야 합니다!!" $RESET

echo -e $GREEN "submodule 업데이트" $RESET
git submodule foreach git pull origin main

cp scrapper-config/template-local.yaml template.yaml

echo -e $GREEN "sam build 실행" $RESET
sam build

aws --profile jungko ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws

# 매개변수가 scrap, keyword, notice, all 인 경우
if [ "$1" == "scrap" ]; then
    echo -e $BLUE "ScrapProductInfoFunction 실행" $RESET

    sam local invoke ScrapProductInfoFunction --event events/event.json \
    --template .aws-sam/build/template.yaml

elif [ "$1" == "keyword" ]; then
    echo -e $PURPLE "ExtractKeywordsFunction 실행" $RESET

    sam local invoke ExtractKeywordsFunction --event events/event.json \
    --template .aws-sam/build/template.yaml

elif [ "$1" == "notice" ]; then
    echo -e $PURPLE "SendNotificationFunction 실행" $RESET

    sam local invoke SendNotificationFunction --event events/event.json \
    --template .aws-sam/build/template.yaml

elif [ "$1" == "all" ] || [ "$#" -eq 0 ]; then
    echo -e $RED "ProductNotificationStateMachine 실행" $RESET
    # TODO: 로컬에서 실행시키는 방법 찾기
    # sam local invoke ProductNotificationStateMachine --event events/event.json \
    # --template .aws-sam/build/template.yaml
fi
