# Creation of AI Driven Multi-Agent Real Estate Negotiation Simulation and Platform

## Project Overview

The **AI Driven Multi-Agent Negotiation Simulation and Platform** is an AI-based real-estate negotiation platform designed for both **AI-vs-AI simulation** and **human negotiation practice**.

The platform uses AI agents with different personalities to simulate realistic buyer-seller negotiations. The **Orchestrator Agent** manages the negotiation turns, while the AI agents generate offers, counteroffers, and decisions based on their objectives and personalities.

The platform supports multiple real-estate scenarios and provides negotiation outcomes, transcripts, round information, and reports.

## Features

* AI-vs-AI negotiation simulation
* Human negotiation practice
* Buyer and Seller AI agents
* Multiple negotiation personalities
* Orchestrator Agent for turn management
* Offers and counteroffers
* Accept, Counter, and Reject decisions
* Deadlock detection
* Round tracking
* Negotiation transcript
* Negotiation outcome and summary
* Multiple real-estate scenarios
* Property dataset integration

## Real-Estate Scenarios

The platform supports:

* Land / Plot
* Apartment / Flat
* Villa / Independent House

## Agent Personalities

The AI agents can use different negotiation personalities:

* Aggressive
* Collaborative
* Risk-Averse

## Negotiation Modes

### AI-vs-AI Simulation

In this mode, the buyer and seller are both controlled by AI agents.

```text
Select Scenario
      ↓
Select Buyer Personality
      ↓
Select Seller Personality
      ↓
Start Negotiation
      ↓
Orchestrator manages turns
      ↓
Buyer and Seller exchange offers
      ↓
Agreement / Rejection
      ↓
Negotiation Report
```

### Human Practice

In Human Practice mode, the user can participate in the negotiation and practice negotiating with an AI agent.

The AI responds according to its assigned personality and negotiation objectives.

This mode helps users understand and practice:

* Making offers
* Making counteroffers
* Negotiation strategies
* Accepting or rejecting offers
* Reaching an agreement

## Main Components

### Orchestrator Agent

Controls the negotiation flow and manages turns between the buyer and seller.

### Reasoning Engine

Uses the AI/LLM service to generate negotiation responses based on personality, objectives, and conversation history.

### Counteroffer Evaluator

Evaluates offers and determines whether the agent should accept, reject, or make a counteroffer.

### Deadlock Detector

Detects situations where the negotiation is not progressing toward an agreement.

### Report Generator

Generates the negotiation transcript, summary, and outcome information.

## Technologies Used

* Python
* FastAPI
* Uvicorn
* React
* Pandas
* AI / LLM API
* HTML
* CSS
* JavaScript
* Git and GitHub

# How to Run

## Prerequisites

Install the following:

* Python 3.x
* Node.js
* npm
* Git

Make sure Python and Node.js are available in Command Prompt.

## 1. Clone the Repository

Open Command Prompt:

```cmd
git clone https://github.com/AkshayaSurala/Multi-agent-negotiation-simulator.git
cd Multi-agent-negotiation-simulator
```

## 2. Configure the API Key

Create a `.env` file in the project root and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Do not upload your actual API key or `.env` file to GitHub.

Add this to `.gitignore`:

```text
.env
```

## 3. Start the Backend

Open **Command Prompt 1**:

```cmd
cd Desktop\Multi-agent-negotiation-simulator
py -m pip install -r requirements.txt
set PYTHONPATH=%CD%;%CD%\backend
cd backend
py -m uvicorn main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Keep this terminal running.

## 4. Start the Frontend

Open **Command Prompt 2**:

```cmd
cd Desktop\Multi-agent-negotiation-simulator\frontend
npm install
npm run dev
```

The terminal will display the frontend URL.

Open that URL in your browser.

## 5. Use the Platform

After both backend and frontend are running:

1. Open the frontend URL.
2. Select the required negotiation mode.
3. Select a real-estate scenario.
4. Select the required personalities or practice role.
5. Start the negotiation.
6. View the negotiation rounds, transcript, and outcome.

## Dataset

The project uses the `dataset_real.csv` file for real-estate property information.

The dataset includes information such as:

* Property Name
* Property Title
* Price
* Location
* Total Area
* Price per Square Foot
* Description
* Bathrooms
* Balcony

Keep `dataset_real.csv` in the project root.

## Testing

Backend tests are available in the `backend` folder.

Run AI-vs-AI negotiation tests:

```cmd
cd backend
py test_ai_vs_ai_rounds.py
```

Run report tests:

```cmd
py test_milestone4_reports.py
```

## Project Purpose

The platform demonstrates the use of AI agents for real-estate negotiation and provides an environment for both **simulation and practical negotiation training**.

It demonstrates:

* Multi-agent interaction
* AI-based reasoning
* Agent orchestration
* Negotiation strategies
* Counteroffer handling
* Deadlock detection
* Human negotiation practice
* Negotiation outcome analysis
