# 🤖 Fundamental Agent

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-API-4A154B.svg)](https://deepseek.com/)
[![Slack](https://img.shields.io/badge/Slack-Integration-4A154B.svg)](https://slack.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Intelligent economic article auto-generation and real-time alert system.

## 🚀 Key Features

### 📊 **Advanced Event Detection**
- **Technical Analysis**: RSI, MACD, Bollinger Bands and 13 other indicators
- **Sentiment Analysis**: News feed-based market sentiment analysis
- **Correlation Analysis**: Inter-market correlation deviation detection
- **Sector Rotation**: Capital flow pattern analysis

### 🤖 **AI-based News Generation**
- **DeepSeek API**: High-quality economic article auto-generation
- **Multi-Agent System**: Specialized agent collaboration
- **Content Optimization**: Readability, SEO, reader engagement optimization

### 📱 **Real-time Slack Alerts**
- **Instant Alerts**: Real-time urgent market event delivery
- **Market Summary**: Regular comprehensive analysis reports
- **Smart Filtering**: Minimize alert fatigue
- **Mobile Support**: Mobile notifications via Slack app

### 📈 **Streamlit Dashboard**
- **Interactive Charts**: Real-time market data visualization
- **AI-generated Articles**: Web-based article viewer
- **Auto Images**: Article illustrations and word clouds

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                      │
│              (Web Interface & Visualization)                │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│               Strands Agent Orchestrator                     │
│              (Pipeline Orchestration)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌────▼─────┐ ┌────▼──────────┐
│ Data         │ │ Article  │ │ Review        │
│ Analysis     │ │ Writer   │ │ Strand        │
│ Strand       │ │ Strand   │ │               │
└──────────────┘ └──────────┘ └───────────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
        ┌─────────────▼─────────────┐
        │      Slack Notifier       │
        │    (Real-time Alerts)      │
        └───────────────────────────┘
```

## 📋 Requirements

### System Requirements
- Python 3.8+
- DeepSeek API key
- Slack workspace (for notifications)
- Internet connection (for data collection)

## 🛠️ Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/jihwanwoo/fundamental-agent.git
cd fundamental-agent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
```bash
# DeepSeek API key
export DEEPSEEK_API_KEY=sk-your_api_key_here

# Slack webhook URL
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/xxxxx/xxxxx/xxxxx"
```

### 4. System Test
```bash
# Full system test
python test_system.py

# Slack alert test
python demo_slack_alerts.py
```

## 🎯 Usage

### 📱 **Slack Alert System (Recommended)**

#### Instant Test
```bash
python demo_slack_alerts.py
```

#### Continuous Monitoring
```bash
# Background execution
./start_background_monitoring.sh

# Check status
./check_monitoring_status.sh

# Stop
./stop_monitoring.sh
```

### 📊 **Streamlit Dashboard**
```bash
# Run dashboard
streamlit run streamlit_app/app.py
```

### 🖥️ **Command Line Interface**
```bash
# Full pipeline
python main.py --mode full

# Specific article type
python main.py --mode article --article-type market_summary --length medium

# Data collection only
python main.py --mode data

# Scheduled automation
python main.py --mode schedule
```

## 📊 Alert Types

### 🚨 **Critical Alerts** (severity 0.6+)
- 📈 Stock surge/drop (5%+)
- ⚡ High volatility (15%+)
- 📊 Volume spike (3x average)
- 🚀 Technical breakout (Bollinger Bands, RSI)
- 💭 Market sentiment shift
- 🔄 Momentum divergence

### 📋 **Market Summary** (hourly)
- Overall risk assessment
- Detected events summary
- Key insights
- Investment implications

### 📰 **News Updates**
- AI-generated article completion alert
- Key points summary

## 📁 Output Files

Generated content is saved in the `output/` directory:

```
output/
├── automated_articles/          # JSON + HTML articles
├── charts/                      # Generated charts
└── images/                      # Generated images
```

## 🔧 Troubleshooting

### Common Issues

**DeepSeek API Key Error**
```bash
# Check environment variable
echo $DEEPSEEK_API_KEY

# Ensure key starts with sk-
```

**Slack Webhook Error**
```bash
curl -X POST -H 'Content-type: application/json' \
--data '{"text":"Test message"}' \
$SLACK_WEBHOOK_URL
```

**Too Many Alerts**
```json
// Adjust in config
"min_alert_severity": 0.8,
"max_alerts_per_hour": 8
```

## 🔒 Security Considerations

- Manage API keys securely
- Use environment variables for secrets
- Add sensitive files to `.gitignore`
- Review and approve generated content

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is distributed under the MIT License. See [LICENSE](LICENSE) file for details.

## 📞 Support

If you encounter issues or have questions:
- Report issues on GitHub Issues
- Check log files (`logs/` directory)
- Verify config files and environment variables

---

**Disclaimer**:
- This system does not provide investment advice
- Generated content is for informational purposes only
- Consult a professional for important investment decisions
