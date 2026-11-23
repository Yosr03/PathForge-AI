# PathForge AI

### Transformez vos compétences en parcours professionnel

**PathForge AI** est une plateforme intelligente d'orientation professionnelle destinée aux étudiants.

Elle vise à analyser les compétences documentées par les CV, les projets et les expériences académiques, puis à les comparer aux exigences des métiers afin de proposer des **recommandations personnalisées, explicables et sourcées**.

Le projet repose sur une architecture cible **Hybrid RAG + GraphRAG + LLM**, développée progressivement.

---

## 1. Problématique

Les étudiants acquièrent de nombreuses compétences pendant leurs formations, stages et projets académiques.

Cependant, ils disposent rarement d'une vision claire de l'adéquation entre leurs compétences et les exigences réelles des métiers.

Les approches classiques de rapprochement entre profils et métiers ne tiennent pas toujours compte des preuves issues des projets, des compétences transférables ni des relations entre métiers et compétences.

**Comment relier les compétences documentées d'un étudiant aux exigences professionnelles d'un métier, tout en justifiant les recommandations proposées ?**

## 2. Notre solution

PathForge AI vise à développer un assistant intelligent capable de :

1. Analyser un CV, des projets et des expériences académiques.
2. Extraire les compétences, expériences et formations de l'étudiant.
3. Identifier les métiers correspondant à son profil.
4. Retrouver les compétences essentielles et optionnelles exigées.
5. Comparer les compétences acquises et les compétences attendues.
6. Identifier les écarts de compétences (*Skill Gap Analysis*).
7. Générer un parcours d'apprentissage personnalisé (*Learning Roadmap*).
8. Justifier les recommandations à partir de sources identifiables.

La plateforme accompagne l'étudiant dans son orientation, sans prétendre certifier automatiquement ses compétences.

## 3. Architecture générale

PathForge AI repose sur deux pipelines complémentaires.

### Pipeline 1 — Ingestion et indexation

**Sources : ESCO, offres d'emploi, CV et projets**

↓

**Extraction, préparation et nettoyage des données**

↓

**Normalisation des compétences et chunking**

↓

**Génération des embeddings avec BGE-M3**

↓

**Indexation vectorielle dans Qdrant**

↓

**Construction du graphe de connaissances avec Neo4j (prévue)**

### Pipeline 2 — Recherche et génération

**React — Interface étudiant (prévue)**

↓

**FastAPI — Backend et orchestration (prévu)**

↓

**Recherche hybride : embeddings + BM25 (prévue)**

↓

**Graph Retrieval avec Neo4j (prévu)**

↓

**Fusion des résultats et reranking avec Cross-Encoder (prévus)**

↓

**Construction du contexte GraphRAG**

↓

**LLM — Analyse des écarts et recommandations sourcées**

PostgreSQL est prévu pour stocker les données applicatives structurées et autorisées.

**Important :** cette architecture représente la cible technique du projet. À ce stade, la partie effectivement développée est principalement le pipeline d'ingestion ESCO et de recherche vectorielle dense.

## 4. Technologies principales

| Domaine | Technologie | État |
|---|---|---|
| Langage principal | Python | Utilisé |
| Base vectorielle | Qdrant 1.9.0 | Fonctionnelle |
| Embeddings | BAAI/bge-m3 | Utilisé |
| Recherche vectorielle | Dense Retrieval, Cosine, Top-K | Testée |
| Ingestion | AsyncQdrantClient, batching | Implémentée |
| Conteneurisation | Docker Compose | Fonctionnelle |
| Base relationnelle | PostgreSQL 16 | Déployée |
| Backend | FastAPI | Prévu |
| Frontend | React | Prévu |
| Graphe de connaissances | Neo4j | Prévu |
| Recherche hybride | BM25 + Dense Retrieval | Prévue |
| Reranking | Cross-Encoder | Prévu |
| Génération augmentée | LLM / GraphRAG | Prévue |
| Évaluation RAG | Ragas | Prévue |
| Versionnement | Git et GitHub | Fonctionnel |

