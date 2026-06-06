# 2026년 전공분야 보수교육(기본교육) 과정안내서
## [인공지능] RAG 기반 AI 응용서비스 설계 2일 코스

본 저장소는 훈련 교ㆍ강사 보수교육(기본-전공) 과정
「[인공지능] RAG 기반 AI 응용서비스 설계 2일 코스」의 교육자료와 실습 코드를 제공합니다.

---

## 교육 개요

| 구분 | 내용 |
|------|------|
| **교육구분** | 훈련 교ㆍ강사 보수교육(기본-전공) |
| **교육분야** | 대분류 `20.정보통신` / 중분류 `01.정보기술` / 소분류 `07.인공지능` |
| **교육대상** | 민간직업훈련기관 종사자(교ㆍ강사 및 행정직원) |
| **교육수준** | 중급 |
| **선수지식** | Python 기초 문법 이해, 기본적인 AI/머신러닝 개념 이해, LLM 활용 경험 |
| **교육시간** | 12시간 |
| **교육방법** | 집체 |
| **신기술 교육기법** | PBL(Project-Based Learning) + 플립러닝(Flipped Learning) + 실습중심(Hands-on Coding) |
| **평가방법** | 실습평가(과제제출) |
| **필요매체(교수자/학습자)** | PC / 인터넷 |

### 교육목표

- RAG(Retrieval-Augmented Generation)의 구조와 동작 원리를 이해하고, 단순 LLM 기반 응답 방식과의 차이를 설명할 수 있다.
- 프롬프트, LCEL, 벡터 검색을 바탕으로 문서 기반 질의응답 파이프라인을 구조적으로 이해하고 직접 구성할 수 있다.
- Chunking, Query Transformation, Hybrid Retrieval, Evaluation, Langfuse 트레이싱을 통해 RAG 시스템의 품질을 개선하고 설명할 수 있는 역량을 확보한다.

---

## 주요 습득 역량

- `2001070504_20v1` / 인공지능서비스 애플리케이션 개발
- `2001021508_21v1` / 클라우드 네트워크 서비스 개발
- `2001070204_22v2` / 인공지능 서비스 모델 기획
- `2001070508_20v1` / 인공지능서비스 이행

### 기대효과

- RAG 기반 AI 응용 서비스의 구조적 이해 역량 확보
- 실무 적용을 고려한 RAG 설계 및 개선 역량 강화
- RAG 시스템 운영 및 분석 역량 확보
- 직업훈련 현장 적용 가능성 확대

---

## 교육 내용 요약

| 단원명 | 시간 | 학습방법 | 주요내용 |
|------|------:|------|------|
| 환경 설정 및 LangChain 기초 | 1 | 이론/실습 | 실습 환경 구성, OpenAI API Key 설정 및 보안 주의, LangChain 핵심 구성 요소 이해 |
| 프롬프트와 LCEL 기본 체인 구성 | 1 | 이론/실습 | PromptTemplate / ChatPromptTemplate 이해, LCEL 연결, invoke·ainvoke·batch·stream 비교 |
| RAG 개요와 벡터 검색 원리 | 1.5 | 이론 | LLM 기반 응답의 한계, RAG 기본 구조, 임베딩·벡터 DB·FAISS 이해 |
| 기본형 RAG 구성과 한계 이해 | 1.5 | 이론/실습 | 기본 파이프라인 이해, 문서 기반 Q&A 체인 구성, Indexing·Retrieval·Generation 한계 체감 |
| Advanced RAG 입문: Chunking과 Query Rewriting | 1 | 이론/실습 | Chunk 전략 비교, Query Rewriting 개념 이해 및 실습 |
| Query Transformation 확장 및 Retrieval 고도화 | 1.5 | 이론/실습 | Multi-Query, HyDE, Dense/Sparse Retrieval, Hybrid Retrieval, RRF 실습 |
| Post-Retrieval 및 Generation 최적화 | 1.5 | 이론/실습 | 후보군 점검, Filtering, Compression, Deduplication, Citation, Fail-safe 설계 |
| RAG 성능 평가 | 1 | 이론/실습 | Recall@K 중심 Retrieval 평가, Faithfulness 중심 Generation 평가, 결과 해석 |
| Langfuse 기반 운영 및 모니터링 | 1 | 이론/실습 | Langfuse 가입, 프로젝트 생성, API Key 설정, trace 분석 |
| 개인별 최종 과제 수행 및 제출 | 1 | 실습 | baseline 실행, 개선 포인트 적용, 점수 확인 및 제출 양식 작성 |

---

## 세부 시간표

