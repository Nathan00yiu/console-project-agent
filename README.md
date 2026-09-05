# Console Project Agent

A standalone console application built with LangChain and LangGraph to manage projects through natural language commands in your terminal.

---

## Features

* **Natural Language Processing:** Create, list, and delete projects using conversational prompts.
* **Smart Field Extraction:** Automatically extracts key project details (project name, customer) from user input.
* **Interactive Clarification:** Asks follow-up questions if required project fields are missing.
* **Local Storage:** Stores project records in a structured local JSON file (`projects.json`).
* **Flexible LLM Support:** Fully configurable to run with OpenAI, OpenRouter, or local Ollama instances.

---

## Prerequisites

* **Python:** `3.10` or higher
* **Package Manager:** `pip`

---

## Installation & Setup

1. **Clone the Repository**
```bash
git clone https://github.com/Nathan00yiu/console-project-agent.git
cd console-project-agent

```


2. **Create & Activate a Virtual Environment**
* **macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate

```


* **Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.bat

```




3. **Install Dependencies**
```bash
pip install -r requirements.txt

```


4. **Configure Environment Variables**
`.env` file in the root directory:

* **Local Ollama Setup**
```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1

```

* **Run Ollama and the pull required model**
```bash
ollama serve
ollama pull llama3

```






---

## Running the Application

Execute the main script to start the interactive terminal session:

```bash
python main.py

```

---

## Usage Examples

Once running, enter natural language prompts at the `>` prompt:

* **Create a Project:**
```text
> Create a project called Alpha for customer Acme

```


* **Handle Missing Fields:**
```text
> Create project Beta
# Response: Please provide the missing information: customer.
> Customer is Globex

```


* **List All Projects:**
```text
> List projects

```


* **Delete a Project:**
```text
> Delete project Alpha

```


* **Exit Application:**
```text
> exit

```

* **Create project with more information:**
```text

> Create a project called Alpha for customer Acme ,the start date is 31/10 and location is HongKong

```

---

## Project Structure

```text
.
├── main.py          # Interactive CLI entry point and event loop
├── agent.py         # LangGraph workflow and LLM intent classifier
├── schema.py        # Pydantic data models for intent and project schemas
├── database.py      # JSON file read/write logic for projects.json
├── requirements.txt # Python dependency list
├── .env             # Environment variable configuration
└── projects.json    # Persistent project storage (auto-generated)

```

## LangGraph workflow

The LangGraph workflow defined in agent.py takes raw natural language input, passes it to the LLM to classify intent, and dynamically routes the request to the correct database handler node.
