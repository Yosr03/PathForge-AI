# Fiche d'Évaluation MLOps & Benchmark RAG — Séance 3
## Mesure Quantitative de la Qualité du Retrieval & de la Génération

---

### 1. Fiche d'Identité de l'Évaluation

- **Nom du Projet :** PathForge AI
- **Membres de l'Équipe :** À compléter
- **Date :** 24 novembre 2026
- **Modèle d'Embeddings (Bi-Encoder) :** BAAI/bge-m3
- **Modèle de Reranking (Cross-Encoder) :** cross-encoder/ms-marco-MiniLM-L-6-v2
- **LLM de génération :** Gemma2:2b via Ollama
- **LLM Évaluateur (Judge) :** Gemma2:2b
- **Framework d'évaluation :** Ragas 0.2.15
- **Corpus :** ESCO v1.2.1
- **Base vectorielle :** Qdrant
- **Collection :** pathforge_esco_256
- **Corpus indexé :** 5 182 chunks, 3 039 métiers
- **Dimensions :** 1024, distance Cosine
- **Golden Dataset :** 15 profils validés humainement
- **Environnement :** Windows, exécution CPU

---

### 2. Tableau Comparatif : Impact du Reranker sur le Retrieval

**Question de Test (P01) :**

I am a student skilled in Python, SQL, Power BI and data visualization. I completed an internship analyzing sales data and creating dashboards. Which occupation best matches my profile?

| Rang | Document / Chunk ID (Recherche Dense Seule) | Score Cosine | Document (Après Cross-Encoder) | Score Cross-Encoder |
| :-: | :--- | :-: | :--- | :-: |
| 1 | data analyst (chunk 0, cad0425a-f24c-5fef-be66-c506e448f799) | 0.574805 | data analyst | -4.180971 |
| 2 | database integrator (chunk 0, 7c435f26-57aa-558e-8437-40722ddedbb7) | 0.561626 | database developer | -5.577122 |
| 3 | business intelligence manager (chunk 1, 7dc6035d-3f6e-568d-a781-8495f44f1a62) | 0.557710 | computer vision engineer | -5.979271 |
| 4 | computer vision engineer (chunk 1, afe43048-4c32-56dd-bfad-f746385b72c4) | 0.549940 | big data archive librarian | -6.552771 |
| 5 | computer science lecturer (chunk 1, 221047a0-0a39-52ad-a8d1-a1a891772be6) | 0.544633 | database integrator | -6.622607 |

**Analyse qualitative :**

Pour P01, Data Analyst est premier en recherche dense,
quatrième après fusion RRF et premier après reranking.
Le Cross-Encoder corrige donc la dégradation introduite
par la fusion hybride sur cette question.
Les scores Cosine et Cross-Encoder ne sont pas
directement comparables et ne sont pas des probabilités.

Le tableau précédent concerne le moteur métier :
la recherche dense est dédupliquée par URI et le
reranking utilise une représentation du métier.

#### Comparaison sur les trois requêtes pièges — moteur métier

| Profil | Métier attendu | Dense | RRF | Cross-Encoder |
|---|---|---:|---:|---:|
| P01 | data analyst | 1 | 4 | 1 |
| P06 | data scientist | Hors Top-5 | Hors Top-5 | 2 |
| P08 | ICT business analyst | 2 | 1 | 3 |

#### Comparaison complémentaire au niveau des chunks

| Profil | Métier attendu | Rang RRF | Rang après reranking |
|---|---|---:|---:|
| P01 | data analyst | 1 | 1 |
| P06 | data scientist | 2 | 2 |
| P08 | ICT business analyst | 1 | 3 |

Le PoC chunk utilise les identifiants Qdrant réels.
Dense Top-20 et BM25 Top-20 sont exécutés en parallèle.
RRF (k=60) fusionne les candidats avant le reranking
des 20 meilleurs chunks et la sélection finale du Top-5.

Le classement reste stable pour P01 et P06,
mais se dégrade pour P08.
Le reranking ne garantit donc pas une amélioration systématique.


