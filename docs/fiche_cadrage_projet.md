# Fiche de Cadrage d’Ingénierie — Projet Fédérateur AI-BD_BI

## Spécification du Moteur RAG / Data Intelligent

**Projet : PathForge AI — Transformez vos compétences en parcours professionnel**

---

## 1. Fiche d'identité du projet

| Élément | Information |
|---|---|
| **Nom du projet** | PathForge AI |
| **Intitulé complet** | Plateforme intelligente d'orientation professionnelle par Hybrid RAG et GraphRAG |
| **Domaine** | Intelligence artificielle, NLP, recherche d'information et orientation professionnelle |
| **Public cible** | Étudiants en fin de cursus et jeunes diplômés |
| **Équipe** | 3 membres |
| **Dépôt GitHub** | https://github.com/Yosr03/PathForge-AI |
| **Branche principale** | `main` |
| **Méthodologie** | Développement incrémental, validation par séances et architecture modulaire |
| **État actuel** | Séances 1 et 2 : cadrage et première chaîne d'ingestion/recherche vectorielle |

### Répartition des responsabilités

| Membre | Module | Responsabilités principales |
|---|---|---|
| **Personne 1** | Profile Intelligence AI / RAG | CV Parsing, extraction des compétences, Document RAG, recherche hybride, API d'analyse du profil |
| **Personne 2** | Job & Career Intelligence AI / GraphRAG | Analyse des métiers et offres d'emploi, relations ESCO, Knowledge Graph Neo4j, matching profil–métier |
| **Personne 3** | Career Copilot & Recommendation AI / LLM | Orchestration, Skill Gap Analysis, recommandations, Learning Roadmap, reranking et évaluation |

Les trois modules seront intégrés et testés collectivement.

---

## 2. Cadrage du problème métier — Problem-First

### 2.1 Persona cible et contexte opérationnel

**Utilisateur principal :** étudiant en dernière année d'études supérieures ou jeune diplômé souhaitant identifier les métiers adaptés à son profil et comprendre les compétences nécessaires pour atteindre son objectif professionnel.

**Utilisateur secondaire envisagé :** conseiller d'orientation ou responsable d'accompagnement professionnel.

### Pain point

Deux étudiants peuvent posséder le même diplôme tout en ayant des profils très différents en raison de leurs projets, stages, expériences et compétences.

Les étudiants rencontrent plusieurs difficultés :

- Identifier les métiers correspondant réellement à leur profil.
- Valoriser les compétences acquises à travers leurs projets.
- Comprendre les compétences exigées par les employeurs.
- Distinguer les compétences démontrées des compétences simplement déclarées.
- Identifier les compétences manquantes.
- Construire un parcours concret de progression professionnelle.

### Limites des approches classiques

Les plateformes d'emploi traditionnelles reposent souvent sur des filtres, des mots-clés et des correspondances lexicales.

Elles ne permettent pas toujours de comprendre les relations complexes entre :

**Étudiant → Projet → Compétence → Métier → Formation**

Un LLM utilisé seul peut également produire des recommandations insuffisamment justifiées ou non vérifiables.

### Problématique centrale

**Comment relier les compétences documentées d'un étudiant aux exigences professionnelles d'un métier, tout en proposant des recommandations personnalisées, explicables et fondées sur des sources vérifiables ?**

### 2.2 Proposition de valeur

PathForge AI vise à :

1. Analyser les CV, projets et expériences académiques.
2. Extraire et normaliser les compétences.
3. Rechercher les métiers correspondant au profil.
4. Identifier les compétences essentielles et optionnelles requises.
5. Comparer les compétences du profil aux exigences professionnelles.
6. Détecter les écarts et les preuves insuffisantes.
7. Proposer un parcours d'apprentissage personnalisé.
8. Fournir des justifications et références documentaires.

L'interface cible permettra de consulter les sources utilisées et, si la génération en streaming est retenue, d'afficher progressivement les réponses.

