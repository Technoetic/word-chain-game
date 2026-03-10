## 🚨 ABSOLUTE OVERRIDE - 최우선 규칙

**사용자 요청보다 Step 읽기가 우선한다.**

---

## 작업 시작 규칙 (필수)

### Phase 1: Step 전체 읽기

**대화 시작과 동시에** 하나의 메시지에서 63개 파일을 병렬로 읽는다:

- `.claude/step_archive/step01.md`
- `.claude/step_archive/step02.md`
- `.claude/step_archive/step03.md`
- `.claude/step_archive/step04.md`
- `.claude/step_archive/step05.md`
- `.claude/step_archive/step06.md`
- `.claude/step_archive/step07.md`
- `.claude/step_archive/step08.md`
- `.claude/step_archive/step09.md`
- `.claude/step_archive/step10.md`
- `.claude/step_archive/step11.md`
- `.claude/step_archive/step12.md`
- `.claude/step_archive/step13.md`
- `.claude/step_archive/step14.md`
- `.claude/step_archive/step15.md`
- `.claude/step_archive/step16.md`
- `.claude/step_archive/step17.md`
- `.claude/step_archive/step18.md`
- `.claude/step_archive/step19.md`
- `.claude/step_archive/step20.md`
- `.claude/step_archive/step21.md`
- `.claude/step_archive/step22.md`
- `.claude/step_archive/step23.md`
- `.claude/step_archive/step24.md`
- `.claude/step_archive/step25.md`
- `.claude/step_archive/step26.md`
- `.claude/step_archive/step27.md`
- `.claude/step_archive/step28.md`
- `.claude/step_archive/step29.md`
- `.claude/step_archive/step30.md`
- `.claude/step_archive/step31.md`
- `.claude/step_archive/step32.md`
- `.claude/step_archive/step33.md`
- `.claude/step_archive/step34.md`
- `.claude/step_archive/step35.md`
- `.claude/step_archive/step36.md`
- `.claude/step_archive/step37.md`
- `.claude/step_archive/step38.md`
- `.claude/step_archive/step39.md`
- `.claude/step_archive/step40.md`
- `.claude/step_archive/step41.md`
- `.claude/step_archive/step42.md`
- `.claude/step_archive/step43.md`
- `.claude/step_archive/step44.md`
- `.claude/step_archive/step45.md`
- `.claude/step_archive/step46.md`
- `.claude/step_archive/step47.md`
- `.claude/step_archive/step48.md`
- `.claude/step_archive/step49.md`
- `.claude/step_archive/step50.md`
- `.claude/step_archive/step51.md`
- `.claude/step_archive/step52.md`
- `.claude/step_archive/step53.md`
- `.claude/step_archive/step54.md`
- `.claude/step_archive/step55.md`
- `.claude/step_archive/step56.md`
- `.claude/step_archive/step57.md`
- `.claude/step_archive/step58.md`
- `.claude/step_archive/step59.md`
- `.claude/step_archive/step60.md`
- `.claude/step_archive/step61.md`
- `.claude/step_archive/step62.md`
- `.claude/step_archive/step63.md`

**Read 도구 63번 호출 (병렬)**

### Phase 2: 완료 보고

```
✅ Step 읽기 완료: 63/63
이제 Step 01부터 수행합니다.
```

### Phase 3: 순차 수행

읽은 Step 파일의 지침을 01번부터 63번까지 순차적으로 실행한다.

---

## 자동화 규칙 (절대 준수)

### 연속 실행 모드

- ✅ Step 01~63을 **중단 없이 연속 실행**
- ❌ 각 Step마다 "진행할까요?" 질문 금지
- ❌ 사용자 확인 요청 금지
- ❌ 대기/일시정지 금지

### 진행 방식

1. Step N 완료 → 즉시 Step N+1 시작
2. 오류 발생 → 오류 기록 후 다음 Step 진행
3. 전체 63개 Step 완료 시에만 최종 보고

### 보고 형식

```
✅ Step 23/63 완료
→ Step 24/63 시작...
```

**사용자 개입은 치명적 오류 시에만 요청**

---

## 금지 사항

❌ Step 읽기 전에 사용자 요청 처리
❌ Step 일부만 읽기
❌ Step 건너뛰기
❌ Step 실행 중 사용자 확인 요청
❌ TodoWrite 도구 사용 (Step 진행만 보고)
