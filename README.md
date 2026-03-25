# AgentAdvisors

A financial multi-agent AI system that ingests real-time market data and news, orchestrates specialized AI agents to analyze signals and generate investment recommendations, and delivers a personalized daily digest through a centralized dashboard.

Currently, AgentAdvisors uses 6 AI agents, each responsible for a distinct role in the analysis pipeline.
* Market Agent pulls real-time price data and computes technical indicators to detect trends and momentum signals 
* News Agent scrapes financial news and social media, embeds articles into Pinecone for semantic search, and produces per-ticker sentiment scores that are tracked over time
* Expert Agent pulls institutional analyst recommendations to extract key insights from earnings reports and risk disclosures
* Opportunity Agent combines signals from the first three agents alongside fundamental data to score and rank stocks as potential investment opportunities
* Strategy Agent synthesizes all available signals using GPT-4o with chain-of-thought reasoning to produce explicit Buy, Hold, or Sell decisions with cited justifications
* Summary Agent compiles everything into a personalized daily digest filtered by the user's preferred sectors and risk tolerance

## Technologies

The main technologies this app uses are
* `Next.js`
* `FastAPI`
* `PostgreSQL`
* `Pinecone`
* `LangGraph`

## Ingestion targets

Ingestion now supports user-driven relevance:
* A new `user_research_interests` table stores active per-user research targets
  (ticker, industry, sector, and keyword).
* The ingestion pipeline resolves targets from active user interests and merges
  them with `INGEST_TICKERS` defaults.
* NewsAPI queries use the merged topics; yfinance and Finnhub use merged ticker
  targets.
* Toggle behavior with `INGEST_ENABLE_USER_SCOPED_TARGETS` (`true` by default).