## 5. Sources de données

### 5.1 ESCO — Référentiel européen métiers-compétences

Nous utilisons le référentiel officiel **ESCO v1.2.1**, contenant :

| Données | Volume |
|---|---:|
| Lignes de métiers dans le fichier source | 3 043 |
| Compétences | 13 960 |
| Relations métiers-compétences | 126 051 |
| Métiers uniques après nettoyage | **3 039** |

Les identifiants officiels ESCO sont conservés pour assurer la traçabilité et la cohérence des relations.

Les descriptions des métiers sont enrichies avec leurs compétences essentielles et optionnelles afin de constituer le corpus documentaire utilisé pour la recherche vectorielle.

### 5.2 Offres d'emploi

Un corpus d'offres d'emploi historiques sera exploité pour identifier les compétences, qualifications et expériences demandées par les employeurs.

Il permettra de compléter le référentiel ESCO par des exigences issues du marché de l'emploi.

**État : intégration prévue.**

### 5.3 Profils étudiants

Des CV et profils fictifs, anonymisés ou utilisés avec autorisation serviront à expérimenter :

- Le CV Parsing.
- L'extraction des compétences et expériences.
- Le rapprochement profil–métier.
- L'analyse des compétences manquantes.
- Les recommandations personnalisées.

**État : intégration prévue.**

## 6. Travaux réalisés — Séance 1 : Idéation et cadrage

Nous avons réalisé :

- La définition de la problématique et de la vision produit.
- L'identification des utilisateurs et des cas d'usage.
- La rédaction de la fiche de cadrage.
- La définition du périmètre et des livrables.
- La priorisation des fonctionnalités selon la méthode **MoSCoW**.
- La conception de l'architecture technique initiale.
- La comparaison des solutions vectorielles et le choix de Qdrant.
- La sélection d'ESCO comme référentiel principal.
- La structuration et la publication du dépôt GitHub.

**Mots-clés :** idéation, cadrage, MVP, backlog, MoSCoW, architecture, choix technologiques.

## 7. Travaux réalisés — Séance 2 : Ingestion et Vector Database

### 7.1 Exploration et préparation du corpus

Nous avons exploré les données ESCO, identifié les champs nécessaires et préparé les documents métiers pour l'indexation.

Les traitements comprennent :

- Data Exploration.
- Data Preprocessing.
- Nettoyage des documents.
- Suppression des doublons.
- Conservation des identifiants ESCO.
- Enrichissement des descriptions avec les compétences associées.

**Résultat : 3 039 documents métiers uniques.**

### 7.2 Chunking

Nous avons implémenté un découpage fondé sur les tokens du tokenizer BGE-M3.

Configuration principale :

| Paramètre | Valeur |
|---|---|
| Chunk size | 512 tokens |
| Chunk overlap | 64 tokens |
| Stratégie | Token-based chunking |
| Nombre de chunks | **3 314** |

L'overlap permet de préserver une partie du contexte entre les chunks successifs.

Cette stratégie n'est pas encore un *Semantic Chunking* fondé sur la détection des changements de sens.

### 7.3 Génération des embeddings

Nous utilisons le modèle préentraîné **BAAI/bge-m3**.

- Type : Dense Embeddings.
- Dimension : **1 024**.
- Normalisation des vecteurs.
- Exécution locale.
- Encodage des chunks par lots.

Chaque chunk est transformé en un vecteur numérique exploitable par Qdrant.

### 7.4 Indexation vectorielle dans Qdrant

Nous avons créé la collection principale :

`pathforge_esco`

Configuration :

- Distance : **Cosine**.
- Dimension vectorielle : **1 024**.
- Nombre de points validés : **3 314**.
- Recherche des voisins proches avec l'indexation vectorielle Qdrant.
- Stockage persistant via Docker Volume.

