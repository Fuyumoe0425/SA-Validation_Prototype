# Research Notebooks

This directory contains Jupyter notebooks for the complete research workflow.

## Workflow

Execute the notebooks in the following order:

### 1. 01_collect_papers.ipynb
**Purpose**: Collect papers from Semantic Scholar and arXiv

**What it does**:
- Queries multiple academic databases using keywords from config.yaml
- Collects ~200 papers per research area (6 areas total)
- Removes duplicates and filters by relevance
- Saves raw data to `data/raw/`

**Prerequisites**:
- API keys configured in `.env` (optional for basic usage)
- Internet connection

**Outputs**:
- `data/raw/papers_by_area.json` - All collected papers organized by research area
- `data/raw/papers_metadata.json` - Combined metadata

**Runtime**: ~10-15 minutes

---

### 2. 02_analyze_papers.ipynb
**Purpose**: Analyze papers using OpenAI LLM

**What it does**:
- Loads papers from `data/raw/`
- Sends paper abstracts to GPT-4 for analysis
- Extracts: key contributions, technical approaches, MiroFish integration points
- Ranks papers by relevance score
- Saves analyzed data to `data/processed/`

**Prerequisites**:
- OpenAI API key in `.env` (REQUIRED)
- Completed notebook 01

**Outputs**:
- `data/processed/analyzed_papers.json` - Full analysis results
- `data/processed/top_papers.json` - Filtered high-relevance papers
- `data/processed/mirofish_integrations.json` - Integration recommendations

**Runtime**: ~30-60 minutes (depending on number of papers)
**Cost**: ~$5-10 in OpenAI API usage

---

### 3. 03_visualize_architecture.ipynb
**Purpose**: Generate visualizations and reports

**What it does**:
- Creates citation network graphs
- Generates timeline charts
- Produces relevance distribution plots
- Creates interactive dashboards
- Exports to `docs/visualizations/`

**Prerequisites**:
- Completed notebooks 01 and 02

**Outputs**:
- `docs/visualizations/citation_network.png` - Static network graph
- `docs/visualizations/citation_network.html` - Interactive network
- `docs/visualizations/timeline.png` - Publication timeline
- `docs/visualizations/dashboard.html` - Summary dashboard
- `docs/reports/summary.md` - Text summary

**Runtime**: ~5-10 minutes

---

## Tips

- **Start small**: Test with a smaller number of papers first (edit config.yaml)
- **Use caching**: All modules cache API responses to save time and money
- **Check logs**: Set LOG_LEVEL=DEBUG in .env for detailed output
- **Save progress**: Each notebook saves intermediate results

## Troubleshooting

**API Rate Limits**:
- Semantic Scholar: 100 requests/5 minutes (no key), 5000/5 min (with key)
- OpenAI: Depends on your tier

**Out of Memory**:
- Process papers in batches (modify notebook code)
- Use lighter LLM models (gpt-3.5-turbo instead of gpt-4)

**Network Errors**:
- Notebooks auto-retry with exponential backoff
- Check internet connection
- Verify API keys