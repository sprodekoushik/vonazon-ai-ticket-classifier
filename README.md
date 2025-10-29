# 🎯 Vonazon – AI Ticket Classifier (DeepSeek + Streamlit)

An end-to-end **AI workflow demo** built for the **Vonazon AI Product Engineer Interview**.  
This project showcases how to design, implement, and explain a small but complete AI-powered system — from **data ingestion → model classification → simulated CRM integration**, all wrapped in a clean, interactive Streamlit UI.

---

## 🚀 Overview

**Objective:**  
Automatically classify incoming customer support tickets (plain text) into fixed categories such as  
> `Billing`, `Technical Issue`, `Sales Inquiry`, `Refunds`, `Other`

The app uses:
- 💬 **DeepSeek API** (OpenAI-style endpoint) for real AI classification  
- ⚙️ **Rule-based fallback** when no API key is set (for offline demos)
- 📊 **Streamlit UI** for live interaction
- 💾 **Mock CRM integration** (JSONL log) to simulate downstream push

---

## 🧩 Features at a Glance

| Feature | Description |
|----------|--------------|
| 🧠 **AI Classification** | Uses DeepSeek LLM to categorize tickets with confidence + short explanation |
| ⚙️ **Offline Fallback** | Deterministic keyword-based classifier when no API key is found |
| 🎛️ **Streamlit Interface** | Paste tickets, view live results, and push to CRM — all in one page |
| 🔄 **Spinning Loader** | Smooth UX feedback during classification or CRM push |
| 💾 **CRM Simulation** | Appends results as structured JSON lines (`data/push_log.jsonl`) |
| 🧪 **Tests Included** | Unit tests for both fallback and mocked AI branch using Pytest |
| 🔐 **Environment Isolation** | `.env` management via `python-dotenv` — safe for interviews |
| 🧱 **Scalable Structure** | Modular core → services → UI separation (production-ready pattern) |

---

## 🏗️ Folder Structure

vonazon_interview_app/
├─ app.py # Streamlit UI
├─ requirements.txt
├─ .env.example # Template for DeepSeek credentials
├─ core/
│ ├─ schemas.py # Pydantic models (Ticket, Request, Result)
│ └─ constants.py # Default categories
├─ services/
│ ├─ deepseek_client.py # OpenAI-compatible DeepSeek adapter
│ ├─ classifier.py # Hybrid: DeepSeek or fallback logic
│ └─ crm.py # Mock CRM push (JSONL log)
├─ data/
│ └─ push_log.jsonl # Output CRM log
├─ tests/
│ └─ test_classifier.py # Unit tests for fallback + mocked AI
└─ README.md # This file

yaml
Copy code

---

## 🛠️ Setup & Installation

### 1️⃣ Clone or create the folder
```bash
git clone <your-repo-url> vonazon_interview_app
cd vonazon_interview_app
2️⃣ Create a virtual environment
Windows (PowerShell):

bash
Copy code
python -m venv .venv
.venv\Scripts\Activate.ps1
macOS/Linux:

bash
Copy code
python3 -m venv .venv
source .venv/bin/activate
3️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Configure your environment
Copy the template and add your API key:

bash
Copy code
cp .env.example .env
Open .env and fill in:

ini
Copy code
DEEPSEEK_API_KEY="sk-xxxx"
DEEPSEEK_API_BASE="https://api.deepseek.com"
DEEPSEEK_MODEL="deepseek-chat"
💡 For offline demos, leave DEEPSEEK_API_KEY empty — it will automatically switch to rule-based mode.

▶️ Running the App
Start the Streamlit interface:

bash
Copy code
streamlit run app.py
In your browser (default http://localhost:8501):

Paste one or more support tickets (one per line)

Click “Classify” → spinner appears while processing

See category, confidence, and explanation

Click “Push to CRM” → results appended to data/push_log.jsonl

(Optional) Download CRM log directly from UI

🧠 Example Run
Input tickets:

pgsql
Copy code
My invoice shows an extra charge that I didn’t authorize.
I can’t log in to my account — the system says my password is invalid.
I’d like to learn more about your premium service plans.
When will my refund be processed?
Output:

Ticket	Category	Confidence	Explanation
My invoice shows an extra charge...	Billing	0.91	Invoice-related issue
I can’t log in...	Technical Issue	0.86	Password problem
I’d like to learn more...	Sales Inquiry	0.77	Product interest
When will my refund...	Refunds	0.83	Refund query

🧪 Testing
Run all tests:

bash
Copy code
pytest -q
Included tests:

✅ Fallback keyword logic

✅ Mocked DeepSeek API branch

✅ Confidence + category validation

🧰 Technology Stack
Layer	Tools / Libraries
Frontend	Streamlit
Backend	Python 3.10+, DeepSeek API
Data Models	Pydantic
Testing	Pytest
Env Mgmt	python-dotenv
Storage	Local JSONL (mock CRM log)

🧩 Design Philosophy
🧠 Clear Modularity
Each layer is isolated:

/core: Pure data models and constants

/services: Integration logic (DeepSeek, CRM)

/app.py: Streamlit orchestration layer

⚙️ Robustness
Auto fallback if API key missing or API fails

Safe JSON extraction from model output

Exceptions handled gracefully for live demos

🧮 Scalability
Swap DeepSeek → OpenAI → Anthropic → HuggingFace with one file change (services/deepseek_client.py).

🔍 Observability
Logs every CRM push (timestamp, category, confidence)

Debug prints show whether DeepSeek or fallback is active

🔐 Security
.env kept local

.gitignore excludes .env and .venv

💬 Talking Points for Interview
Architecture: “I separated concerns into core, services, and UI, keeping logic testable and modular.”

Resilience: “If DeepSeek fails or no key, rule-based fallback ensures graceful degradation.”

Scalability: “Replacing DeepSeek with any API is a one-file swap — same schema.”

Testing: “I mocked the API to validate logic without real calls.”

User Experience: “Added spinners and dynamic messages for smooth interaction.”

Ethics / Interpretability: “Model explanations are surfaced but can be omitted in production pipelines.”

📈 Stretch Ideas (Future Enhancements)
Add FastAPI endpoints for /classify and /push

Include confidence thresholding → “Unclear” category

Replace JSONL with SQLite or MongoDB CRM storage

Add streaming UI for real-time token display

Deploy via Docker + Cloud Run or Streamlit Cloud

🧾 License
MIT License — free for personal and educational use.

✨ Credits
Built with ❤️ by Koushik Biswas for the Vonazon AI Product Engineer Live Coding Exercise (2025).
Powered by DeepSeek, Streamlit, and Python.


