# Backlog Technique MoSCoW — PathForge AI

## Découpage Agile des User Stories, critères d'acceptation et suivi d'avancement

**Projet :** PathForge AI — Plateforme intelligente d'orientation professionnelle par Hybrid RAG et GraphRAG

**Dépôt GitHub :** https://github.com/Yosr03/PathForge-AI

**Équipe :** 3 personnes

**Avancement documenté :** Séances 1 et 2

---

## 1. Objectif du backlog

Ce backlog organise les fonctionnalités techniques nécessaires à la réalisation de PathForge AI.

Il repose sur la méthode **MoSCoW**, qui distingue quatre niveaux de priorité :

- **MUST HAVE :** fonctionnalités indispensables à la livraison finale.
- **SHOULD HAVE :** fonctionnalités importantes apportant une forte valeur ajoutée.
- **COULD HAVE :** fonctionnalités complémentaires réalisables si les ressources le permettent.
- **WON'T HAVE :** fonctionnalités explicitement exclues du périmètre.

Le projet est développé selon une approche incrémentale : chaque composant est implémenté, testé et validé avant son intégration dans l'architecture complète.

Les critères d'acceptation permettent de déterminer si une User Story satisfait sa **Definition of Done (DoD)**.

---

## 2. MUST HAVE — Fonctionnalités indispensables

Les User Stories US-01 à US-08 correspondent aux exigences techniques du gabarit fourni.

| ID | User Story technique | Critères d'acceptation (DoD) | Séance cible |
|---|---|---|---|
| **US-01** | **Ingestion & Chunking structuré** — En tant que Data Engineer, je veux découper le corpus en chunks avec métadonnées pour permettre un indexage précis. | Script Python asynchrone avec gestion des erreurs ; métadonnées `doc_id`, `page_number`, `chunk_id`, `source` ; aucune perte d'information sur les tableaux. | S2 |
| **US-02** | **Indexation vectorielle HNSW** — En tant que système RAG, je veux insérer les vecteurs denses dans une base vectorielle pour accélérer la recherche sémantique. | Base démarrée via Docker Compose ; index HNSW avec distance Cosine ; temps d'insertion inférieur à 50 ms par batch de 64 chunks. | S2 |
| **US-03** | **Retrieval hybride & Reranking** — En tant que moteur de recherche, je veux fusionner les résultats denses et BM25 puis les reranker pour maximiser la pertinence. | Top-20 initial en recherche hybride ; Cross-Encoder produisant un Top-5 ; Recall@5 mesuré ≥ 80 %. | S3 |
| **US-04** | **API REST FastAPI & Pydantic v2** — En tant qu'application cliente, je veux interroger des endpoints typés et validés. | Schémas `QueryRequest` et `QueryResponse` ; rejet HTTP 422 des chaînes invalides ; documentation OpenAPI/Swagger. | S4 |
| **US-05** | **Génération en streaming SSE** — En tant qu'utilisateur, je veux recevoir progressivement une réponse accompagnée de citations. | Endpoint `/api/v1/chat/stream` ; événements SSE transmettant les sources et scores ; TTFT inférieur à 800 ms. | S4–S5 |
| **US-06** | **Interface web réactive** — En tant qu'utilisateur, je veux saisir une question, visualiser la réponse et consulter les sources. | Chat React/Angular avec états `idle`, `loading`, `error` ; affichage des chunks cités ; aucun rechargement de page. | S5 |
| **US-07** | **Assurance qualité & CI/CD** — En tant que Lead Developer, je veux exécuter automatiquement les tests et le linting. | Au moins 4 tests Pytest avec mocks ; Ruff ; GitHub Actions vert et contrôle des merges. | S6 |
| **US-08** | **Conteneurisation de production** — En tant qu'ingénieur DevOps, je veux déployer l'application avec Docker Compose. | Dockerfile multi-stage ; utilisateur non-root ; secrets injectés par variables d'environnement. | S7 |

### 2.1 État d'avancement des MUST HAVE