Chaque point contient également un payload avec des informations telles que :

- `title`
- `text`
- `source`
- `type`
- `occupation_uri`
- `chunk_index`

Ces métadonnées permettent d'identifier les sources et d'appliquer des filtres lors de la recherche.

### 7.5 Ingestion asynchrone

Le script `scripts/ingest.py` utilise **AsyncQdrantClient**.

Il prend en charge :

- La préparation des chunks.
- La vérification des points existants.
- La génération des embeddings manquants.
- L'indexation par lots.
- La reprise d'une ingestion interrompue.
- La vérification finale du nombre de points.
- Le mode simulation `--dry-run`.

Le script a été validé sur un corpus déjà entièrement indexé : **3 314 points attendus et 3 314 points présents**.

La reprise sans réindexation inutile a été vérifiée. Une nouvelle insertion asynchrone complète reste à valider séparément.

### 7.6 Recherche sémantique Top-K

Nous avons développé `scripts/search_test.py` pour interroger la collection Qdrant.

Fonctionnalités :

- Transformation de la question en embedding BGE-M3.
- Recherche vectorielle par similarité Cosine.
- Retour des meilleurs résultats Top-K.
- Affichage des scores de similarité.
- Affichage des titres, sources et identifiants ESCO.
- Filtrage par métadonnées.

Exemple de requête :

`Which occupations require Python, SQL and data analysis skills?`

Lors de notre test, **Data Analyst** a été retourné en première position avec un score de similarité de **0,6368**.

Ce score mesure une proximité vectorielle, et non une probabilité de compatibilité professionnelle.

### 7.7 Benchmark des stratégies de chunking

Nous avons préparé un benchmark comparant deux configurations :

| Configuration | Chunk size | Overlap | Collection |
|---|---:|---:|---|
| A | 512 | 64 | `pathforge_esco` |
| B | 256 | 32 | `pathforge_esco_256` |

Un jeu de **10 questions de test**, associé à des métiers ESCO attendus, a été préparé dans :

`data/benchmark/questions.json`

Les métriques prévues sont :

- **Hit@5** : présence du métier attendu parmi les cinq premiers métiers distincts.
- **MRR@5** : qualité du rang du premier métier attendu.
- Latence de recherche, si mesurée dans des conditions comparables.

**État :** deuxième indexation lancée ; résultats finaux du benchmark non encore confirmés.

## 8. Démarrage local

### Prérequis

- Git
- Docker Desktop
- Docker Compose
- Python
- Environnement virtuel Python et dépendances du projet

### Démarrer les services

Depuis la racine du projet :

```powershell
docker compose up -d
```

Vérifier les conteneurs :

```powershell
docker compose ps
```

### Accéder à Qdrant

Tableau de bord :

http://localhost:6333/dashboard

### Vérifier l'ingestion

```powershell
python scripts/ingest.py --dry-run
```

### Exécuter une recherche vectorielle

```powershell
python scripts/search_test.py --query "Which occupations require Python, SQL and data analysis skills?"
```

### Arrêter les services

```powershell
docker compose down
```

Les données Qdrant sont conservées dans un volume Docker, sauf suppression explicite de ce volume.

**Remarque :** le corpus préparé `data/processed/esco_documents_clean.json` doit être disponible pour l'ingestion. Il est exclu du dépôt Git actuel ; sa préparation nécessite les données ESCO et les scripts correspondants.

## 9. Répartition des responsabilités — Équipe de trois personnes

| Module | Responsabilités | Livrable attendu |
|---|---|---|
| **Personne 1 — Profile Intelligence AI / RAG** | CV Parsing, extraction LLM des compétences et expériences, Document RAG, recherche hybride Qdrant + BM25, API d'analyse de profil | Profil étudiant structuré avec compétences extraites |
| **Personne 2 — Job & Career Intelligence AI / GraphRAG** | Analyse des offres d'emploi, extraction des compétences, graphe Neo4j, Graph Retrieval, recherche de métiers, matching | Métiers adaptés et compétences exigées |
| **Personne 3 — Career Copilot & Recommendation AI / LLM** | Orchestration RAG/GraphRAG, Skill Gap Analysis, Learning Roadmap, Cross-Encoder, évaluation Ragas | Recommandations personnalisées et plan d'apprentissage |