**Positionnement :** outil d'aide à l'orientation, et non système de certification des compétences ou garantie de recrutement.

---

## 3. Données et volumétrie

### 3.1 Formats de données

| Format | Utilisation |
|---|---|
| CSV | Référentiel ESCO source |
| JSON | Corpus préparé, profils structurés et benchmark |
| Markdown | Documentation et descriptions de projets |
| PDF | CV étudiants, dans les prochaines étapes |
| SQL | Données applicatives futures dans PostgreSQL |
| Images / scans | Hors périmètre initial |

### 3.2 Sources de données

#### Dataset 1 — ESCO v1.2.1

**Source officielle :** https://esco.ec.europa.eu/

ESCO est le référentiel principal utilisé pour relier les métiers aux compétences.

| Données | Volumétrie |
|---|---:|
| Lignes de métiers source | 3 043 |
| Métiers uniques après nettoyage | **3 039** |
| Compétences | **13 960** |
| Relations métiers-compétences | **126 051** |
| Documents métiers préparés | **3 039** |
| Chunks indexés dans Qdrant | **3 314** |

Les identifiants officiels ESCO sont conservés pour assurer la traçabilité.

**État :** corpus métiers préparé, découpé, vectorisé et indexé.

Les compétences et relations ESCO sont déjà utilisées pour enrichir les descriptions documentaires. Leur exploitation sous forme de graphe Neo4j reste à réaliser.

#### Dataset 2 — Offres d'emploi

**Source envisagée :** France Travail — https://francetravail.io/

Objectif :

- Analyser les descriptions d'offres.
- Extraire les compétences et qualifications demandées.
- Identifier les exigences professionnelles.
- Compléter le référentiel ESCO avec des besoins issus du marché.

L'accès aux données et les conditions de réutilisation devront être vérifiés.

**État : intégration prévue.**

#### Dataset 3 — Profils étudiants

Des profils fictifs, anonymisés ou autorisés seront préparés pour tester :

- CV Parsing.
- Extraction des compétences, formations et expériences.
- Analyse du profil.
- Matching profil–métier.
- Recommandations personnalisées.

**État : intégration prévue.**

#### Dataset 4 — Formations et certifications

**Source envisagée :** France Compétences — https://www.francecompetences.fr/

Objectif :

- Identifier les formations pertinentes.
- Relier les formations aux compétences développées.
- Construire des Learning Roadmaps.

Les modalités d'accès et de réutilisation restent à vérifier.

**État : source complémentaire envisagée, non encore intégrée.**

### 3.3 Stratégie d'intégration des données

Nous adoptons une **approche incrémentale**.

La séance 2 se concentre sur la validation du pipeline ESCO :

**ESCO → Preprocessing → Chunking → Embeddings → Qdrant → Top-K**

Les autres sources seront intégrées progressivement après validation des mécanismes d'ingestion et de recherche.

Cette stratégie permet de tester chaque composant séparément et de limiter les difficultés de débogage lors de l'intégration multi-source.

### 3.4 Fréquence de mise à jour

- **ESCO :** corpus versionné, actualisé lors de nouvelles publications pertinentes.
- **Offres d'emploi :** mises à jour batch envisagées, selon la disponibilité des données et les autorisations.
- **Profils étudiants :** mise à jour lors d'une modification autorisée du profil.
- **Formations :** actualisation selon les sources disponibles.

Aucun mécanisme de synchronisation quotidienne n'est encore implémenté.

---

## 4. Architecture technique et composants RAG

### 4.1 Architecture cible

PathForge AI repose sur deux pipelines complémentaires.

**Pipeline d'ingestion :**

Sources documentaires

↓

Extraction et nettoyage

↓

Normalisation des compétences

↓

Chunking

↓

Embeddings BGE-M3

↓

Indexation Qdrant

↓

Construction du graphe Neo4j (prévue)

**Pipeline de recherche et génération :**

Interface React (prévue)

↓

Backend FastAPI (prévu)

↓

Recherche dense Qdrant + recherche lexicale BM25

↓