#### Cas de démonstration Flash-Audit — P02

**Question :**

I developed machine learning models using Python, PyTorch
and TensorFlow. My projects include predictive modeling
and intelligent systems. Which career suits my skills?

| Indicateur | Dense seule | Hybrid RAG + Cross-Encoder |
|---|---|---|
| Premier résultat | Electromechanical Engineer | Artificial Intelligence Engineer |
| Rang du métier attendu | 12 | 1 |

Le moteur chunk rétablit le métier attendu en première
position, avec un gain de 11 places.

Ce cas illustre la correction d'un échec de la recherche
vectorielle seule par le pipeline hybride avec reranking.

Il a été sélectionné rétrospectivement parmi les profils
du Golden Dataset. Il ne démontre pas une amélioration
systématique sur toutes les requêtes.

Preuve : `data/benchmark/flash_audit_case_p02.json`.

#### Benchmark métier sur 15 profils

| Métrique | Avant reranking | Après reranking |
|---|---:|---:|
| Hit@5 | 86,67 % | 100 % |
| MRR@5 | 0,6411 | 0,6389 |

La couverture progresse, mais le rang réciproque moyen
diminue légèrement. Les trois cas pièges ont été
sélectionnés rétrospectivement dans le benchmark.

---

### 3. Métriques d'Évaluation Ragas (Golden Dataset Benchmark)

| ID Question | Question Posée | Faithfulness (>= 0.85) | Answer Relevance (>= 0.80) | Context Recall (>= 0.80) | Latence E2E (ms) |
|---|---|---:|---:|---:|---:|
| P01 | I am a student skilled in Python, SQL, Power BI and data visualization. I completed an internship analyzing sales data and creating dashboards. Which occupation best matches my profile? | 1.0000 | 0.6191 | 1.0000 | 75947.47 |
| P06 | I use Python to build predictive models, apply statistical methods and evaluate machine learning algorithms. I also analyze datasets and communicate findings. Which occupation best matches my profile? | 1.0000 | 0.5590 | 1.0000 | 66353.95 |
| P13 | I assess cybersecurity risks, identify vulnerabilities and develop risk mitigation plans. I also work on security policies, compliance and risk reporting. Which occupation best matches my profile? | 1.0000 | 0.6660 | 1.0000 | 60323.97 |
| **MOYENNE** | **Score Global du Moteur** | **1.0000** | **0.6147** | **1.0000** | **67541.80** |

**Interprétation :**

- Faithfulness : objectif atteint.
- Answer Relevance : objectif non atteint.
- Context Recall : objectif atteint.
- Trois questions évaluées, neuf scores calculés.
- Les mesures concernent le moteur métier et le prompt V1.
- Les scores ne constituent pas une garantie générale
  d'absence d'hallucinations.
- Le moteur chunk n'a pas fait l'objet de cette évaluation Ragas.
- Le juge local est également le modèle de génération,
  ce qui limite l'indépendance de l'évaluation.

---

### 4. Décomposition Budgétaire de la Latence

| Étape Technique du Pipeline RAG | Latence Mesurée (ms) | Seuil SLA (ms) | Statut |
|---|---:|---:|---|
| 1. Encodage Bi-Encoder | 782.22 | < 30 | Hors SLA |
| 2. Recherche Dense Qdrant | 2103.34 | < 40 | Hors SLA |
| 3. Recherche Sparse BM25 | 69.30 | < 15 | Hors SLA |
| 4. Fusion RRF | 0.07 | < 5 | Validé |
| 5. Reranking Cross-Encoder | 1854.70 | < 150 | Hors SLA |
| 6. TTFT LLM | 27643.51 | < 600 | Hors SLA |
| **LATENCE TOTALE AVANT AFFICHAGE (estimée)** | 35606.61 | < 1000 | Hors SLA |

**Observations :**