| ID | État actuel | Réalisations et éléments restants |
|---|---|---|
| **US-01** | Partiellement validée | Corpus ESCO nettoyé ; chunking 512/64 ; 3 314 chunks ; script d'ingestion asynchrone. Gestion des erreurs et correspondance complète des métadonnées à vérifier. Les tableaux ne font pas partie du corpus ESCO indexé actuellement. |
| **US-02** | Partiellement validée | Qdrant opérationnel ; Cosine ; 1 024 dimensions ; 3 314 points indexés. Le seuil d'insertion de 50 ms/batch n'est pas encore mesuré. |
| **US-03** | À réaliser | Dense Retrieval Top-K fonctionnel. BM25, fusion hybride, Cross-Encoder et Recall@5 restent à implémenter ou mesurer. |
| **US-04** | À réaliser | Backend FastAPI et schémas Pydantic non encore développés. |
| **US-05** | À réaliser | Génération LLM, citations et streaming SSE non encore intégrés. |
| **US-06** | À réaliser | Interface React non encore développée. |
| **US-07** | À réaliser | Dépôt GitHub créé ; pipeline CI/CD, tests Pytest et Ruff restent à configurer. |
| **US-08** | À réaliser | Docker Compose de développement fonctionnel ; conteneurisation complète de production non encore réalisée. |

**Bilan :** les fondations des US-01 et US-02 sont opérationnelles, mais leur DoD complet n'est pas encore démontré.

---

## 3. SHOULD HAVE — Forte valeur ajoutée industrielle

| ID | User Story technique | Critères d'acceptation | Séance cible | État |
|---|---|---|---|---|
| **US-09** | **Tracing MLOps distribué** — Tracer chaque étape de la chaîne RAG avec Langfuse ou OpenTelemetry. | Latence par étape : embedding, recherche, reranking, LLM ; suivi des tokens et du coût estimé. | S3–S4 | À réaliser |
| **US-10** | **Cache sémantique Redis** — Réutiliser les résultats de requêtes similaires pour réduire les coûts. | Similarité Cosine supérieure à 0,95 ; réponse depuis le cache en moins de 50 ms ; invalidation configurable. | S4 | À réaliser |
| **US-11** | **Évaluation continue Ragas** — Évaluer automatiquement les réponses générées. | Pipeline périodique mesurant Faithfulness et Answer Relevance. | S3 | À réaliser |

### Adaptation au projet

Le benchmark de chunking actuellement préparé constitue une première démarche d'évaluation expérimentale.

Cependant, il **ne remplace pas US-11**, car Hit@5 et MRR@5 évaluent le retrieval, tandis que Faithfulness et Answer Relevance évaluent les réponses produites par le système RAG.

---

## 4. COULD HAVE — Fonctionnalités complémentaires

| ID | User Story technique | Critères d'acceptation | État |
|---|---|---|---|
| **US-12** | Manifestes Kubernetes | Deployments, Services, ConfigMaps, Ingress et HPA. | À planifier |
| **US-13** | Routage agentique multi-outils | Routage automatique entre retrieval documentaire, SQL décisionnel et calculatrice. | Optionnel |
| **US-14** | Support multimodal | Ingestion et exploitation de tableaux complexes, images et schémas avec un modèle de vision. | Optionnel |

**Point de vigilance :** les manifests Kubernetes figurent dans les fonctionnalités COULD HAVE du gabarit, mais peuvent également être attendus dans les travaux de la séance 7. Leur priorité finale doit suivre les consignes effectivement données pour cette séance.

---

## 5. WON'T HAVE — Hors périmètre

Les fonctionnalités suivantes sont exclues de la première version :

- Entraînement complet d'un LLM de grande taille depuis zéro.
- Facturation SaaS avec Stripe et gestion complexe des abonnements.
- Application mobile native iOS ou Android.
- Candidature automatique aux offres d'emploi sans intervention de l'utilisateur.

L'objectif est de concentrer les ressources sur un prototype fonctionnel, explicable et évaluable.

---

