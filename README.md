# prep-telc-osd.com

Plateforme SaaS de préparation aux examens d'allemand **TELC** et **ÖSD** (niveaux B1 et B2).

## Stack

| Couche | Technologie |
|--------|-------------|
| Backend | Python 3.12 · FastAPI · PostgreSQL · SQLAlchemy async · Alembic |
| Frontend | Nuxt 4 · Vue 3 · PrimeVue · Tailwind CSS v4 |
| Paiement | My-CoolPay (MTN MoMo · Orange Money · Carte bancaire) |
| Package managers | uv (Python) · pnpm (Node) |
| Déploiement | Docker · Nginx · Certbot |

## Structure

```
german-test/
├── backend/          # API FastAPI
│   ├── app/
│   │   ├── modules/  # auth, users, exams, payments, invoices, plans...
│   │   └── shared/   # database, exceptions, schemas
│   ├── alembic/      # migrations
│   └── storage/      # audio, invoices (non versionné)
├── frontend/         # App Nuxt 4
│   ├── pages/
│   ├── components/
│   ├── stores/
│   └── composables/
└── setup_backend.sh
```

## Lancement local

### Backend
```bash
cd backend
uv sync
cp .env.example .env   # remplir les variables
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8001
```

### Frontend
```bash
cd frontend
pnpm install
cp .env.example .env
pnpm dev
```

## Variables d'environnement

### Backend (`.env`)
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/deutschtest
SECRET_KEY=your_secret_key
MYCOOLPAY_PUBLIC_KEY=...
MYCOOLPAY_PRIVATE_KEY=...
MYCOOLPAY_BASE_URL=https://my-coolpay.com/api/v1.1/paylink
MYCOOLPAY_CALLBACK_URL=https://prep-telc-osd.com/api/v1/payments/webhook/...
```

### Frontend (`.env`)
```env
NUXT_PUBLIC_API_BASE_URL=http://localhost:8001
```

## Fonctionnalités

- 📝 Simulations d'examens TELC & ÖSD B1/B2 (Lesen, Hören, Schreiben, Sprechen, Sprachbausteine)
- 🎧 Hörverstehen avec fichiers audio
- 💳 Paiement mobile money (MTN · Orange) et carte bancaire
- 🤝 Système de partenaires avec codes promo et commissions
- 📄 Factures PDF générées automatiquement
- 👤 Dashboard étudiant + panel admin complet
- 📊 Suivi de progression et résultats détaillés

## Migrations

```bash
cd backend
# Générer une migration
uv run alembic revision --autogenerate -m "description"
# Appliquer
uv run alembic upgrade head
# Revenir en arrière
uv run alembic downgrade -1
```

## Déploiement

```bash
docker-compose up -d
```

---

© 2026 ITIA Solutions — prep-telc-osd.com