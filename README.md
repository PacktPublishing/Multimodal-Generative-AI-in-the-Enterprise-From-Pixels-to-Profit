# Multimodal Generative AI in the Enterprise: From Pixels to Profit

Welcome to the official repository accompanying the book **"Multimodal Generative AI in the Enterprise: From Pixels to Profit"** (published by Packt). 

This repository contains all the code samples, Jupyter Notebooks, and assets required to take you step-by-step from a strategic business idea to a fully automated, enterprise-grade multimodal generation pipeline.

---

## 📖 About the Book

We are living through a profound paradigm shift: **from analysis to creation**. Generative AI allows enterprises to not just categorize data, but to generate entirely new media assets—spanning text, images, audio, and video. 

By intersecting these generative capabilities with **multimodal understanding**, businesses can automate complex creative workflows. This book serves as your practical, code-first guide to deploying these transformative technologies responsibly.

---

## 🗂 Repository Structure

The code is organized sequentially by chapters:

| Chapter / Directory | Topic | Core Contents |
| :--- | :--- | :--- |
| 🚀 **Getting Started** | **Environment Setup** | Environment verification (`00_environment_check.ipynb`) |
| 📝 [04-text-generation](04-text-generation) | **Text Generation** | Crafting the strategic marketing foundation |
| 🎨 [05-image-generation](05-image-generation) | **Image Generation** | Visualizing the campaign narrative and generating product photography |
| 🎙 [06-audio-generation](06-audio-generation) | **Audio Generation** | Synthesizing voices and giving the campaign a voice |
| 🎬 [07-video-generation](07-video-generation) | **Video Generation** | Assembling the final video ad elements and media assets |
| 🛡 [09-security](09-security) | **Security & Ethics** | Brand guidelines, copyright guardrails, and enterprise security |
| ⚙️ [12-deployment](12-deployment) | **Deployment & Iteration** | Running evaluations and tracking model lifecycle |
| ⛓ [13-pipeline](13-pipeline) | **Enterprise Pipelines** | Scaling agentic production via ADK, `uv`, and orchestrating complex tasks |

---

## 🛠 Quick Start: Preparing Your Environment

To run the notebooks and application pipelines, configure your local environment by following these steps from Chapter 3:

### 1. Prerequisites
*   **Python 3.11** (recommended for maximum library compatibility)
*   An IDE of choice (e.g., **Visual Studio Code** with the **Python** and **Jupyter** extensions installed)

### 2. Clone the Repository
```bash
git clone https://github.com/PacktPublishing/Multimodal-Generative-AI-in-the-Enterprise-From-Pixels-to-Profit.git
cd Multimodal-Generative-AI-in-the-Enterprise-From-Pixels-to-Profit
```

### 3. Install Dependencies
You can install dependencies using the standard Python package manager:
```bash
pip install google-genai openai
```

> [!TIP]
> This project is compatible with `uv`. To set up a virtual environment and run commands or tests cleanly, you can use:
> ```bash
> uv venv --python 3.11
> source .venv/bin/activate  # On Windows: .venv\Scripts\activate
> uv pip install google-genai openai
> ```

### 4. Configure Your Frontier AI SDK Keys
Both the **Google Gen AI SDK** and the **OpenAI SDK** use environment variables to locate project context and credentials securely.

#### Google Gen AI (Vertex AI & Developer Keys)
```bash
# Set your enterprise project and billing location
export GOOGLE_CLOUD_PROJECT="your-enterprise-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI=True

# Add your Gemini Developer API Key if running in express mode
export GEMINI_API_KEY="your-gemini-api-key"
```

#### OpenAI SDK
```bash
export OPENAI_API_KEY="sk-proj-..."
```

---

## 🏃‍♂️ Launching Your First Notebook

1. Open this repository inside VS Code:
   ```bash
   code .
   ```
2. Navigate to the folder of your choice (e.g., Chapter 4 or 5) and open any `.ipynb` file.
3. Select your Python 3.11 kernel in the top-right corner of the VS Code notebook interface.
4. Run the cells sequentially to start building!

---

## 📚 Book References & Links
*   **Official Publisher Site**: [Packt Publishing](https://www.packtpub.com/)
*   **Google Gen AI Python SDK Docs**: [GitHub - google-genai](https://github.com/googleapis/python-genai)
*   **OpenAI API Reference**: [OpenAI Docs](https://platform.openai.com/docs/)
