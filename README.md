# Dynamic Resource Scheduling Research System
# 动态资源调度研究系统

A complete automated literature review and visualization system for dynamic resource scheduling research, with integration analysis for the MiroFish swarm intelligence engine.

一个完整的自动化文献综述和可视化系统，用于动态资源调度研究，并提供与 MiroFish 群体智能引擎的集成分析。

## 🎯 Project Overview

This system provides:

- ✅ **Automated Paper Collection** - Search and collect papers from Semantic Scholar, arXiv
- ✅ **LLM-Powered Analysis** - Extract technical insights and integration opportunities
- ✅ **Interactive Visualizations** - Citation networks, technology timelines, architecture diagrams
- ✅ **Knowledge Graph** - Obsidian-based knowledge management system
- ✅ **MiroFish Integration** - Identify implementation opportunities in MiroFish modules

## 🏗️ Research Areas

This system focuses on 6 core technical areas:

1. **Multi-Agent Coordination** (MARL, Swarm Intelligence, GNN)
2. **Dynamic Scheduling** (Online Learning, Constraint Programming, Meta-Learning)
3. **Uncertainty Handling** (Bayesian Optimization, Robust Optimization, Ensembles)
4. **Scene Adaptation** (Transfer Learning, Continual Learning, Online Adaptation)
5. **Knowledge Graph Reasoning** (Temporal KG, Graph Embedding, Causal Inference)
6. **LLM Enhancement** (RAG, Tool-Augmented LLM, Planning)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Jupyter Notebook
- OpenAI API Key (for LLM analysis)

### Installation

```bash
# Clone the repository
git clone https://github.com/Fuyumoe0425/SA-Validation_Prototype.git
cd SA-Validation_Prototype

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Run the Workflow

```bash
# Start Jupyter Notebook
jupyter notebook

# Execute notebooks in order:
# 1. notebooks/01_collect_papers.ipynb  - Collect papers
# 2. notebooks/02_analyze_papers.ipynb  - Analyze with LLM
# 3. notebooks/03_visualize_architecture.ipynb - Generate visualizations
```

## 📊 Workflow

```
┌─────────────────────┐
│ 01_collect_papers   │  Search 6 research areas
│  - Semantic Scholar │  ~200 papers per area
│  - arXiv API        │  Export to data/raw/
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 02_analyze_papers   │  LLM extracts:
│  - GPT-4o-mini      │  - Key algorithms
│  - Technical focus  │  - MiroFish integration points
└──────────┬──────────┘  - Implementation suggestions
           │
           ▼
┌─────────────────────┐
│ 03_visualize        │  Generate:
│  - Citation network │  - PNG/SVG charts
│  - Timeline         │  - Interactive HTML
│  - Architecture map │  - Obsidian notes
└─────────────────────┘
```

## 📁 Directory Structure

```
SA-Validation_Prototype/
├── README.md                    # This file
├── INTEGRATION_GUIDE.md         # MiroFish integration guide
├── research_architecture.md     # Technical framework overview
├── requirements.txt             # Python dependencies
├── config.yaml                  # Configuration file
├── .env.example                 # API key template
│
├── notebooks/                   # Jupyter notebooks
│   ├── 01_collect_papers.ipynb
│   ├── 02_analyze_papers.ipynb
│   └── 03_visualize_architecture.ipynb
│
├── utils/                       # Python utilities
│   ├── paper_collector.py       # Paper search APIs
│   ├── llm_analyzer.py          # LLM analysis tools
│   ├── mirofish_integrator.py   # Integration analyzer
│   ├── obsidian_generator.py    # Generate notes
│   └── visualization.py         # Chart generators
│
├── research/                    # Obsidian knowledge vault
│   ├── 0-Overview/
│   ├── 1-MARL/
│   ├── 2-Scheduling/
│   ├── 3-Uncertainty/
│   ├── 4-Scene-Adaptation/
│   ├── 5-Knowledge-Graph/
│   └── 6-LLM-Enhancement/
│
├── data/                        # Data storage
│   ├── raw/                     # Raw paper metadata
│   ├── processed/               # Cleaned data
│   └── vosviewer/               # VOSviewer exports
│
├── docs/                        # Documentation
│   ├── visualizations/          # Generated charts
│   ├── reports/                 # Auto-generated reviews
│   └── tutorials/               # Tutorials
│
└── templates/                   # Templates
    ├── paper_note_template.md
    └── integration_analysis.md
```

## 🔧 Configuration

Edit `config.yaml` to customize:

- Research areas and search keywords
- Paper collection limits per area
- LLM model and parameters
- Visualization settings

## 📚 Documentation

- **INTEGRATION_GUIDE.md** - How to integrate research findings into MiroFish
- **research_architecture.md** - Detailed technical framework
- **docs/tutorials/** - Step-by-step tutorials

## 🎨 Visualization Tools

This system integrates with external tools:

- **VOSviewer** - Professional citation network visualization
- **Obsidian** - Knowledge graph and note-taking
- **NetworkX** - Python network analysis and plotting

## 🔗 Related Projects

- [MiroFish](https://github.com/666ghj/MiroFish) - Swarm Intelligence Engine for prediction

## 📖 Research Areas Detail

See `research_architecture.md` for:
- Detailed technology breakdown
- Key papers and keywords
- MiroFish module mapping
- Integration priorities (Phase 1-3)

## 🤝 Contributing

This is a research system. Feel free to:
- Add new research areas
- Improve analysis prompts
- Enhance visualizations
- Contribute integration examples

## 📄 License

MIT License

## 🙋 Support

For questions about:
- **Paper collection** - Check `utils/paper_collector.py` docstrings
- **LLM analysis** - See `notebooks/02_analyze_papers.ipynb` examples
- **MiroFish integration** - Read `INTEGRATION_GUIDE.md`

## 🎯 Next Steps

After setup:

1. Run notebook 01 to collect ~1200 papers
2. Review and filter top papers in `data/processed/`
3. Run notebook 02 to analyze with LLM
4. Generate visualizations with notebook 03
5. Open `research/` folder in Obsidian
6. Read `INTEGRATION_GUIDE.md` for implementation ideas

---

**Happy Researching! 🚀**