## 6. Adaptation spécifique à PathForge AI

Les fonctionnalités suivantes complètent les exigences techniques générales du gabarit.

| ID | Priorité | User Story PathForge AI | Critère d'acceptation | Séance cible |
|---|---|---|---|---|
| **PF-01** | MUST | En tant qu'étudiant, je veux importer un CV et obtenir un profil structuré. | Profil JSON validé contenant formations, expériences et compétences avec provenance. | S3–S4 |
| **PF-02** | MUST | En tant qu'étudiant, je veux rechercher les métiers et compétences du référentiel ESCO. | Corpus indexé dans Qdrant ; recherche Top-K ; identification des sources. | S2–S5 |
| **PF-03** | MUST | En tant qu'étudiant, je veux comparer mon profil aux exigences d'un métier. | Compétences acquises, manquantes et preuves insuffisantes identifiées. | S3–S5 |
| **PF-04** | SHOULD | En tant qu'étudiant, je veux explorer les relations métier–compétence–formation. | Graphe Neo4j et démonstration d'une traversée multi-sauts. | S3–S5 |
| **PF-05** | SHOULD | En tant que responsable IA, je veux comparer et tracer les expériences. | Configurations, métriques et résultats reproductibles ; MLflow envisagé. | S3–S6 |
| **PF-06** | COULD | En tant que conseiller carrière, je veux exporter un plan de progression. | PDF contenant les recommandations et leurs sources. | Après MVP |
| **PF-07** | WON'T | En tant qu'utilisateur, je veux candidater automatiquement. | Fonction exclue de la V1. | — |

### Fonctionnalités métier complémentaires

Pour couvrir explicitement les trois modules de votre projet, nous ajoutons :

| ID | Priorité | User Story | Critère d'acceptation | Responsable |
|---|---|---|---|---|
| **PF-08** | MUST | Extraire les compétences et exigences des offres d'emploi. | Offres préparées et compétences normalisées avec références documentaires. | P2 |
| **PF-09** | MUST | Générer des recommandations professionnelles personnalisées. | Recommandations fondées sur le profil, les métiers et les compétences identifiées. | P3 |
| **PF-10** | MUST | Construire une Learning Roadmap personnalisée. | Étapes d'apprentissage ordonnées et justifiées par les compétences manquantes. | P3 |
| **PF-11** | MUST | Analyser les projets et stages comme preuves de compétences. | Extraction des compétences avec référence au projet ou à l'expérience concernée. | P1 |
| **PF-12** | SHOULD | Justifier les recommandations à l'aide des relations du graphe. | Chemin de relations explicite entre profil, compétence, métier et formation. | P2–P3 |

**Remarque :** PF-08 à PF-12 sont des ajouts propres à PathForge AI, proposés pour rendre les livrables métier plus explicites. Ils ne remplacent aucune User Story du gabarit initial.

---

## 7. Travaux réalisés — Séance 1

### Idéation et cadrage

- [x] Définition de la problématique.
- [x] Identification du persona principal.
- [x] Définition de la proposition de valeur.
- [x] Délimitation du MVP.
- [x] Priorisation MoSCoW.
- [x] Conception de l'architecture initiale.
- [x] Comparaison des bases vectorielles.
- [x] Choix de Qdrant.
- [x] Sélection du référentiel ESCO.
- [x] Création et publication du dépôt GitHub.

**Livrables :** fiche de cadrage, backlog MoSCoW, architecture initiale et dépôt GitHub.

---

## 8. Travaux réalisés — Séance 2

### Ingestion, chunking et base vectorielle

