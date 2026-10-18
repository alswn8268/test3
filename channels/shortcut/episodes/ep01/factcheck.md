# 사실 확인 — ep01_flashfill Ctrl+E 하나로 300줄 정리

- 출처는 국세청·법령정보센터·정부 누리집 같은 **공식 출처**를 우선으로 적습니다.
- 확인 칸: 출처 원문을 눈으로 확인했으면 `✅`, 틀렸으면 `❌` 후 대본 수정.

| # | 장면 | 화면 문구 | 출처 (URL) | 확인 |
|---|---|---|---|---|
| 1 | 02 | '김민주' → '김', 300명분 / 이름에서 / 성만 따로 | https://support.microsoft.com/ko-kr/office/%EC%9E%85%EB%A0%A5-%EB%82%B4%EC%9A%A9%EC%97%90-%EB%94%B0%EB%A5%B8-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EC%97%B4-%EB%B6%84%ED%95%A0-27326b11-2358-432c-bf78-cf49621fe76d | ✅ Claude: "한 개의 열에서 성과 이름을 분리하거나, 서로 다른 두 개의 열에서 성과 이름을 결합할 수 있습니다." |
| 2 | 03 | 패턴을 감지하면 나머지를 채워요 / 첫 칸만 쓰고 / Ctrl + E | https://support.microsoft.com/ko-kr/excel/enable-flash-fill-in-excel | ✅ Claude: "빠른 채우기는 패턴을 감지하면 자동으로 데이터를 입력합니다." |
| 3 | 04 | 옆 열을 보고 규칙을 알아채요 / 예시 한 칸이 / 곧 명령어 | https://support.microsoft.com/ko-kr/accessibility/excel/keyboard-shortcuts-in-excel | ✅ Claude: "인접한 열에서 패턴을 자동으로 인식하고 현재 열을 채우는 빠른 채우기 기능을 호출합니다." |
| 4 | 05 | 두 열 합치기도 / 두 열 김 / 민주 / 결과 김민주 | https://support.microsoft.com/ko-kr/office/%EC%9E%85%EB%A0%A5-%EB%82%B4%EC%9A%A9%EC%97%90-%EB%94%B0%EB%A5%B8-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EC%97%B4-%EB%B6%84%ED%95%A0-27326b11-2358-432c-bf78-cf49621fe76d | ✅ Claude: "한 개의 열에서 성과 이름을 분리하거나, 서로 다른 두 개의 열에서 성과 이름을 결합할 수 있습니다." |
| 5 | 06 | 나머지 줄을 미리 보여줘요 / 둘째 칸에 / 입력 시작하면 | https://support.microsoft.com/en-us/excel/using-flash-fill-in-excel | ✅ Claude: "Excel will sense the pattern you provide, and show you a preview of the rest of the column filled in with your combined text." |
| 6 | 07 | 메뉴로도 / Ctrl + E 와 같은 기능 / 데이터 탭 → / 빠른 채우기 | https://support.microsoft.com/ko-kr/excel/enable-flash-fill-in-excel | ✅ Claude: "데이터>빠른 채우기를 선택하여 수동으로 시작할 수 있습니다. 키보드에서 Ctrl+E를 누를 수도 있습니다." |
| 7 | 08 | 주의 / 기능이 꺼져 있을 수 있어요 / 미리 보기가 / 안 뜨면 | https://support.microsoft.com/en-us/excel/using-flash-fill-in-excel | ✅ Claude: "If Flash Fill doesn't generate the preview, it might not be turned on." |
| 8 | 09 | 주의 / 데이터 → 빠른 채우기 또는 Ctrl + E / 그럴 땐 / 직접 실행 | https://support.microsoft.com/ko-kr/excel/enable-flash-fill-in-excel | ✅ Claude: "데이터>빠른 채우기를 선택하여 수동으로 시작할 수 있습니다. 키보드에서 Ctrl+E를 누를 수도 있습니다." |
| 9 | 10 | 정리 / 한 열 나누기 · 두 열 합치기 / 나누기도 합치기도 / 예시 한 칸 | https://support.microsoft.com/ko-kr/office/%EC%9E%85%EB%A0%A5-%EB%82%B4%EC%9A%A9%EC%97%90-%EB%94%B0%EB%A5%B8-%EB%8D%B0%EC%9D%B4%ED%84%B0-%EC%97%B4-%EB%B6%84%ED%95%A0-27326b11-2358-432c-bf78-cf49621fe76d | ✅ Claude: "한 개의 열에서 성과 이름을 분리하거나, 서로 다른 두 개의 열에서 성과 이름을 결합할 수 있습니다." |
| 10 | 11 | 지금 해보기 / 예시 한 칸 입력 / 바로 아래 칸 선택 / Ctrl + E | https://support.microsoft.com/ko-kr/excel/enable-flash-fill-in-excel | ✅ Claude: "데이터>빠른 채우기를 선택하여 수동으로 시작할 수 있습니다. 키보드에서 Ctrl+E를 누를 수도 있습니다." |

## 확인 메모 (2026-10-18, Claude 위임)
- 이 클라우드 환경에서는 공식 사이트 직접 접속(WebFetch)이 막혀 있어, 공식 도메인으로 한정한 WebSearch 결과에 나온 원문 문장으로 확인했습니다.
- 뺀 내용: 전화번호 하이픈 넣기·이메일 아이디 뽑기·'결과는 값으로 남음'·'예시 한 칸 더'(MS 공식 문서 원문 없음, 커뮤니티 답변만 있음), '파일 → 옵션 → 고급' 경로(공식 문서 버전마다 경로가 달라 미확인).
