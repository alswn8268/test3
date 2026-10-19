# 사실 확인 — ep02_filter 필터는 Ctrl+Shift+L

- 출처는 국세청·법령정보센터·정부 누리집 같은 **공식 출처**를 우선으로 적습니다.
- 확인 칸: 출처 원문을 눈으로 확인했으면 `✅`, 틀렸으면 `❌` 후 대본 수정.

| # | 장면 | 화면 문구 | 출처 (URL) | 확인 |
|---|---|---|---|---|
| 1 | 02 | 한 번 더 누르면 필터가 꺼져요 / 표 아무 칸에서 / Ctrl + Shift + L | https://support.microsoft.com/en-us/office/use-a-screen-reader-to-sort-or-filter-a-table-in-excel-d6ae119c-5fab-4b7f-8869-6ef02ece71f5 | ✅ Claude: "To clear the filter and remove the AutoFilter dropdown menus, select any cell in the range and press Ctrl+Shift+L." |
| 2 | 03 | 열 머리글마다 필터 메뉴 / 머리글마다 / ▼ 버튼이 생겨요 | https://support.microsoft.com/en-us/accessibility/excel/keyboard-shortcuts-in-excel | ✅ Claude: "Turn the AutoFilter dropdown menu in a column heading off and on" |
| 3 | 04 | 마우스 없이 필터 목록이 열려요 / 머리글 칸에서 / Alt + ↓ | https://support.microsoft.com/en-us/office/use-a-screen-reader-to-sort-or-filter-a-table-in-excel-d6ae119c-5fab-4b7f-8869-6ef02ece71f5 | ✅ Claude: "In the table header of the column you want to filter, press Alt+Down arrow key." |
| 4 | 05 | 항목 체크·해제 / 방향키로 고르고 / 스페이스바 | https://support.microsoft.com/en-us/office/use-a-screen-reader-to-sort-or-filter-a-table-in-excel-d6ae119c-5fab-4b7f-8869-6ef02ece71f5 | ✅ Claude: "press the Down arrow key or until you hear "Select all, menu item," and then press Spacebar." |
| 5 | 06 | 오름차순 · 내림차순 / 같은 목록에 / 정렬도 있어요 | https://support.microsoft.com/en-us/office/use-a-screen-reader-to-sort-or-filter-a-table-in-excel-d6ae119c-5fab-4b7f-8869-6ef02ece71f5 | ✅ Claude: "Press Alt+Down arrow key to open the drop-down menu. To sort the data, press the Down arrow key until you hear" |
| 6 | 07 | SUBTOTAL 은 필터로 숨긴 행을 빼고 계산 / 걸러진 것만 / 합계 내기 | https://support.microsoft.com/en-us/excel/get-started/total-the-data-in-an-excel-table | ✅ Claude: "The table will automatically convert them to a SUBTOTAL function, which will ignore rows that have been hidden with a filter by default." |
| 7 | 08 | 합계가 SUBTOTAL 로 들어가요 / 표 요약 행을 / 켜면 자동 | https://support.microsoft.com/en-us/excel/get-started/total-the-data-in-an-excel-table | ✅ Claude: "The table will automatically convert them to a SUBTOTAL function, which will ignore rows that have been hidden with a filter by default." |
| 8 | 09 | 팁 / Alt + ↓ → 필터 해제 → Enter / 한 열만 풀 땐 / 필터 해제 | https://support.microsoft.com/en-us/office/use-a-screen-reader-to-sort-or-filter-a-table-in-excel-d6ae119c-5fab-4b7f-8869-6ef02ece71f5 | ✅ Claude: "press the Down arrow key until you hear "Clear filter from," followed by the coordinates of the filtered cell, and then press Enter." |
| 9 | 10 | 팁 / 이동 옵션 → 화면에 보이는 셀만 / 숨긴 행 빼고 / 복사하려면 | https://support.microsoft.com/en-us/excel/copy-visible-cells-only | ✅ Claude: "On the Home tab, in the Editing group, select Find & Select, and then select Go To Special. Under Select, select Visible cells only, and then select OK." |
| 10 | 11 | 지금 해보기 / 표 칸 클릭 / Ctrl + Shift + L / Alt + ↓ 로 고르기 | https://support.microsoft.com/en-us/office/use-a-screen-reader-to-sort-or-filter-a-table-in-excel-d6ae119c-5fab-4b7f-8869-6ef02ece71f5 | ✅ Claude: "In the table header of the column you want to filter, press Alt+Down arrow key." |

## 확인 메모 (2026-10-19, Claude 위임)
- 이 클라우드 환경에서는 공식 사이트 직접 접속(WebFetch)이 막혀 있어, 공식 도메인으로 한정한 WebSearch 결과에 나온 원문 문장으로 확인했습니다.
- 뺀 내용: 'Alt + ;'(MS 공식 문서에서 확인 못 함) → 이동 옵션 → 화면에 보이는 셀만. 'SUBTOTAL 9 / 109'(원문 문장 확인 못 함) → 표 요약 행이 SUBTOTAL 로 바뀌는 원문으로 교체. '빈 줄이 있으면 범위가 끊김'(AutoFilter 공식 원문 없음) → 한 열 필터 해제로 교체.
