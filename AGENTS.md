# AGENTS.md

## Project

Fundamental Agent — DeepSeek API + Strands Agent framework. English-language financial analysis and article auto-generation with Streamlit dashboard, Slack alerts, and data monitoring.

**Language**: All code, config, output, and docs are in English (migrated from Korean, May 2026). Project renamed from "Economic News System" to "Fundamental Agent" (May 2026).

## Architecture

- **LLM provider** (`agents/deepseek_provider.py`): `DeepSeekProvider` wrapper — OpenAI SDK with `base_url="https://api.deepseek.com"`, model `deepseek-v4-flash`. Used by both Strands and legacy agents.
- **Primary agent framework** (`agents/`): Strands system — `BaseStrandAgent`, `StrandOrchestrator`, 5 strands (`DataAnalysisStrand`, `ArticleWriterStrand`, `ReviewStrand`, `ImageGeneratorStrand`, `AdRecommendationStrand`). Sequential workflow: data_analyst → article_writer → reviewer → image_generator → ad_recommender.
- **Legacy agent system** (`agents_backup/`): Old `BaseAgent`/`OrchestratorAgent` classes. Imported by `main.py` and `streamlit_app/app.py` from `agents_backup/`, not `agents/`.
- **Data monitoring** (`data_monitoring/`): yfinance-driven collectors, technical analysis, event detection, sentiment analysis, Reddit/Twitter collectors.
- **Notifications** (`notifications/slack_notifier.py`): Slack webhook alerts with priority levels.
- **Streamlit dashboard** (`streamlit_app/app.py`): Starts with `streamlit run streamlit_app/app.py` or `python run_streamlit.py` (port 8501, 0.0.0.0).

## Entrypoints

| Command | Mode |
|---|---|
| `python main.py --mode full` | Full pipeline |
| `python main.py --mode data` | Data collection only |
| `python main.py --mode article --article-type market_summary --length medium` | Article only |
| `python main.py --mode schedule` | Scheduled automation |
| `python main.py --mode status` | System status |
| `python demo_slack_alerts.py` | Test Slack alerts |
| `streamlit run streamlit_app/app.py` | Dashboard |
| `docker-compose up` | Docker deployment |

## Key Config

- `config/default.json` — main config (model ID: `deepseek-v4-flash`, symbols, intervals)
- `config/settings.py` — loads config, expects `DEEPSEEK_API_KEY` env var.
- `.env` — set `DEEPSEEK_API_KEY=sk-...` and `SLACK_WEBHOOK_URL=...`. See `.env.example`.

## Environment Variables (Required)

| Variable | Purpose |
|---|---|
| `DEEPSEEK_API_KEY` | DeepSeek API key (sk-...) |
| `SLACK_WEBHOOK_URL` | Slack webhook for notifications |

## Testing

No test framework. Tests are ad-hoc scripts (`test_*.py`). CI (`.github/workflows/test.yml`) only runs import checks and standalone modules.

## Railway Deployment

- `Procfile` at project root: `web: python main.py --mode full`
- `Dockerfile` + `docker-compose.yml` both use `DEEPSEEK_API_KEY` env var (no AWS variables)
- Requirements in `requirements.txt` (no boto3/botocore/langchain-aws)

## Output Directories

- `output/automated_articles/` — JSON + HTML articles
- `output/charts/`, `output/images/` — generated media
- `streamlit_articles/` — auto-generated Streamlit pages
- `logs/` — log files

## Known Issues

- **Import paths**: `main.py` and `streamlit_app/app.py` import from `agents_backup.*`, not `agents.*`. This is intentional — the legacy agent system (`agents_backup/`) is used by entry points.
- **Matplotlib font setup**: `data_analysis_strand.py` has platform-specific font setup but Korean font requirements removed.
- **Hardcoded paths**: Several shell scripts and `data_monitoring/monitor.py` still reference `/home/ec2-user/projects/ABP/fundamental_agent/` (EC2 deployment paths).
- **Image generation**: All LLM-based image generation removed (Titan, Stability AI). Falls back to placeholder images.

## Dependencies

`requirements.txt` — yfinance, pandas, openai, streamlit, plotly, matplotlib, Pillow, wordcloud, scipy, scikit-learn, etc. No AWS SDK.

## Project Rename History

The project was originally cloned from `jihwanwoo/Economic-News-System` (Korean-language economic news system using AWS Bedrock). It was:
1. Migrated from AWS Bedrock to DeepSeek API (April 2026)
2. Translated from Korean to English (May 2026)
3. Renamed from "Economic News System" to "Fundamental Agent" (May 2026)

Some legacy files (`streamlit_articles/`, `.md` docs, shell scripts) still contain old references. The core Python source, config, and deployment files have been fully updated.
