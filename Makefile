.PHONY: help setup check test stills render assemble review

EP ?= ep01

help:  ## 명령 목록
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS=":.*?## "}; {printf "  \033[36m%-9s\033[0m %s\n", $$1, $$2}'

setup:    ## 처음 한 번: 라이브러리 설치 + render/vendor 준비
	PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install
	npm run setup

check:    ## 전체 대본 규칙 검사
	python3 -m tools.validate --all

test:     ## 도구 단위 테스트
	python3 -m pytest

stills:   ## 미리보기 PNG 12장 (make stills EP=ep02)
	node render/capture.mjs $(EP) --stills

render:   ## 사실 확인 통과 후 장면 클립 12개
	python3 -m tools.validate $(EP)
	python3 -m tools.factcheck $(EP) --check
	node render/capture.mjs $(EP)

assemble: ## 클립 → final.mp4 + captions.srt (ffmpeg 대체 경로)
	python3 -m tools.assemble $(EP)

review:   ## metrics.csv 판정표
	python3 -m tools.review
