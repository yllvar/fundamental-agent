# 🤖 AI 기사 Create System Guide

## 📋 Overview

완전 자동화된 AI 기사 Create pipeline Streamlit Dashboard에 통합되었습니다. 이벤트 감지부터 기사 작성, 이미지 Create, 검수, 광고 추천까지 원스톱으로 제공합니다.

## 🚀 주요 Features

### 🔄 **자동 이벤트 감지 System**
- **실시간 시장 Data**: 주요 종목의 가격 변동 감지
- **Economic  지표 모니터링**: VIX, 주요 지수 변화 추적
- **보장된 이벤트 Create**: 5분마다 무조건 기사 Create 가능
- **다양한 주제**: 시장 Analysis, 개별 종목, Economic  전망, 섹터 Analysis

### 🤖 **AI Agent 파이프라인**
1. **📊 Data Analysis Agent**: Economic  Data 심층 Analysis
2. **✍️ 기사 작성 Agent**: 고품질 Economic  기사 자동 Create
3. **🎨 이미지 Create Agent**: 관련 차트 및 illustration
4. **🔍 검수 Agent**: 품질 검수 및 개선 제안
5. **📢 광고 추천 Agent**: 기사 내용 기반 맞춤 광고

### 🔄 **5분 자동 새로고침**
- **자동 Create**: 5분마다 새로운 기사 자동 Create
- **수동 제어**: 언제든지 수동으로 기사 Create 가능
- **진행률 표시**: 실시간 Create 과정 모니터링

## 🎯 Usage

### 1. **접속 방법**
```
브라우저: http://localhost:8501
페이지 선택: 🤖 AI 기사 Create
```

### 2. **Configuration 옵션**
- **🔄 5분 자동 새로고침**: 체크 시 자동으로 새 기사 Create
- **기사 유형**: 시장 Analysis, 개별 종목, Economic  전망, 섹터 Analysis
- **Analysis 깊이**: 기본, 상세, 전문가
- **이미지 Create 포함**: 관련 차트 및 이미지 Create 여부
- **광고 추천 포함**: 맞춤 광고 추천 여부

### 3. **기사 Create 과정**
```
🚀 AI 기사 Create Start 버튼 클릭
    ↓
🔍 이벤트 감지 (실시간 시장 Data Analysis)
    ↓
📊 Data Analysis (AI Agent 기반 심층 Analysis)
    ↓
✍️ 기사 작성 (고품질 Economic  기사 자동 Create)
    ↓
🎨 이미지 Create (관련 차트 및 illustration)
    ↓
🔍 기사 검수 (품질 검수 및 개선 제안)
    ↓
📢 광고 추천 (기사 내용 기반 맞춤 광고)
    ↓
✅ 완성된 기사 표시
```

## 📊 Create되는 콘텐츠

### 📰 **완성된 기사**
- **제목**: AI Create 헤드라인
- **본문**: 구조화된 Economic  기사 내용
- **태그**: 관련 키워드 및 분류
- **품질 점수**: 1-10점 품질 평가

### 📈 **Data Analysis 차트**
- **라인 차트**: 시계열 Data 시각화
- **바 차트**: 비교 Analysis 차트
- **인터랙티브**: Plotly 기반 동적 차트

### 🖼️ **관련 이미지**
- **기사 illustration**: 내용 기반 맞춤 이미지
- **차트 및 그래프**: Data 시각화
- **이미지 설명**: 각 이미지의 상세 설명

### 🔍 **검수 Result**
- **품질 평가**: 다양한 기준별 점수
- **개선 제안**: 구체적인 개선 방향
- **신뢰도 Analysis**: Information의 정확성 평가

### 📢 **추천 광고**
- **맞춤 광고**: 기사 내용 기반 관련 광고
- **관련도 점수**: 1-10점 관련성 평가
- **타겟팅**: 독자 관심사 기반 추천

## 🔄 실시간 진행률 표시

### 📊 **진행률 바**
```
단계: 3/6 (50.0%) - 경과시간: 15.2초
🔄 현재 작업: 기사 작성 - AI 기사 작성 중...
```

