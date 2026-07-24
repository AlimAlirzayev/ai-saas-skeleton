# AI SaaS Skeleton 🤖

Production serverda işləyən tam AI backend sistemi.

## Nədir bu?

Hər AI layihəsi eyni problemləri həll etməlidir: API, verilənlər bazası, keş, workflow, AI modeli.
Bu layihə həmin problemləri bir dəfəlik həll edir.
Bundan sonra istənilən yeni AI ideyasını 2 həftəyə deyil, 2 günə çıxarmaq mümkün olur.

## Stack

| Texnologiya | Nə üçün |
|-------------|---------|
| FastAPI | REST API |
| PostgreSQL | Söhbət tarixi |
| Redis | Keş sistemi |
| LangChain LCEL | AI chain |
| Groq (Llama3) | Pulsuz LLM |
| n8n | Workflow avtomatizasiyası |
| Qdrant | Vector DB |
| Docker | Konteynerləşdirmə |
| GitHub Actions | CI/CD |

## Necə işləyir?

POST /chat
→ Redis keş yoxla
→ PostgreSQL-dən söhbət tarixini oxu
→ LangChain: Prompt → Groq → Cavab
→ PostgreSQL-ə yaz
→ Redis-ə keşlə
→ Cavab qaytar


## API

| Method | URL | Nə edir |
|--------|-----|---------|
| GET | /health | Sistem yoxlama |
| POST | /chat | AI ilə söhbət |
| GET | /history/{session_id} | Söhbət tarixi |

## Quraşdırma

```bash
git clone https://github.com/AlimAlirzayev/ai-saas-skeleton.git
cd ai-saas-skeleton
cp .env.example .env
# .env-də GROQ_API_KEY-i doldur
docker compose up -d
```

## Deploy

GitHub Actions ilə avtomatikdir:

git push → GitHub Actions → SSH → Server → docker compose up


## Müəllif

Alim Əlirzayev — AI Engineering, 3-cü ay capstone layihəsi