L'ingestion ESCO et la recherche vectorielle déjà réalisées constituent une base technique commune, principalement utile au module Job & Career Intelligence.

Les tests d'intégration et la validation finale seront effectués collectivement.

## 10. Documentation

Le projet comprend notamment :

- `fiche_cadrage_projet.md` — Problématique, objectifs et périmètre.
- `matrice_moscow_backlog.md` — Priorisation MoSCoW.
- `scripts/prepare_esco.py` — Préparation du corpus.
- `scripts/clean_esco.py` — Nettoyage et déduplication.
- `scripts/ingest.py` — Ingestion asynchrone.
- `scripts/ingest_full.py` — Script d'indexation complète.
- `scripts/search_test.py` — Recherche sémantique.
- `scripts/ingest_benchmark_256.py` — Deuxième stratégie de chunking.
- `scripts/check_benchmark.py` — Validation des questions de benchmark.
- `data/benchmark/questions.json` — Jeu de questions d'évaluation.

## 11. État d'avancement

### Réalisé

- [x] Définition de la vision et de la problématique.
- [x] Fiche de cadrage et backlog MoSCoW.
- [x] Conception de l'architecture cible.
- [x] Sélection de Qdrant.
- [x] Déploiement de Qdrant et PostgreSQL avec Docker Compose.
- [x] Exploration du référentiel ESCO.
- [x] Préparation et nettoyage du corpus de 3 039 métiers.
- [x] Chunking 512 tokens / overlap 64.
- [x] Génération des embeddings BGE-M3.
- [x] Indexation de 3 314 chunks dans Qdrant.
- [x] Association des métadonnées aux vecteurs.
- [x] Recherche sémantique Top-K.
- [x] Filtrage des résultats par métadonnées.
- [x] Implémentation du script d'ingestion asynchrone.
- [x] Validation de la reprise sur corpus déjà indexé.
- [x] Préparation de 10 questions de benchmark.
- [x] Publication du projet sur GitHub.

### En cours

- [ ] Vérification finale de l'indexation 256/32.
- [ ] Exécution du benchmark sur les 10 questions.
- [ ] Comparaison Hit@5 et MRR@5.
- [ ] Rédaction du rapport comparatif.
- [ ] Validation d'une nouvelle ingestion asynchrone avec insertion effective.

### À réaliser

- [ ] Intégration des profils étudiants.
- [ ] Intégration des offres d'emploi.
- [ ] Normalisation multi-source des compétences.
- [ ] Construction du Knowledge Graph avec Neo4j.
- [ ] Implémentation du Hybrid Search BM25 + Dense Retrieval.
- [ ] Développement du backend FastAPI.
- [ ] Développement de l'interface React.
- [ ] Orchestration Hybrid RAG et GraphRAG.
- [ ] Reranking avec Cross-Encoder.
- [ ] Skill Gap Analysis.
- [ ] Génération des recommandations et Learning Roadmaps.
- [ ] Évaluation du système avec Ragas et métriques adaptées.
- [ ] Tests d'intégration et préparation de la démonstration finale.

## 12. Limites

PathForge AI est un outil d'aide à l'orientation professionnelle.

Il ne certifie pas automatiquement les compétences d'un étudiant et ne garantit ni son employabilité ni son recrutement.

La qualité des recommandations dépendra de la fiabilité des sources, de la précision des compétences extraites et des performances du système de recherche et de génération.

À ce stade, les résultats de recherche vectorielle constituent une première validation technique. Ils ne démontrent pas encore la qualité d'un système complet de recommandation professionnelle.
