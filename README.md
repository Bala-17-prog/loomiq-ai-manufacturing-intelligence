# LoomIQ — AI-Powered Textile Manufacturing Intelligence

![LoomIQ](https://img.shields.io/badge/Status-Prototype-blue) ![Python](https://img.shields.io/badge/Python-3.9+-yellow) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)

LoomIQ is a full-stack proof-of-concept application demonstrating how modern textile manufacturing organizations can leverage AI, Machine Learning, Computer Vision, and Data Analytics to monitor operations and assist in data-driven decision-making.

> **Disclaimer:** This project is specifically designed as a technical demonstration for a Software Engineering & AI internship interview. It uses **100% synthetic demonstration data**. It does not represent actual company data, machines, production figures, or employees.

## Features

- **Dashboard**: Real-time KPI aggregation directly from a SQLite database with dynamic Chart.js visualizations.
- **Production Intelligence**: Deep dive into production yields by machine, shift, and fabric type.
- **Explainable Machine Health ML**: Uses Scikit-Learn's `IsolationForest` to analyze telemetry (vibration, temperature, RPM) and generates a transparent Risk Score (LOW/MEDIUM/HIGH) with human-readable explanations.
- **Computer Vision Quality Inspection**: OpenCV-based visual anomaly detection pipeline that highlights fabric defects (stains, broken yarns) with bounding boxes and confidence scores.
- **AI Copilot**: A deterministic NLP interface that parses manufacturing intents and answers questions strictly backed by live database metrics (Zero Hallucination).
- **What-If Simulator**: Interactive tool to simulate the revenue and production impact of tweaking machine speeds, downtime, and defect rates.

## Architecture

```text
Frontend (HTML/CSS/JS) <--> REST API (FastAPI) <--> Service Layer <--> Repository Layer <--> SQLite / Models
```

## Getting Started

### Prerequisites
- Python 3.9+
- Windows environment (for `start_demo.bat`)

### Installation

1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Initialize the database and generate 365 days of synthetic data:
```bash
python scripts/initialize_database.py
python scripts/generate_demo_data.py
python scripts/validate_data.py
```

### Running the Application

Simply run the provided batch script:
```bash
start_demo.bat
```
This will start the FastAPI backend on `http://localhost:8000` and automatically open `frontend/index.html` in your default browser.