- Retrieval parallèle moyen : 4 742 ms sur 15 profils.
- Retrieval séquentiel moyen : 5 856,44 ms.
- Gain observé : 19,03 %, avec classements identiques.
- Les deux benchmarks sont des exécutions distinctes ;
  le gain ne peut pas être attribué uniquement au parallélisme.
- Les temps dense et sparse ne doivent pas être additionnés
  directement puisqu'ils sont exécutés en parallèle.
- Le moteur métier récupère jusqu'à 300 chunks Qdrant
  puis conserve 20 métiers distincts.
- Le moteur chunk applique directement un Top-20.
- Qdrant ne présente actuellement aucun vecteur indexé HNSW.
- La latence Qdrant inclut les échanges avec le client.
- TTFT mesuré sur trois profils via streaming Ollama.
- La latence avant affichage est une estimation combinant
  retrieval historique et TTFT, pas une mesure intégrée.
- La génération complète et le TTFT sont deux métriques distinctes.
- Les durées d'évaluation Ragas sont exclues de la latence E2E.

---

### 5. Analyse des Échecs & Décisions MLOps

#### 5.1 Cas d'hallucination détecté

Aucune hallucination n'a été détectée par la métrique
Faithfulness sur les trois réponses V1 évaluées.
Ce résultat reste limité au corpus de test et au juge local.

La faiblesse principale est la pertinence des réponses :
Answer Relevance moyenne de 0,614685 pour une cible de 0,80.

Des variantes de prompt V2 et V3 ont été testées.
V2 a recommandé un métier incorrect sur P13.
V3 a amélioré la présence des citations mais a obtenu
une Answer Relevance moyenne de 0,600749.
Le prompt V1 a donc été restauré.

#### 5.2 Décisions d'architecture prises

- Utilisation de BGE-M3 pour les embeddings.
- Utilisation de BM25 pour la recherche lexicale.
- Fusion RRF avec k=60.
- Exécution parallèle des recherches dense et sparse.
- Conservation de 20 candidats avant reranking et de 5 après.
- Utilisation de MiniLM comme alternative légère au
  BAAI/bge-reranker-base indiqué dans la consigne.
  Cette adaptation reste à faire valider par l'enseignant.
- Conservation du moteur métier pour l'orientation professionnelle.
- Ajout d'un moteur chunk pour le PoC demandé.
- Conservation de Gemma2:2b pour une génération locale.
- Conservation du prompt V1 après comparaison expérimentale.
- Budget de contexte LLM : 4096 tokens.
- Budget maximal de génération : 180 tokens.
- Contexte transmis : cinq documents, tronqués à 1200
  caractères chacun.

#### 5.3 Limites et améliorations envisagées

- Réduire la latence du modèle de génération.
- Étudier l'accélération matérielle et la quantification.
- Examiner la configuration HNSW de Qdrant.
- Améliorer la pertinence directe des réponses.
- Évaluer davantage de profils avec un juge indépendant.
- Évaluer séparément le moteur chunk de bout en bout.
- Enrichir ultérieurement le corpus avec les offres d'emploi
  et les profils étudiants.

Ces améliorations sont envisagées, non encore validées.

#### 5.4 Traçabilité des résultats

- `data/benchmark_golden.json`
- `data/benchmark/ragas_summary_3_profiles.json`
- `data/benchmark/results_golden_retrieval_15.json`
- `data/benchmark/trap_cases_detailed.json`
- `data/benchmark/chunk_reranking_trap_cases.json`
- `data/benchmark/latency_detailed_parallel.json`
- `data/benchmark/latency_detailed_sequential.json`
- `data/benchmark/latency_summary.json`
- `data/benchmark/ttft_benchmark.json`
- `data/benchmark/ragas_answer_relevancy_v3.json`

**Conclusion :** Le pipeline RAG hybride est fonctionnel.
Les objectifs Faithfulness et Context Recall sont atteints
sur les trois profils évalués. Answer Relevance et la
majorité des objectifs de latence restent non conformes.
Les résultats constituent une base mesurée pour les
prochaines étapes du projet PathForge AI.
