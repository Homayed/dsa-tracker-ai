# DSA Tracker AI API — Demo Script

## 2-Minute Demo Script

Hi, I’m Zarif, and this is my project: **DSA Tracker AI API**.

This is an AI-assisted backend system built for tracking DSA preparation and generating personalized learning feedback.

The problem I wanted to solve was simple: when someone practices LeetCode or DSA, they usually track only the problem name or status. But they often forget what mistake they made, what pattern they struggled with, and what they should review next.

So I built a backend where users can track solved problems, notes, mistakes, review logs, confidence level, time taken, complexity, and weak patterns.

The backend is built with **FastAPI, Python, SQLAlchemy, Alembic, JWT authentication, and PostgreSQL**. The database is hosted on **Supabase**, and I used **pgvector** to store embeddings for problems, notes, mistakes, and review logs.

The AI part works like this:

When the user asks a question, for example, **“What mistake did I make in Two Sum and what should I review?”**, the system converts the question into an OpenAI embedding. Then it searches the vector database to find the most relevant saved learning data. After that, the retrieved context is passed to an LLM, which generates a personalized answer based on the user’s own progress.

So this is not just a generic chatbot. It is a **RAG-based learning assistant** because the answer is grounded in the user’s saved DSA history.

The project also includes an AI study recommendation endpoint. It can generate a study plan based on the user’s solved problems, confidence levels, mistakes, notes, and review logs.

For production readiness, I added Docker support, Render deployment, GitHub Actions CI, Pytest tests, and AI cost-control environment variables. For example, I can keep AI enabled but disable automatic embeddings to avoid unnecessary OpenAI API cost.

The project is deployed live on Render, the API documentation is available through Swagger, and the GitHub repository includes a professional README, badges, screenshots, and passing CI tests.

Overall, this project helped me connect backend engineering, authentication, database design, vector search, OpenAI embeddings, RAG, testing, deployment, and learning analytics into one complete system.

---

## 30-Second Short Version

DSA Tracker AI API is an AI-assisted backend system for DSA preparation. Users can track solved problems, notes, mistakes, review logs, confidence levels, and weak patterns.

The backend is built with FastAPI, PostgreSQL, Supabase, SQLAlchemy, JWT auth, Docker, and Render. The AI part uses OpenAI embeddings, pgvector semantic search, and RAG to answer questions based on the user’s own learning history.

For example, if a user asks, **“What mistake did I make in Two Sum?”**, the system retrieves the relevant mistake, note, and review log, then generates a personalized answer using an LLM.

The project also includes AI study recommendations, GitHub Actions CI, Pytest tests, and a live Swagger demo.
