.PHONY: help setup check test stills render assemble batch drafts review analyze

CH ?= money
EP ?= ep01

help:  ## 명령 목록 (CH=채널 EP=편)
	@grep -E '^[a-z-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS=":.*?## "}; {printf "  \033[36m%-9s\033[0m %s\n", $$1, $$2}'

setup:    ## 처음 한 번: 라이브러리 설치 + render/vendor 준비
	PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install
	npm run setup
	python3 -m pip install -r requirements.txt

check:    ## 모든 채널 대본 규칙 검사
	python3 -m tools.validate --all

test:     ## 도구 단위 테스트
	python3 -m pytest

stills:   ## 미리보기 PNG 12장 (make stills CH=shortcut EP=ep02)
	node render/capture.mjs $(CH) $(EP) --stills

render:   ## 사실 확인 통과 후 장면 클립 12개
	python3 -m tools.validate $(CH) $(EP)
	python3 -m tools.factcheck $(CH) $(EP) --check
	node render/capture.mjs $(CH) $(EP)

assemble: ## 클립 + 자체 BGM·효과음 → final.mp4 + captions.srt
	python3 -m tools.assemble $(CH) $(EP)

batch:    ## 모든 채널·모든 편 (사실 확인 통과한 편만), 채널 3개 동시
	python3 -m tools.batch --all --jobs 3

drafts:   ## 사실 확인 전 초안까지 전부 렌더 (업로드 금지)
	python3 -m tools.batch --all --draft --jobs 3

review:   ## 한 채널 metrics.csv 판정표
	python3 -m tools.review $(CH)

analyze:  ## refs/ 폴더의 참고 영상 분석
	python3 -m tools.analyze_ref refs/*.mp4
