#!/bin/bash

# 색상 설정
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}[1/3] Running Ruff (Linting & Formatting)...${NC}"
# 자동으로 코드 스타일을 고쳐줍니다 (--fix)
venv/bin/ruff check . --fix
if [ $? -ne 0 ]; then
    echo -e "${RED}Linting failed!${NC}"
    exit 1
fi

echo -e "${GREEN}[2/3] Running Mypy (Type Checking)...${NC}"
# 타입 에러를 검사합니다
venv/bin/mypy src
if [ $? -ne 0 ]; then
    echo -e "${RED}Type Check failed!${NC}"
    exit 1
fi

echo -e "${GREEN}[3/3] All Checks Passed! Starting App...${NC}"
./START_MAC.sh