| Activité | Résultat | État |
|---|---|---|
| Exploration ESCO v1.2.1 | 3 043 lignes de métiers, 13 960 compétences et 126 051 relations identifiées | Réalisé |
| Nettoyage et déduplication | **3 039 métiers uniques** | Réalisé |
| Préparation documentaire | **3 039 documents métiers** | Réalisé |
| Token-based Chunking | **512 tokens / overlap 64** | Réalisé |
| Génération des chunks | **3 314 chunks** | Réalisé |
| Modèle d'embeddings | **BAAI/bge-m3 — 1 024 dimensions** | Réalisé |
| Docker Compose | Qdrant et PostgreSQL opérationnels | Réalisé |
| Indexation Qdrant | Collection `pathforge_esco` — **3 314 points** | Réalisé |
| Distance vectorielle | Cosine | Réalisé |
| Payloads | Métadonnées associées aux chunks | Réalisé |
| Recherche sémantique | Top-K avec affichage des scores | Réalisé |
| Filtrage | Recherche filtrée par métadonnées | Réalisé |
| Ingestion asynchrone | Script `scripts/ingest.py` implémenté | Partiellement validé |
| Benchmark | 10 questions avec métiers ESCO attendus | Préparé |
| Deuxième chunking | 256 tokens / overlap 32 | Indexation à confirmer |

### Exemple de recherche validée

**Question :**

*Which occupations require Python, SQL and data analysis skills?*

**Premier résultat observé :**

Data Analyst — Similarité Cosine : **0,6368**.

Cette recherche démontre le fonctionnement de la chaîne :

**Question → Embedding BGE-M3 → Qdrant → Top-K → Résultats ESCO**

Elle ne constitue pas encore une recommandation professionnelle personnalisée.

---

## 9. Benchmark de chunking — Travail en cours

### Objectif

Comparer deux configurations de chunking sur un même corpus ESCO.

| Configuration | Taille | Overlap | Collection |
|---|---:|---:|---|
| A | 512 tokens | 64 tokens | `pathforge_esco` |
| B | 256 tokens | 32 tokens | `pathforge_esco_256` |

### Jeu de test

**10 questions** associées à des identifiants de métiers ESCO attendus.

### Métriques

**Hit@5 :** proportion de questions pour lesquelles le métier attendu figure parmi les cinq premiers métiers distincts.

**MRR@5 :** mesure de la qualité du classement en tenant compte du rang du métier attendu.

**Latence :** temps nécessaire pour exécuter une recherche, dans des conditions comparables.

### Critères de validation

- Les deux collections sont correctement indexées.
- Les mêmes questions sont exécutées sur chaque collection.
- Les résultats sont regroupés par métier pour éviter de compter plusieurs chunks d'un même métier comme plusieurs métiers différents.
- Hit@5 et MRR@5 sont calculés.
- Un tableau comparatif présente les résultats.
- Une conclusion justifie le choix de configuration.

**État :** benchmark préparé ; résultats comparatifs non encore confirmés.

---

## 10. Répartition du backlog entre les trois personnes

| Personne | Module | User Stories principales | Livrable |
|---|---|---|---|
| **P1** | Profile Intelligence AI / RAG | PF-01, PF-11, contribution à US-01, US-03 et US-04 | Analyse de CV, extraction des compétences et API Profile Analysis |
| **P2** | Job & Career Intelligence AI / GraphRAG | PF-02, PF-04, PF-08, PF-12, contribution à US-01, US-02 et US-03 | Référentiel métiers, recherche, graphe et matching |
| **P3** | Career Copilot & Recommendation AI / LLM | PF-03, PF-09, PF-10, contribution à US-03, US-05 et US-11 | Assistant carrière, Skill Gap Analysis et Learning Roadmap |

### Responsabilités transversales

Les trois membres participent à :

- L'intégration des modules.
- La documentation.
- Les tests d'intégration.
- La gestion Git/GitHub.
- La préparation de la démonstration.
- La validation des livrables selon les consignes du professeur.

Les US-06, US-07 et US-08 nécessitent une attribution opérationnelle complémentaire lors de la planification des prochaines séances.

---

## 11. Planification des prochaines séances

