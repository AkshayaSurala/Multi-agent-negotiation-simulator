# Creation of AI Driven Multi-Agent Negotiation Simulation and Platform

## Project Overview

The **Creation of AI Driven Multi-Agent Negotiation Simulation and Platform** is an AI-based real-estate negotiation system that simulates negotiations between buyer and seller agents.

The platform uses multiple AI agents with different personalities. The **Orchestrator Agent** manages the negotiation turns, while the agents generate offers, counteroffers, and decisions based on their objectives and personalities.

The system supports different real-estate scenarios and provides negotiation outcomes, round information, transcripts, and reports.

## Features

* AI-vs-AI negotiation
* Buyer and seller AI agents
* Multiple agent personalities
* Orchestrator Agent for turn management
* Offer and counteroffer generation
* Accept, Counter, and Reject decisions
* Deadlock detection
* Round and negotiation tracking
* Negotiation transcript
* Outcome and summary report
* Multiple real-estate scenarios
* Property dataset integration

## Real-Estate Scenarios

The platform supports:

* Land / Plot
* Apartment / Flat
* Villa / Independent House

## Agent Personalities

The platform supports different negotiation personalities, including:

* Aggressive
* Collaborative
* Risk-Averse

## Project Structure

```text
Creation of AI Driven Multi-Agent Negotiation Simulation and Platform
│
├── frontend/
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator_agent.py
│   │   ├── deadlock_detector.py
│   │   ├── counteroffer_evaluator.py
│   │   ├── practice_agent.py
│   │   ├── practice_store.py
│   │   └── reasoning_engine.py
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   └── negotiation_router.py
│   │
│   ├── main.py
│   ├── dataset_manager.py
│   ├── negotiation_runner.py
│   ├── models.py
│   ├── personalities.py
│   ├── property_utils.py
│   ├── report_generator.py
│   └── ...
│
├── dataset_real.csv
├── requirements.txt
└── README.md
```

## Technologies Used

* Python
* FastAPI
* Uvicorn
* React
* Pandas
* AI / LLM API
* HTML, CSS and JavaScript
* Git and GitHub

# How to Run the Project

## Prerequisites

Install the following software:

* Python 3.x
* Node.js
* npm
* Git

Make sure Python and Node.js are added to PATH.

---

## 1. Clone the Repository

Open **Command Prompt** and run:

```cmd
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Go into the project folder:

```cmd
cd <PROJECT_FOLDER>
```

---

# 2. Backend Setup

Open Command Prompt.

Go to the project folder:

```cmd
cd "<PROJECT_FOLDER>"
```

Install the Python dependencies:

```cmd
py -m pip install -r requirements.txt
```

Set the Python path:

```cmd
set PYTHONPATH=%CD%;%CD%\backend
```

Go to the backend folder:

```cmd
cd backend
```

Start the FastAPI server:

```cmd
py -m uvicorn main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

FastAPI API documentation can be opened at:

```text
http://127.0.0.1:8000/docs
```

**Keep this Command Prompt window running.**

---

# 3. Frontend Setup

Open a **new Command Prompt window**.

Go to the project folder:

```cmd
cd "<PROJECT_FOLDER>"
```

Go to the frontend folder:

```cmd
cd frontend
```

Install the frontend dependencies:

```cmd
npm install
```

Start the frontend:

```cmd
npm run dev
```

The terminal will display the frontend URL.

Open that URL in a web browser.

---

# 4. Running the Complete Project

You need **two Command Prompt windows**.

### CMD Window 1 — Backend

```cmd
cd "<PROJECT_FOLDER>"
set PYTHONPATH=%CD%;%CD%\backend
cd backend
py -m uvicorn main:app --reload
```

### CMD Window 2 — Frontend

```cmd
cd "<PROJECT_FOLDER>\frontend"
npm install
npm run dev
```

After both servers are running, open the frontend URL shown by the frontend terminal.

---

# 5. Dataset

The project uses the following dataset:

```text
dataset_real.csv
```

The dataset contains real-estate property information such as:

* Property Name
* Property Title
* Price
* Location
* Total Area
* Price per Square Foot
* Description
* Bathrooms
* Balcony

Keep the dataset in the project root:

```text
project/
├── backend/
├── frontend/
├── dataset_real.csv
└── README.md
```

---

# 6. Negotiation Flow

The basic negotiation flow is:

```text
Select Property Scenario
        ↓
Select Buyer Personality
        ↓
Select Seller Personality
        ↓
Start AI-vs-AI Negotiation
        ↓
Orchestrator manages turns
        ↓
Buyer makes an offer
        ↓
Seller accepts / counters / rejects
        ↓
Buyer responds
        ↓
Negotiation continues
        ↓
Agreement or Rejection
        ↓
Outcome and Report
```

## 7. Main Components

### Orchestrator Agent

The Orchestrator Agent controls the negotiation flow and manages the turns between the buyer and seller agents.

### Reasoning Engine

The reasoning engine uses the configured AI/LLM service to generate negotiation responses based on the agent's personality, objectives, and conversation history.

### Counteroffer Evaluator

Evaluates offers and determines whether an agent should accept, reject, or make a counteroffer.

### Deadlock Detector

Detects situations where the negotiation is not progressing toward an agreement.

### Report Generator

Generates the negotiation transcript, summary, and outcome information.

## 8. Testing

Backend testing files are available in the `backend` folder.

To run the AI-vs-AI negotiation tests:

```cmd
cd backend
py test_ai_vs_ai_rounds.py
```

To run the Milestone 4 report tests:

```cmd
cd backend
py test_milestone4_reports.py
```

## 9. API Key Configuration

The project requires the configured AI/LLM API key for AI-based negotiation.

Create a `.env` file if required by the project configuration and add the required API key.

Example:

```text
GEMINI_API_KEY=your_api_key_here
```

**Do not upload your actual API key or `.env` file to GitHub.**

Add `.env` to `.gitignore`:

```text
.env
```

## 10. GitHub Development

The project uses Git branches for development.

Example:

```cmd
git status
git add .
git commit -m "Update project"
git push origin <branch-name>
```

Changes can then be merged into the `main` branch using a Pull Request.

## Project Purpose

The purpose of this project is to provide a simulation and training platform for understanding how multiple AI agents can interact and negotiate in a real-estate scenario.

The system demonstrates:

* Multi-agent interaction
* AI-based reasoning
* Negotiation strategies
* Agent orchestration
* Counteroffer handling
* Deadlock detection
* Negotiation outcome analysis
