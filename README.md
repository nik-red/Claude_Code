# 🤖 Claude Code Agentic Data Engineering Platform

A hands-on project built to explore the intersection of **Data Engineering**, **Agentic AI**, and **Workflow Automation** using Claude Code.

This repository demonstrates how AI-powered agents can orchestrate data pipelines, automate repetitive engineering tasks, review code, generate reports, and interact with external systems through MCP (Model Context Protocol).

The project combines Python, Apache Airflow, Claude Code Skills, Agents, Hooks, and MCP Servers to create an intelligent and extensible data engineering workflow.

---

## 🎯 Why I Built This Project

As a Data Engineer, I wanted to understand how Agentic AI can be applied to real-world data engineering problems.

Instead of learning concepts in isolation, I built a working project that demonstrates:

* AI-assisted workflow orchestration
* Agent-based task delegation
* Automated data ingestion and transformation
* Intelligent reporting and visualization
* MCP-based integrations
* Hook-driven governance and automation

The goal is to eventually evolve this into an enterprise-grade AI-powered Data Platform with integrations for Databricks, Azure Data Factory, Unity Catalog, and Azure Data Lake.

---

# 🏗️ Architecture

```text
User
 │
 ▼
Claude Code
 │
 ├── Orchestrator Agent
 │
 ├── Code Reviewer Agent
 │
 ├── Fetch API Skill
 │
 ├── Migration Skill
 │
 ├── Visualization Skill
 │
 └── Reporting Skill
 │
 ▼
Apache Airflow
 │
 ▼
CSV → Parquet → Analytics → Reports
```

---

# 🧠 Claude Code Components

## Skills

### 🔹 Fetch API Skill

Responsible for:

* Retrieving data from APIs
* Storing raw data as CSV
* Logging extraction activities
* Managing timestamp-based output folders

### 🔹 Migration Skill

Responsible for:

* Converting CSV files to Parquet
* Tracking migration metadata
* Generating audit logs
* Improving storage efficiency

### 🔹 Visualization Skill

Responsible for:

* Generating analytical charts
* Sales trend analysis
* Customer-level insights
* Product-level insights
* Returns analysis

### 🔹 Daily Report Skill

Responsible for:

* KPI calculations
* Report generation
* Email-ready summaries
* Automated report delivery

---

## Agents

### 🚀 Orchestrator Agent

Acts as the central coordinator.

Responsibilities:

* Planning execution flow
* Invoking relevant skills
* Managing dependencies
* Coordinating workflow execution

### 🔍 Code Reviewer Agent

Acts as an automated reviewer.

Responsibilities:

* Reviewing generated code
* Validating standards
* Providing recommendations
* Supporting quality assurance

---

## Hooks

Custom hooks are configured to automate actions before and after tool execution.

### PreToolUse

Executed before tool invocation.

Examples:

* Validation
* Security checks
* Governance rules
* Execution logging

### PostToolUse

Executed after tool invocation.

Examples:

* Audit logging
* Monitoring
* Notifications
* Operational tracking

---

## MCP Servers

This project explores the Model Context Protocol (MCP) ecosystem.

Configured MCP Servers:

### DuckDuckGo MCP

Used for:

* Web search
* Information retrieval

### Playwright MCP

Used for:

* Browser automation
* Website interaction
* UI testing

### Tavily MCP

Used for:

* AI-powered search
* Research workflows
* Knowledge retrieval

---

# 📊 Data Pipeline Flow

```text
Fetch Data
    │
    ▼
CSV Files
    │
    ▼
Parquet Conversion
    │
    ▼
Visualization
    │
    ▼
Reporting
    │
    ▼
Email Delivery
```

---

# ⚙️ Airflow Integration

This project includes Apache Airflow DAGs that demonstrate workflow orchestration.

Implemented patterns:

* Producer-Consumer DAGs
* Asset-Based Scheduling
* Data-Aware Triggers
* Automated Workflow Execution

Current DAGs:

* data_fetch.py
* data_report.py

---

# 📁 Project Structure

```text
.claude/
│
├── agents/
│   ├── orchestrator/
│   └── code_reviewer/
│
├── hooks/
│   ├── pre_script.py
│   └── post_script.py
│
├── skills/
│   ├── fetchAPI/
│   ├── migrate/
│   ├── visualize/
│   └── send-daily-report/
│
├── Airflow_Project/
│   └── dags/
│
├── CLAUDE.md
├── settings.json
└── .mcp.json
```

---

# 🛠️ Technologies Used

### Data Engineering

* Python
* Pandas
* PyArrow
* Apache Airflow
* CSV
* Parquet

### Agentic AI

* Claude Code
* Claude Skills
* Claude Agents
* MCP (Model Context Protocol)
* Hooks

### Automation

* Playwright MCP
* Tavily MCP
* DuckDuckGo MCP

### Development

* Git
* GitHub
* UV Package Manager

---

# 📚 Key Concepts Explored

Throughout this project I explored:

* Agentic AI Systems
* Multi-Agent Architecture
* Claude Code Skills
* Claude Code Hooks
* MCP Servers
* Workflow Orchestration
* Data Engineering Automation
* Data Pipeline Design
* AI-Assisted Development
* Code Review Automation

---

# 🚀 Future Roadmap

Planned enhancements include:

* Databricks Integration
* Azure Data Factory Integration
* Azure Data Lake Integration
* Unity Catalog Integration
* AI-Based Root Cause Analysis
* Data Quality Framework
* Automated Monitoring Platform
* Email & Teams Notifications
* Custom Databricks MCP Server
* AI-Powered Data Governance Assistant

---

# 🎓 Learning Outcomes

This project helped me gain practical experience in:

* Building AI-powered workflows
* Designing agent-based architectures
* Implementing MCP integrations
* Automating data engineering processes
* Creating reusable Claude Skills
* Understanding enterprise AI patterns

---

# 👨‍💻 Author

**Nikhil Reddyvari**

Data Engineer | Azure | Databricks | Agentic AI Enthusiast

Currently exploring how Agentic AI can transform modern Data Engineering and Data Architecture practices.

---