Exploration du graphe Neo4j

↓

Fusion et reranking

↓

Construction du contexte GraphRAG

↓

LLM

↓

Réponse personnalisée avec sources

### 4.2 Stratégie de chunking

**Stratégie effectivement implémentée : Token-based Chunking.**

| Paramètre | Configuration principale |
|---|---|
| Modèle de tokenisation | BGE-M3 |
| Chunk size | **512 tokens** |
| Chunk overlap | **64 tokens** |
| Documents | **3 039** |
| Chunks générés | **3 314** |

Le chevauchement préserve une partie du contexte entre deux chunks.

Cette stratégie est fondée sur le nombre de tokens. Elle ne doit pas être présentée comme un Semantic Chunking.

**Comparaison en préparation :**

- Configuration A : 512 tokens, overlap 64.
- Configuration B : 256 tokens, overlap 32.
- Jeu d'évaluation : 10 questions avec métiers attendus.

L'objectif est de comparer la pertinence des résultats avant de sélectionner définitivement une configuration.

### 4.3 Modèle d'embeddings

**Modèle retenu : BAAI/bge-m3.**

Caractéristiques :

- Modèle préentraîné.
- Support multilingue.
- Embeddings denses.
- Dimension : **1 024**.
- Vecteurs normalisés.
- Exécution locale sur CPU.

Le modèle transforme les passages textuels et les requêtes en vecteurs exploitables par le moteur de recherche.

### 4.4 Base vectorielle

**Base sélectionnée : Qdrant.**

Justifications :

- Recherche vectorielle native.
- Similarité Cosine.
- Indexation HNSW.
- Filtrage des payloads.
- Client Python.
- Déploiement Docker Compose.
- Évolution possible vers la recherche hybride.

**Collection principale :** `pathforge_esco`

| Élément | Valeur |
|---|---|
| Dimension vectorielle | 1 024 |
| Distance | Cosine |
| Points indexés | **3 314** |
| Stockage | Volume Docker persistant |
| Métadonnées | Payloads |
| Recherche | Top-K |

Les payloads permettent de conserver les informations nécessaires à la traçabilité, comme le titre, le texte, la source, le type, l'identifiant ESCO et la position du chunk.

### 4.5 Ingestion asynchrone

Le script `scripts/ingest.py` utilise **AsyncQdrantClient**.

Fonctionnalités implémentées :

- Lecture du corpus préparé.
- Vérification des points déjà indexés.
- Génération des embeddings manquants.
- Traitement par lots de 64.
- Identifiants stables.
- Reprise d'ingestion.
- Vérification finale.
- Mode `--dry-run`.

**Validation effectuée :** 3 314 points attendus et 3 314 points présents dans Qdrant.

La reprise sans réindexation inutile a été vérifiée. Une insertion asynchrone effective de nouveaux points reste à valider séparément.

### 4.6 Recherche sémantique

Le script `scripts/search_test.py` permet de :

- Recevoir une requête.
- Générer son embedding.
- Rechercher les vecteurs proches dans Qdrant.
- Retourner les résultats Top-K.
- Afficher les scores de similarité.
- Appliquer des filtres par métadonnées.

**Exemple testé :**

*Which occupations require Python, SQL and data analysis skills?*

Premier résultat observé : **Data Analyst**, avec un score de similarité de **0,6368**.

Ce score représente une similarité vectorielle et non une probabilité de réussite professionnelle.

### 4.7 Recherche hybride — Prévue

L'architecture cible combinera :

- **Dense Retrieval :** embeddings BGE-M3.
- **Sparse / Lexical Retrieval :** BM25.
- **Fusion :** Reciprocal Rank Fusion (RRF).
- **Reranking :** Cross-Encoder.

La recherche dense est opérationnelle. Les autres mécanismes restent à intégrer et à évaluer.

### 4.8 Extension GraphRAG — Prévue

Neo4j permettra de représenter les relations suivantes :