| Séance | Objectif principal | Livrables attendus |
|---|---|---|
| **S2 — Finalisation** | Terminer le benchmark et vérifier les DoD d'ingestion/indexation | Comparaison des chunkings, métriques et preuves de fonctionnement |
| **S3** | Hybrid Retrieval et premiers liens GraphRAG | BM25, fusion RRF, Cross-Encoder, premiers tests Neo4j |
| **S4** | Backend et analyse de profils | FastAPI, Pydantic, CV Parsing, premiers endpoints |
| **S5** | Interface et recommandations | React, intégration RAG, Skill Gap Analysis, Learning Roadmap |
| **S6** | Évaluation, qualité et CI/CD | Pytest, Ruff, GitHub Actions, Ragas |
| **S7** | Intégration et livraison | Déploiement, tests finaux, démonstration et documentation |

Cette planification combine les séances cibles du gabarit avec les besoins spécifiques de PathForge AI. Elle reste à ajuster selon les consignes officielles de chaque séance.

---

## 12. Definition of Done — Règles de validation

Une User Story ne peut être considérée comme **terminée** que lorsque :

1. La fonctionnalité demandée est implémentée.
2. Les critères d'acceptation sont vérifiés.
3. Les résultats des tests sont disponibles.
4. Les erreurs principales sont traitées.
5. Le code est versionné dans Git.
6. La documentation nécessaire est mise à jour.
7. La fonctionnalité peut être démontrée.

### Application aux séances 1 et 2

**US-01 — Ingestion et chunking :**

Le corpus ESCO est préparé, découpé et indexé. Le script asynchrone est implémenté, mais certains critères de robustesse et de métadonnées restent à vérifier.

**US-02 — Indexation vectorielle :**

Qdrant est opérationnel avec 3 314 points. Le seuil de performance d'insertion demandé dans le gabarit n'est pas encore mesuré.

**PF-02 — Recherche ESCO :**

La recherche vectorielle est fonctionnelle. L'intégration à une réponse RAG avec citations reste à réaliser.

Ainsi, ces User Stories sont **avancées, mais pas entièrement clôturées selon leur DoD final**.

---

## 13. Risques et points de vigilance

| Risque | Conséquence | Mesure prévue |
|---|---|---|
| Temps d'embedding élevé sur CPU | Ingestion lente | Batching et reprise d'ingestion |
| Consommation mémoire | Instabilité locale | Surveillance RAM et réduction des lots |
| Mauvais choix de chunking | Baisse de pertinence | Benchmark 512/64 vs 256/32 |
| Données multi-sources hétérogènes | Difficultés de normalisation | Identifiants ESCO et schémas communs |
| Résultats non pertinents | Recommandations incorrectes | Hybrid Retrieval et reranking |
| Hallucinations du LLM | Conseils non justifiés | Citations, garde-fous et Ragas |
| Données personnelles des CV | Risque de confidentialité | Profils fictifs et contrôle des accès |
| Complexité GraphRAG | Retard d'intégration | Graphe limité aux relations essentielles du MVP |
| Retard sur les DoD | Livrables incomplets | Vérification à chaque séance |

---

## 14. Conclusion

Le backlog MoSCoW de PathForge AI distingue les exigences techniques indispensables, les améliorations de qualité et les fonctionnalités optionnelles.

Les séances 1 et 2 ont permis de construire un premier socle fonctionnel :

**ESCO → Preprocessing → Token-based Chunking → BGE-M3 → Qdrant → Semantic Search Top-K**

Les résultats déjà obtenus comprennent :

- **3 039 métiers ESCO uniques.**
- **3 314 chunks générés et indexés.**
- **Embeddings BGE-M3 de 1 024 dimensions.**
- **Recherche vectorielle Top-K opérationnelle.**
- **Ingestion asynchrone implémentée et reprise vérifiée sur collection complète.**
- **Benchmark de chunking préparé.**

Les prochaines étapes permettront d'enrichir cette base avec les profils étudiants, les offres d'emploi, BM25, Neo4j, le LLM et les recommandations personnalisées.

**Notre priorité est de transformer progressivement ce socle de recherche vectorielle en un système Hybrid RAG et GraphRAG complet, explicable et évalué, tout en respectant les critères d'acceptation du professeur.**
