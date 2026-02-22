# 🤖 Autonomous SRE Agent Prototype

An AI-driven agent designed to ingest real-time infrastructure alerts via **Kafka**, diagnose issues using **Llama 3.3**, and persist remediation logs in **Cassandra**.

## 🚀 The Tech Stack
- **Messaging:** Apache Kafka (Managed via NetApp Instaclustr)
- **Database:** Apache Cassandra (Managed via NetApp Instaclustr)
- **Brain:** Llama 3.3 via Groq (High-speed inference)
- **Orchestration:** LangChain 0.3
- **Development Paradigm:** Vibecoding

## 🛠️ How it Works
1. **Ingest:** `producer.py` simulates system failures (OOM, High CPU) and sends them to Kafka.
2. **Reason:** `agent.py` consumes the alert and asks the LLM if it needs more context.
3. **Execute:** The agent calls local diagnostic tools (Uptime, Incident History).
4. **Remediate:** The LLM synthesizes a final CLI fix based on the context.
5. **Log:** The suggestion is saved to Cassandra for audit.

## 📦 Setup
1. Clone the repo.
2. Create a `.env` file with your `GROQ_API_KEY`, `KAFKA_` and `CASSANDRA_` credentials.
3. Run `pip install -r requirements.txt`.
4. Run `python agent.py`.