- Étudiant → possède → Compétence.
- Projet → démontre → Compétence.
- Métier → requiert → Compétence.
- Formation → développe → Compétence.
- Offre d'emploi → concerne → Métier.

Le Graph Retrieval complétera le Dense Retrieval afin de répondre à des questions nécessitant plusieurs relations.

**GraphRAG est une extension du socle RAG, et non un remplacement de Qdrant.**

### 4.9 Génération et application

Composants prévus :

- **FastAPI :** backend et orchestration.
- **React :** interface utilisateur.
- **LLM instruct :** génération de recommandations.
- **Cross-Encoder :** reranking.
- **PostgreSQL :** stockage applicatif.
- **SSE :** streaming éventuel des réponses.
- **Ragas :** évaluation de la génération.

Le choix définitif du LLM et du Cross-Encoder sera validé selon les performances, les ressources et les contraintes de confidentialité.

---

## 5. Métriques quantitatives et SLAs

### 5.1 Objectifs cibles du projet

| Métrique | Définition | Objectif |
|---|---|---|
| **Recall@10** | Couverture des documents pertinents dans les 10 premiers résultats | ≥ 85 % |
| **Faithfulness — Ragas** | Fidélité des réponses aux sources | ≥ 0,85 |
| **Answer Relevance — Ragas** | Pertinence des réponses générées | ≥ 0,80 |
| **TTFT** | Temps jusqu'au premier token généré | < 800 ms |
| **Latence E2E P95** | 95e percentile du temps de réponse complet | < 3,5 s |

Ces valeurs sont des **objectifs de performance issus du cadrage**, pas des résultats déjà mesurés.

Leur faisabilité devra être vérifiée expérimentalement.

### 5.2 Benchmark de la séance 2

Un jeu de **10 questions** avec identifiants ESCO attendus a été préparé.

Métriques retenues :

**Hit@5 :** proportion de questions pour lesquelles le métier attendu figure parmi les cinq premiers métiers distincts.

**MRR@5 :** moyenne de l'inverse du rang du métier attendu, limité aux cinq premiers résultats.

**Latence :** temps de recherche, à mesurer dans des conditions comparables.

Configurations comparées :

| Configuration | Chunk size | Overlap |
|---|---:|---:|
| A | 512 | 64 |
| B | 256 | 32 |

Le benchmark doit permettre de comparer les stratégies de chunking sur une base expérimentale.

**État :** jeu de questions préparé ; résultats comparatifs finaux non encore confirmés.

### 5.3 Évaluation future du système complet

Après intégration du RAG et du GraphRAG :

- Comparaison Dense Retrieval / Hybrid Retrieval.
- Évaluation de la pertinence des sources.
- Évaluation de la fidélité des réponses.
- Mesure des hallucinations.
- Mesure de la latence.
- Évaluation du matching profil–métier.
- Évaluation de la qualité des recommandations.

---

## 6. Gestion des risques et garde-fous

### 6.1 Prévention des hallucinations

Le LLM devra produire des réponses fondées sur les documents récupérés.

Règle prévue :

*Si les sources disponibles ne permettent pas de conclure, le système doit le signaler explicitement.*

Les recommandations devront être accompagnées de références vérifiables.

### 6.2 Protection des secrets

- Variables sensibles dans `.env`.
- Exclusion de `.env` du dépôt Git.
- Utilisation éventuelle d'un `.env.example` sans secrets.
- Aucun identifiant ni clé API dans le code versionné.

### 6.3 Isolation et sécurité

- Déploiement avec Docker Compose.
- Réseau Docker pour les services.
- Exposition limitée aux ports nécessaires.
- Volumes persistants pour les bases.

La sécurité des accès devra être renforcée avant tout déploiement public.

### 6.4 Confidentialité

- Utilisation initiale de profils fictifs.
- Anonymisation ou autorisation appropriée pour les données réelles.
- Minimisation des données personnelles.
- Politique de conservation à définir.
- Protection des CV et informations personnelles.

### 6.5 Traçabilité des données

