# Case Technique — Développeur Full Stack - Boris Le Bon

Puisque les instructions sont en français,
je me permettrais d'écrire ainsi concernant le README.MD

## Prerequis

- [Docker](https://docs.docker.com/get-docker/) et [Docker Compose](https://docs.docker.com/compose/install/) (inclus dans Docker Desktop sur Mac/Windows)
- Une cle API Anthropic (disponible sur [console.anthropic.com](https://console.anthropic.com/))

## Installation et lancement

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd Orbital_tech_challenge
```

### 2. Configurer l'environnement

```bash
cp .env.example .env
```

Editer `.env` avec votre cle API :

```
MODEL=anthropic:claude-haiku-4-5-20251001
ANTHROPIC_API_KEY=sk-ant-api03-VOTRE_CLE_ICI
```

### 3. Ajouter des donnees

Placer vos fichiers CSV dans le dossier `data/`. Des fichiers d'exemple sont deja fournis.

### 4. Lancer l'API (backend FastAPI)

```bash
docker compose up api --build
```

L'API est accessible sur `http://localhost:8000`.
La documentation Swagger est disponible sur `http://localhost:8000/docs`.

### 5. Lancer l'agent CLI (optionnel)

L'agent CLI original reste disponible :

```bash
docker compose run --rm agent
```

## A propos de UV

J'ai modifie la configuration pre-etablie afin d'ajouter uv.
Avec uv, plus besoin de requirements.txt, les dependances s'installent dans pyproject.toml
automatiquement lorsqu'on les ajoute avec les commandes uv.

## Lancer les tests

```bash
# Avec uv (en local)
uv run pytest tests

# Avec Docker
docker compose run --rm api uv run pytest tests
```

## Lancer les linters

note: git doit etre configuré avec le projet

```bash
uv run pre-commit run --all-files
```

## Instructions

### Contexte

Tu reçois un **agent d'analyse de données** qui fonctionne en mode CLI (terminal).

L'agent peut :

- Répondre à des questions sur des données en générant du **SQL** (via DuckDB)
- Créer des **visualisations** avec Plotly
- Expliquer son **raisonnement** (balises `<thinking>`)
- Enchaîner les étapes automatiquement via des **tool calls**

L'agent est construit avec [PydanticAI](https://ai.pydantic.dev/).

---

### Objectif

**Transformer cet agent CLI en une application web complète.**

L'utilisateur doit pouvoir poser des questions dans une interface web et voir en temps réel :

1. Le **raisonnement** de l'agent (thinking) — affiché progressivement
2. Les **appels d'outils** (tool calls) — nom, arguments, résultat
3. Les **visualisations** Plotly / tableaux de données
4. La **réponse finale** de l'agent

---

### Ce qui est fourni

```
case_fullstack/
├── agent/
│   ├── agent.py              # Création de l'agent PydanticAI
│   ├── context.py            # Contexte injecté dans les tools
│   ├── prompt.py             # System prompt
│   └── tools/
│       ├── query_data.py     # Exécution SQL via DuckDB
│       └── visualize.py      # Création de visualisations Plotly
├── data/                     # Fichiers CSV (tes données de test)
├── output/                   # Visualisations générées
├── main.py                   # Script CLI de démonstration
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

### Setup

```bash
# 1. Configurer la clé API
cp .env.example .env
# Éditer .env avec ta clé API

# 2. Ajouter des fichiers CSV dans data/

# 3. Lancer le CLI via Docker
docker compose run --rm agent
```

> Le volume `data/` est monté dans le container — tu peux ajouter/modifier des CSV sans rebuild.
> Les visualisations générées sont dans `output/`.

---

### Ce qui est attendu

#### Minimum requis

- [ ] **Backend API** avec endpoint de streaming (SSE ou WebSocket)
- [ ] **Frontend web** avec :
  - [ ] Champ texte pour poser des questions
  - [ ] Affichage **streaming** du thinking (collapsible/dépliable)
  - [ ] Affichage des **tool calls** (nom de l'outil, arguments, résultat)
  - [ ] Rendu des **visualisations Plotly** (graphiques interactifs)
  - [ ] Rendu des **tableaux** de données
- [ ] **Code propre** et structuré

---

### Stack technique

- **Backend** : FastAPI
- **Frontend** : Libre React
- **Streaming** : SSE ou WebSocket (à ton choix)

---

### Critères d'évaluation

| Critère | Description |
|---------|-------------|
| **Fonctionnalité** | Le streaming fonctionne, le thinking s'affiche en temps réel, les tool calls sont visibles, les visualisations s'affichent |
| **Code** | Propre, structuré, lisible, bien découpé |
| **UX** | L'expérience utilisateur est fluide et intuitive |
| **Architecture** | Bonne séparation frontend / backend, gestion des états cohérente |

---

### Ressources utiles

- [PydanticAI — Documentation](https://ai.pydantic.dev/)
- [PydanticAI — Streaming](https://ai.pydantic.dev/streaming/)
- [PydanticAI — Tools](https://ai.pydantic.dev/tools/)
- [Plotly.js — React integration](https://plotly.com/javascript/react/)
- [FastAPI — Streaming Response](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [Server-Sent Events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