| 일차 | 시간 | 단원명 | 세부 학습 내용 | 학습방법 |
|------|------|------|------|------|
| 1일차 | 10:00~11:00 | 환경 설정 및 LangChain 기초 | 실습 환경 구성, OpenAI API Key 설정 및 보안 주의, LangChain 핵심 구성 요소 이해 | 이론/실습 |
| 1일차 | 11:00~12:00 | 프롬프트와 LCEL 기본 체인 구성 | PromptTemplate / ChatPromptTemplate 이해, LCEL 기반 Q&A 체인 구성, invoke·ainvoke·batch·stream 비교 | 이론/실습 |
| 1일차 | 13:00~14:30 | RAG 개요와 벡터 검색 원리 | LLM 기반 응답의 한계와 RAG 등장 배경, RAG 개념 및 전체 구조, 임베딩·벡터 DB·FAISS 이해 | 이론 |
| 1일차 | 14:30~16:00 | 기본형 RAG 구성과 한계 이해 | 기본 파이프라인 이해, 문서 기반 Q&A 체인 구성 실습, Indexing / Retrieval / Generation 단계 한계 분석 | 이론/실습 |
| 1일차 | 16:00~17:00 | Advanced RAG 입문: Chunking과 Query Rewriting | Chunking 전략 비교, Query Rewriting 개념 및 실습, Advanced RAG 확장 관점 이해 | 이론/실습 |
| 2일차 | 09:00~10:30 | Query Transformation 확장 및 Retrieval 고도화 | Multi-Query, HyDE, Dense Retrieval과 Sparse Retrieval(BM25) 비교, Hybrid Retrieval과 RRF 실습 | 이론/실습 |
| 2일차 | 10:30~12:00 | Post-Retrieval 및 Generation 최적화 | 후보군 점검, Context Filtering, Compression, Deduplication, Citation, Fail-safe 설계 | 이론/실습 |
| 2일차 | 13:00~14:00 | RAG 성능 평가 | Recall@K 중심 Retrieval 평가, Faithfulness 중심 Generation 평가, 평가 결과 해석 및 개선 포인트 도출 | 이론/실습 |
| 2일차 | 14:00~15:00 | Langfuse 기반 운영 및 모니터링 | Langfuse 가입, 프로젝트 생성, API Key 설정, RAG 실행 흐름 트레이싱 및 trace 분석, Evaluation과 Monitoring 구분 | 이론/실습 |
| 2일차 | 15:00~16:00 | 개인별 최종 과제 수행 및 제출 | baseline 실행 및 개선 포인트 선정, Retrieval / Generation 개선 적용, 점수 확인 및 제출 양식 작성 | 실습 |

---

## 실습 환경 준비

본 과정의 모든 실습은 **Python 3.10 기반 Conda 가상환경**에서 진행됩니다.  
원활한 실습 진행을 위해 아래 절차를 **사전에 반드시 완료**해 주시기 바랍니다.

### 1. Anaconda 설치

본 실습은 **Conda 기반 Python 가상환경**을 사용합니다.  
아래 공식 페이지에서 운영체제(Windows / macOS / Linux)에 맞는 **Anaconda**를 먼저 설치해 주세요.

Anaconda 공식 다운로드 페이지:  
https://www.anaconda.com/download/success

### 2. Conda 가상환경 생성 (Python 3.10)

```bash
conda create -n py310 python=3.10
```

### 3. 가상환경 활성화

```bash
conda activate py310
```

### 4. 실습에 필요한 패키지 설치

본 저장소 루트 디렉터리에 포함된 `requirements.txt` 파일을 사용하여  
실습에 필요한 모든 라이브러리를 설치합니다.

```bash
pip install -r requirements.txt
```

### 5. VS Code 설치 (선택)

본 과정의 실습은 Jupyter Notebook 또는 Visual Studio Code(VS Code)를 활용하여 진행됩니다.  
원활한 실습과 코드 관리, 디버깅을 위해 **VS Code 사용을 권장**합니다.

VS Code가 설치되어 있지 않은 경우, 아래 공식 홈페이지를 통해 설치해 주세요.

https://code.visualstudio.com/

---

## 교육 장소

**한국휴렛팩커드 교육센터**  
서울특별시 서초구 서운로 220, 대지프라자 6층

**대중교통 안내**
- 9호선/신분당선 신논현역 9번 출구 → 직진 240m, 현대오일뱅크 좌회전 후 도미노피자 건물 6층
- 2호선 강남역 9번 출구 → 시내버스(146, 341) 또는 마을버스(11) 이용, 도보 20분 내외
- 주차지원 불가

---

## 문의

**강사 문의:** `rlaalstn1504@naver.com`

---

> © 2026. RAG 기반 AI 응용서비스 설계 2일 코스  
> 본 자료는 훈련 교ㆍ강사 보수교육(기본-전공) 과정 전용으로 제작되었습니다.