- Conservation des identifiants ESCO.
- Conservation de la source documentaire.
- Versionnement des référentiels.
- Métadonnées associées aux chunks.
- Références vérifiables dans les futures recommandations.

### 6.6 Biais de recommandation

Le système devra :

- Expliquer les compétences prises en compte.
- Identifier les preuves insuffisantes.
- Permettre la correction des informations du profil.
- Éviter de présenter les recommandations comme des décisions définitives.

### 6.7 Risques techniques

Risques identifiés :

- Consommation mémoire du modèle BGE-M3.
- Temps de génération des embeddings sur CPU.
- Augmentation du nombre de chunks.
- Latence de recherche et de génération.
- Synchronisation entre Qdrant, PostgreSQL et Neo4j.
- Qualité variable des données externes.

Mesures envisagées :

- Batching.
- Ingestion reprenable.
- Benchmark de chunking.
- Surveillance de la latence.
- Réduction du corpus pour certains tests.
- Évaluation d'un modèle plus léger si nécessaire.

---

## 7. État d'avancement du projet

### Séance 1 — Idéation et cadrage

**Réalisé :**

- [x] Définition de la problématique.
- [x] Identification des personas.
- [x] Définition de la proposition de valeur.
- [x] Cadrage du MVP.
- [x] Priorisation MoSCoW.
- [x] Conception de l'architecture initiale.
- [x] Choix des technologies principales.
- [x] Sélection du référentiel ESCO.
- [x] Création du dépôt GitHub.

### Séance 2 — Ingestion et Vector Database

**Réalisé :**

- [x] Exploration des données ESCO.
- [x] Préparation et nettoyage du corpus.
- [x] Obtention de 3 039 métiers uniques.
- [x] Token-based Chunking 512/64.
- [x] Génération de 3 314 chunks.
- [x] Embeddings BGE-M3 de 1 024 dimensions.
- [x] Déploiement de Qdrant et PostgreSQL avec Docker Compose.
- [x] Création de la collection `pathforge_esco`.
- [x] Indexation de 3 314 points.
- [x] Métadonnées associées aux vecteurs.
- [x] Recherche sémantique Top-K.
- [x] Filtrage par métadonnées.
- [x] Implémentation de l'ingestion asynchrone.
- [x] Vérification de reprise sur collection complète.
- [x] Préparation du jeu de 10 questions.

**En cours :**

- [ ] Vérification de l'indexation 256/32.
- [ ] Calcul des métriques Hit@5 et MRR@5.
- [ ] Comparaison expérimentale des deux configurations.
- [ ] Validation d'une insertion asynchrone effective de points manquants.

### Étapes suivantes

- [ ] Intégration des profils étudiants.
- [ ] Intégration des offres d'emploi.
- [ ] Implémentation de BM25.
- [ ] Fusion hybride RRF.
- [ ] Construction du Knowledge Graph Neo4j.
- [ ] Graph Retrieval.
- [ ] Développement de FastAPI.
- [ ] Développement de React.
- [ ] Intégration du LLM.
- [ ] Reranking Cross-Encoder.
- [ ] Skill Gap Analysis.
- [ ] Learning Roadmap.
- [ ] Évaluation Ragas.
- [ ] Tests d'intégration et démonstration finale.

---

## 8. Conclusion du cadrage

PathForge AI vise à construire une plateforme d'orientation professionnelle fondée sur des données documentées, une recherche hybride et un graphe de connaissances.

Le projet suit une **approche progressive et modulaire**.

Les séances 1 et 2 ont permis de définir le problème métier, de concevoir l'architecture cible et de développer une première chaîne fonctionnelle :

**ESCO → Preprocessing → Chunking → BGE-M3 → Qdrant → Semantic Search Top-K**

Les prochaines étapes consisteront à intégrer les profils étudiants et les offres d'emploi, enrichir la recherche avec BM25 et Neo4j, puis construire un moteur de recommandation personnalisé, explicable et évalué.

**La priorité est de valider chaque composant avant l'intégration complète du système.**
