# 📰 News & 소셜미디어 Data 출처 Analysis

## 📰 News Data 출처 (실제 RSS 피드)

### 1️⃣ **금융 News (Financial)**
| 매체명 | RSS 피드 URL | Status |
|--------|-------------|------|
| **Bloomberg Markets** | https://feeds.bloomberg.com/markets/news.rss | ✅ 실제 |
| **Reuters Business** | https://feeds.reuters.com/reuters/businessNews | ✅ 실제 |
| **MarketWatch** | https://feeds.marketwatch.com/marketwatch/topstories/ | ✅ 실제 |
| **CNN Money** | https://rss.cnn.com/rss/money_latest.rss | ✅ 실제 |
| **Yahoo Finance** | https://feeds.finance.yahoo.com/rss/2.0/headline | ✅ 실제 |
| **Financial Times** | https://www.ft.com/rss/home | ✅ 실제 |
| **Wall Street Journal** | https://feeds.a.dj.com/rss/RSSMarketsMain.xml | ✅ 실제 |

### 2️⃣ **Economic  기관 News (Economic)**
| 기관명 | RSS 피드 URL | Status |
|--------|-------------|------|
| **Federal Reserve** | https://www.federalreserve.gov/feeds/press_all.xml | ✅ 실제 |
| **Treasury** | https://home.treasury.gov/rss/press-releases | ✅ 실제 |
| **BLS News** | https://www.bls.gov/feed/news_release/rss.xml | ✅ 실제 |
| **Commerce Dept** | https://www.commerce.gov/rss.xml | ✅ 실제 |

### 3️⃣ **국제 기관 News (International)**
| 기관명 | RSS 피드 URL | Status |
|--------|-------------|------|
| **ECB Press** | https://www.ecb.europa.eu/rss/press.xml | ✅ 실제 |
| **Bank of Japan** | https://www.boj.or.jp/en/rss/whatsnew.xml | ✅ 실제 |
| **IMF News** | https://www.imf.org/en/News/RSS?language=eng | ✅ 실제 |

## 📱 소셜미디어 Data 출처

### ⚠️ **현재 Status: 시뮬레이션 Data**

```python
# 현재는 데모용 가상 Data Usage
social_data = {
    "platforms": {
        "twitter": {
            "mentions": 1250,  # 가상 Data
            "sentiment": {"positive": 45, "negative": 30, "neutral": 25},
            "trending_hashtags": ["#Fed", "#Inflation", "#StockMarket"]
        },
        "reddit": {
            "posts": 89,  # 가상 Data
            "comments": 1456,
            "top_subreddits": ["r/investing", "r/stocks", "r/economics"]
        }
    }
}
```

### 🔧 **실제 소셜미디어 API 연동 방법**

#### **Twitter API v2**
- **필요**: Twitter Developer Account
- **비용**: 기본 무료, 고급 Features 유료
- **Data**: 실시간 트윗, 해시태그, 감정 Analysis

#### **Reddit API**
- **필요**: Reddit App 등록
- **비용**: 무료 (Rate Limit 있음)
- **Data**: 서브레딧 포스트, 댓글, 투표

#### **기타 소셜미디어**
- **Discord API**: 커뮤니티 대화
- **Telegram API**: 채널 메시지
- **YouTube API**: 댓글 Analysis

## 🔍 감정 Analysis 기술

### **TextBlob Usage**
```python
from textblob import TextBlob

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 (부정) ~ 1 (긍정)
    subjectivity = blob.sentiment.subjectivity  # 0 (객관) ~ 1 (주관)
```

### **키워드 기반 주제 분류**
```python
keywords = {
    "monetary_policy": ["fed", "federal reserve", "interest rate"],
    "market_sentiment": ["bull", "bear", "rally", "crash"],
    "economic_indicators": ["gdp", "unemployment", "cpi"]
}
```

## 📊 Data 수집 Process

### **1단계: RSS 피드 수집**
```python
import feedparser

def fetch_rss_feed(url, max_items=10):
    feed = feedparser.parse(url)
    articles = []
    
    for entry in feed.entries[:max_items]:
        article = {
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "summary": entry.summary
        }
        articles.append(article)
    
    return articles
```

### **2단계: 감정 Analysis**
```python
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    
    if polarity > 0.1:
        label = "positive"
    elif polarity < -0.1:
        label = "negative"
    else:
        label = "neutral"
    
    return {"polarity": polarity, "label": label}
```

### **3단계: 주제 분류**
```python
def classify_topics(text):
    text_lower = text.lower()
    topics = []
    
    for topic, keywords in keyword_dict.items():
        if any(keyword in text_lower for keyword in keywords):
            topics.append(topic)
    
    return topics
```

## 🎯 현재 System의 장단점

### ✅ **장점**
- **실제 News Data**: 11개 주요 매체의 실시간 RSS 피드
- **다양한 소스**: 금융, Economic 기관, 국제기관 포함
- **자동 감정 Analysis**: TextBlob 기반 실시간 Analysis
- **주제 분류**: 키워드 기반 자동 카테고리화

### ⚠️ **한계점**
- **소셜미디어**: 현재 시뮬레이션 Data (실제 API 연동 필요)
- **감정 Analysis 정확도**: TextBlob은 기본 수준 (고급 NLP 모델 필요)
- **언어 제한**: 영어 중심 (한국어 News 소스 부족)

## 🚀 개선 방안

### **1단계: 소셜미디어 API 연동**
- Twitter API v2 연동
- Reddit API 연동
- 실시간 소셜미디어 감정 추적

### **2단계: 고급 감정 Analysis**
- BERT, RoBERTa 등 Transformer 모델 Usage
- 금융 특화 감정 Analysis 모델
- 다국어 Support

### **3단계: 한국 News 소스 Add**
- 연합News, 한국Economic , 매일Economic  RSS
- 네이버 News API
- 다음 News API