### 📈 **단계별 Status**
```
[이벤트감지] ✅  [DataAnalysis] ✅  [기사작성] 🔄  
[이미지Create] ⏳  [기사검수] ⏳  [광고추천] ⏳
```

### 📝 **실시간 로그**
```
✅ [06:41:15] 🚀 주식 Data 수집을 Start합니다
ℹ️ [06:41:16] 🔍 Economic  이벤트 감지 Start
✅ [06:41:17] ✅ 3개 이벤트 감지 완료
  이벤트 1: META 주가 1.12% 상승
  이벤트 2: AMZN 주가 4.00% 상승
  이벤트 3: VIX 지수 1.08 하락, 시장 안정성 개선
ℹ️ [06:41:18] 🤖 AI Agent System 초기화
✅ [06:41:19] ✅ Data Analysis 완료
ℹ️ [06:41:20] ✍️ 기사 작성 Agent Run
```

## 💾 다운로드 Features

### 📄 **Support 형식**
- **기사 텍스트**: Markdown 형식 (.md)
- **Analysis Data**: JSON 형식 (.json)
- **전체 Result**: 종합 Data 패키지

### 📥 **다운로드 옵션**
1. **📄 기사 텍스트 다운로드**: 제목과 본문만
2. **📊 Analysis Data 다운로드**: Data Analysis Result
3. **📋 전체 Result 다운로드**: 모든 Create Result

## 🔧 기술적 특징

### 🤖 **AI Agent Architecture**
- **Strand Framework**: Agent 간 협업 프레임워크
- **비동기 처리**: 각 Agent 독립 Run
- **오류 복구**: 단계별 실패 시에도 계속 진행

### 📊 **이벤트 감지 System**
- **실시간 Data**: Yahoo Finance API 활용
- **다중 소스**: 주식, 지수, VIX 등 종합 모니터링
- **보장된 Create**: 이벤트가 없어도 기본 이벤트 Create

### 🔄 **자동화 Features**
- **5분 주기**: 자동 새로고침 옵션
- **세션 캐싱**: Create된 기사 세션 저장
- **진행률 추적**: 실시간 Status 모니터링

## 🎯 활용 사례

### 📰 **News 미디어**
- 실시간 Fundamental Agent 자동 Create
- 24시간 News 피드 운영
- 기자 업무 보조 도구

### 💼 **금융 기관**
- 고객용 시장 Analysis 리포트
- 투자 참고 자료 Create
- 내부 Analysis 보고서

### 📈 **투자 플랫폼**
- User 맞춤 시장 Analysis
- 실시간 투자 인사이트
- 교육용 콘텐츠 Create

## ⚠️ Notes

### 🔒 **면책 조항**
- Create된 기사는 Information 제공 목적으로만 Usage
- 투자 조언이 아니며 투자 결정은 개인 책임
- 중요한 투자 결정은 전문가와 상담 권장

### 🔍 **품질 관리**
- AI Create 콘텐츠는 검수 과정을 거침
- 사실 Check 및 Add 검증 권장
- 정기적인 System 모니터링 필요

## 🚀 향후 개선 계획

### 🔮 **예정 Features**
- **다국어 Support**: 영어, 중국어, 일본어 기사 Create
- **음성 변환**: 기사를 음성으로 변환
- **소셜 미디어 연동**: 자동 SNS 포스팅
- **개인화**: User 관심사 기반 맞춤 기사

### 📊 **성능 개선**
- **더 빠른 Create**: 병렬 처리 최적화
- **더 정확한 Analysis**: 고도화된 AI 모델 적용
- **더 다양한 소스**: Add Data 소스 통합

---

## 📞 Support 및 Contact

- **System Status**: Streamlit Dashboard에서 실시간 Check
- **로그 Check**: `streamlit_comprehensive.log` File
- **Troubleshooting**: 페이지 새로고침 또는 재Start

**🎉 이제 완전 자동화된 AI 기사 Create System을 활용해보세요!**
