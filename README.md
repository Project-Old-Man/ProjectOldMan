

# 🧠 AI Response Recommender/Project Old Man(AI 놀이터)

A full-stack, AI-powered response recommender system that provides streaming suggestions based on user input, designed with scalable architecture and model optimization in mind.

---

## 🗺️ Project Overview

This project aims to build a web-based service that:

- Accepts user prompts
- Streams optimized AI-generated responses
- Collects feedback for future improvements
- Integrates local and cloud-based LLMs using **vLLM** and vector search (RAG/RAC)

---

## 📐 Architecture

```
Figma → React+TypeScript → Vercel (Frontend)
                ↓
            FastAPI (Backend)
                ↓
PostgreSQL + Weaviate (Data/VectorDB)
                ↓
         vLLM (LLaMA, Mistral)
```

---

## 🧩 System Components

### 1. Web Design (Figma)
- Designed full user flow and UI/UX layout
- Clear interaction path: `Prompt → Suggested Answer → Feedback`
- Key UX Features:
  - Adjustable font size
  - Legal disclaimer placement
  - Conversational flow mapping

### 2. Frontend (React + TypeScript)
- UI built using **Cursor AI** and **MCP**
- Responsive design deployed on **Vercel**
- Integrated with streaming API for real-time response display

### 3. AI Model Workflow
#### 3-1. Model Selection
- Initial testing using **GPT API** and **HuggingFace models**
- Built prompt-response pipelines

#### 3-2. Performance Review
- Latency, quality, and cost analysis
- Evaluated need for finetuning or local hosting

#### 3-3. Dataset Preparation
- Curated open datasets and user feedback
- Built embedding index for RAG/RAC using **Weaviate + PostgreSQL**

### 4. Backend (FastAPI + vLLM)
- FastAPI handles:
  - Prompt generation logic
  - VectorDB query (RAG/RAC)
  - API endpoints: `/query`, `/recommend`
- Hosted on **Oracle Cloud Free Tier**
- Multiple models hosted with port-specific access via **vLLM**

### 5. Database & Vector Search
- **Weaviate**: Embedding search and metadata management
- **PostgreSQL**: User history, feedback logs
- Full RAC flow: Prompt → Search → Context injection → Generation

### 6. Deployment & Optimization
- Converted models to **ONNX / GGUF**
- Automated build & deployment via:
  - **Docker**
  - **GitHub Actions**
  - **DockerHub**
- Hosting:
  - **Backend**: Oracle Cloud
  - **Frontend**: Vercel
  - (Planned) **vLLM GPU Serving**: AWS EC2

### 7. Monitoring & Continuous Improvement
- Logs stored in PostgreSQL
- Future integration:
  - **Prometheus + Grafana** for resource monitoring
  - Prompt refinement via user feedback
  - Auto-retraining pipeline using Colab → Finetune → Hot-swap new models

---

## 🔧 Tech Stack

| Layer        | Tools / Frameworks |
|--------------|-------------------|
| Frontend     | React, TypeScript, Vercel, MCP |
| Backend      | FastAPI, vLLM, Oracle Cloud |
| Database     | PostgreSQL, Weaviate |
| AI Models    | LLaMA, Mistral, ONNX/GGUF |
| DevOps       | Docker, GitHub Actions, DockerHub |
| Monitoring   | (Planned) Prometheus, Grafana |

---

## 🚧 Roadmap

- [x] Basic Figma → Frontend conversion  
- [x] FastAPI + AI model serving  
- [x] RAG/RAC integration with vector search  
- [ ] GPU-based serving on AWS EC2  
- [ ] Live feedback-driven prompt optimization  
- [ ] Monitoring + auto-retrain pipeline  

---

## 🧑‍💻 Contributors

- **Zeu** — AI pipeline, backend architecture, deployment  
- **Team Members** — [Add roles based on contribution]

---

## 📜 License

This project is for educational and portfolio purposes only.  
Model deployments and data usage must comply with their respective licenses.