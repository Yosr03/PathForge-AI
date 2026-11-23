# Répartition de l'équipe — PathForge AI

## Organisation des responsabilités, livrables et collaboration technique

**Projet :** PathForge AI — Plateforme intelligente d'orientation professionnelle par Hybrid RAG et GraphRAG

**Équipe :** 3 membres

**Dépôt GitHub principal :** https://github.com/Yosr03/PathForge-AI

**État d'avancement documenté :** Séances 1 et 2

---

## 1. Composition de l'équipe

Le projet PathForge AI est réalisé par trois membres, chacun responsable d'un module d'intelligence artificielle complémentaire.

| Membre | Rôle principal | Module |
|---|---|---|
| **Essaied Nour** | Lead Career Copilot & Recommendation AI | LLM, orchestration RAG/GraphRAG, analyse des écarts et recommandations |
| **Fourati Yosr** | Lead Job & Career Intelligence AI | Analyse des métiers et offres, recherche hybride, Neo4j et Graph Retrieval |
| **Trabelsi Nidhal** | Lead Profile Intelligence AI | CV Parsing, extraction LLM, Document RAG et analyse du profil |

Cette organisation vise une répartition équilibrée, permettant à chaque membre de contribuer au développement de composants IA, NLP, LLM et RAG.

Chaque membre est responsable de son module, de la préparation des données à la validation des résultats, en passant par les traitements et les API.

Les composants partagés, l'intégration et la démonstration finale relèvent de la responsabilité collective.

---

## 2. Responsabilités principales

### 2.1 Trabelsi Nidhal — Profile Intelligence AI

**Spécialité : LLM + Document RAG**

**Objectif :** comprendre le profil académique et professionnel de l'étudiant à partir de ses documents et expériences.

**Responsabilités :**

1. Développer le système de CV Parsing.
2. Extraire les informations issues des projets et des stages.
3. Utiliser un LLM pour identifier les compétences, expériences et formations.
4. Normaliser les compétences extraites à l'aide du référentiel ESCO.
5. Développer un Document RAG appliqué aux documents du profil.
6. Exploiter le moteur commun de recherche hybride Qdrant + BM25.
7. Analyser et structurer les compétences de l'étudiant.
8. Distinguer les compétences déclarées des compétences documentées.
9. Conserver les preuves et références associées aux compétences.
10. Développer l'API Profile Analysis avec FastAPI.
11. Contribuer à l'interface React de consultation du profil.
12. Évaluer la qualité de l'extraction et de la structuration.

**Datasets principaux :**

- CV fictifs ou autorisés.
- Descriptions de projets académiques.
- Expériences de stages.
- Référentiel ESCO pour la normalisation.

**Technologies envisagées :**

Python, LLM, Document RAG, Qdrant, BM25, FastAPI, Pydantic et React.

**Livrable attendu :**

Un module permettant à l'étudiant d'importer son CV et ses expériences afin d'obtenir un profil structuré, contenant ses compétences, formations, expériences et preuves documentaires.

**Contrat de sortie :** `StudentProfile`

**État actuel :** module fonctionnel à développer. Le pipeline ESCO–Qdrant déjà réalisé constitue un socle réutilisable pour la normalisation et la recherche.

---

### 2.2 Fourati Yosr — Job & Career Intelligence AI

**Spécialité : LLM + Hybrid RAG + GraphRAG**

**Objectif :** comprendre les métiers, les offres d'emploi et les relations entre compétences et exigences professionnelles.

**Responsabilités :**

1. Préparer et valider le référentiel ESCO.
2. Préparer un corpus d'offres d'emploi historiques, notamment LinkedIn Job Postings si sa source et ses conditions de réutilisation sont validées.
3. Analyser les Job Descriptions avec un LLM.
4. Extraire les compétences et qualifications requises.
5. Normaliser les compétences professionnelles avec ESCO.
6. Construire un Knowledge Graph avec Neo4j.
7. Développer les relations entre métiers, compétences et offres.
8. Implémenter le Graph Retrieval avec Cypher.
9. Développer le moteur commun de recherche hybride Qdrant + BM25.
10. Effectuer la recherche et la récupération des offres pertinentes.
11. Comparer les exigences des métiers aux informations structurées du profil étudiant.
12. Développer l'API Job & Career Intelligence.
13. Évaluer la pertinence du retrieval.

**Datasets principaux :**

- ESCO v1.2.1 — Occupations.
- ESCO v1.2.1 — Skills.
- ESCO v1.2.1 — Occupation–Skill Relations.
- Corpus LinkedIn Job Postings ou autre source d'offres autorisée.

**Technologies envisagées :**

Python, BGE-M3, Qdrant, BM25, LLM, Neo4j, Cypher, GraphRAG et FastAPI.

**Livrable attendu :**

Un moteur intelligent permettant d'identifier les métiers pertinents, leurs compétences essentielles et optionnelles, ainsi que les relations documentaires et graphiques justifiant les correspondances.

**Contrat de sortie :** `JobRequirements`

#### Travaux déjà réalisés sur le socle Job & Career Intelligence

| Activité | Résultat |
|---|---|
| Exploration ESCO | 3 043 lignes de métiers, 13 960 compétences et 126 051 relations |
| Nettoyage et déduplication | **3 039 métiers uniques** |
| Préparation documentaire | **3 039 documents métiers** |
| Token-based Chunking | **512 tokens, overlap 64** |
| Génération des chunks | **3 314 chunks** |
| Embeddings | **BAAI/bge-m3 — 1 024 dimensions** |
| Base vectorielle | **Qdrant — Cosine** |
| Indexation | **3 314 points dans `pathforge_esco`** |
| Métadonnées | Payloads associés aux chunks |
| Recherche | Top-K sémantique avec filtres |
| Ingestion asynchrone | Script implémenté, reprise vérifiée sur collection complète |
| Benchmark | 10 questions préparées ; comparaison 512/64 et 256/32 en cours |

Ces réalisations constituent le **socle technique commun**, développé dans le cadre des premières séances. Elles sont principalement rattachées au domaine Job & Career Intelligence, sans exclure la contribution des autres membres.

**À réaliser :** intégration des offres d'emploi, BM25, fusion hybride, construction du graphe Neo4j, Graph Retrieval, matching et API métier.

---

### 2.3 Essaied Nour — Career Copilot & Recommendation AI

**Spécialité : LLM + RAG Orchestration + Recommendation**

**Objectif :** transformer les informations du profil étudiant et les exigences professionnelles en recommandations personnalisées et explicables.

**Responsabilités :**

1. Développer le Career Assistant basé sur un LLM.
2. Orchestrer les modules Profile Intelligence et Job & Career Intelligence.
3. Intégrer les résultats du Hybrid RAG et du Graph Retrieval.
4. Construire le contexte transmis au LLM.
5. Développer le Skill Gap Analysis.
6. Identifier les compétences acquises, manquantes ou insuffisamment documentées.
7. Recommander les métiers adaptés au profil.
8. Générer des Personalized Learning Roadmaps.
9. Intégrer le reranking avec Cross-Encoder.
10. Générer des recommandations accompagnées de sources.
11. Évaluer la qualité des réponses avec Ragas.
12. Développer l'API Career Copilot.
13. Coordonner l'intégration des réponses entre les modules.

**Données principales :**

- `StudentProfile` fourni par le module Profile Intelligence.
- `JobRequirements` fourni par le module Job & Career Intelligence.
- Résultats documentaires et graphiques.
- Références de formations et certifications, si disponibles.

**Technologies envisagées :**

Python, LLM, RAG Orchestration, GraphRAG, Cross-Encoder, Ragas, FastAPI et PostgreSQL.

**Livrable attendu :**

Un assistant intelligent capable de recommander des métiers, d'expliquer les écarts entre les compétences acquises et les exigences professionnelles, puis de générer un parcours de progression personnalisé.

**Contrat de sortie :** `CareerRecommendation`

**État actuel :** module à développer. Il réutilisera les mécanismes de retrieval et les données structurées produits par les deux autres modules.

---

## 3. Architecture globale et collaboration

Les trois modules sont complémentaires.

### Entrées utilisateur

- CV.
- Projets académiques.
- Expériences de stage.
- Compétences déclarées.
- Objectif professionnel, si renseigné.

### Module 1 — Profile Intelligence AI

**Responsable : Trabelsi Nidhal**

CV + Projets + Stages

↓

CV Parsing et extraction LLM

↓

Normalisation des compétences avec ESCO

↓

Document RAG et identification des preuves

↓

**`StudentProfile`**

### Module 2 — Job & Career Intelligence AI

**Responsable : Fourati Yosr**

ESCO + Offres d'emploi

↓

Préparation et analyse des données

↓

Extraction et normalisation des compétences requises

↓

Hybrid Retrieval : Qdrant + BM25

↓

Graph Retrieval : Neo4j + Cypher

↓

**`JobRequirements`**

### Module 3 — Career Copilot & Recommendation AI

**Responsable : Essaied Nour**

`StudentProfile` + `JobRequirements`

↓

Orchestration RAG et Graph Retrieval

↓

Reranking

↓

Comparaison des compétences

↓

Skill Gap Analysis

↓

Génération LLM avec sources

↓

**`CareerRecommendation`**

### Résultat final

**Personalized Career Roadmap**

La plateforme devra permettre à l'étudiant de :

1. Comprendre ses compétences documentées.
2. Identifier des métiers potentiellement adaptés.
3. Comparer son profil aux exigences professionnelles.
4. Repérer les compétences manquantes.
5. Obtenir des recommandations personnalisées.
6. Suivre un parcours de progression structuré.
7. Consulter les sources justifiant les recommandations.

Cette architecture représente le fonctionnement cible du système complet.

---

## 4. Matrice des responsabilités techniques

| Composant | Trabelsi Nidhal | Fourati Yosr | Essaied Nour |
|---|---|---|---|
| **Module principal** | Profile Intelligence | Job & Career Intelligence | Career Copilot |
| **LLM** | CV et extraction de compétences | Analyse des offres et exigences | Recommandations |
| **RAG** | Document RAG | Hybrid Retrieval + Graph Retrieval | Orchestration RAG/GraphRAG |
| **Qdrant** | Utilisation du moteur commun | Développement du retrieval métier | Consommation des résultats |
| **BM25** | Recherche dans les profils | Moteur hybride commun | Exploitation des résultats |
| **Neo4j** | Références aux compétences | Construction et requêtes du graphe | Exploitation des relations |
| **FastAPI** | Profile API | Job API | Copilot API |
| **React** | Interface du profil | Interface de recherche métier | Chatbot et Roadmap |
| **Évaluation** | Qualité de l'extraction | Qualité du retrieval | Qualité des réponses |
| **Datasets** | CV, projets, stages | ESCO, offres d'emploi | Données structurées des modules |
| **Sortie** | `StudentProfile` | `JobRequirements` | `CareerRecommendation` |

### Principe d'architecture

Le moteur de recherche hybride sera développé comme un **composant partagé**, afin d'éviter de dupliquer :

- Les modèles d'embeddings.
- Les connexions Qdrant.
- La recherche BM25.
- Les mécanismes de fusion.
- Les fonctions communes de retrieval.

Chaque membre pourra utiliser ce moteur à travers des interfaces définies collectivement.

---

## 5. Contrats de communication entre modules

Pour permettre le développement parallèle, les trois modules doivent échanger des données structurées.

### Contrat 1 — StudentProfile

Produit par : **Trabelsi Nidhal**

Contenu attendu :

- Identifiant du profil.
- Formations.
- Expériences.
- Projets.
- Compétences extraites.
- Références documentaires.
- Niveau de confiance ou preuve disponible, lorsque justifiable.

### Contrat 2 — JobRequirements

Produit par : **Fourati Yosr**

Contenu attendu :

- Identifiant ESCO du métier.
- Intitulé du métier.
- Compétences essentielles.
- Compétences optionnelles.
- Exigences issues des offres.
- Références des documents.
- Relations du graphe, lorsqu'elles seront disponibles.

### Contrat 3 — CareerRecommendation

Produit par : **Essaied Nour**

Contenu attendu :

- Métiers recommandés.
- Compétences déjà documentées.
- Compétences manquantes.
- Justifications des correspondances.
- Recommandations de progression.
- Learning Roadmap.
- Sources utilisées.

Les schémas définitifs seront formalisés avec **Pydantic v2** avant l'intégration des API.

---

## 6. Responsabilités transversales

| Activité | Organisation |
|---|---|
| Architecture générale | Travail commun |
| Choix des modèles | Décision commune |
| Schémas JSON et Pydantic | Définition commune |
| Moteur de recherche partagé | Développement coordonné, pilotage Job & Career Intelligence |
| Backend FastAPI | Chaque membre développe les endpoints de son module |
| Frontend React | Chaque membre contribue aux écrans de son module |
| Intégration des modules | Coordination par Essaied Nour |
| Docker Compose | Travail commun |
| PostgreSQL | Intégration applicative coordonnée |
| GitHub Actions / CI/CD | Travail commun |
| Tests d'intégration | Travail commun |
| Documentation | Chaque membre documente son module |
| Démonstration et soutenance | Travail commun |

La répartition des responsabilités techniques ne dispense aucun membre de comprendre l'architecture globale.

---

## 7. Planning de développement

Le planning est organisé selon les sept séances du projet fédérateur.

| Séance | Objectif | Responsabilités principales |
|---|---|---|
| **S1** | Idéation, problématique, architecture, MoSCoW, MVP | Toute l'équipe |
| **S2** | Ingestion ESCO, chunking, embeddings, Qdrant, Top-K | Socle commun, principalement Job & Career Intelligence |
| **S3** | Hybrid Retrieval, BM25, reranking et premiers travaux GraphRAG | P2 avec participation de P1 et P3 |
| **S4** | CV Parsing, APIs FastAPI, profils structurés et orchestration | P1, P2 et P3 selon leurs modules |
| **S5** | Interface React, intégration, Skill Gap Analysis et recommandations | P3 avec P1 et P2 |
| **S6** | Évaluation, tests, qualité, Ragas et CI/CD | Toute l'équipe |
| **S7** | Déploiement, validation finale, documentation et démonstration | Toute l'équipe |

Ce planning est prévisionnel et devra être ajusté aux consignes officielles des prochaines séances.

### Avancement réel

**Séance 1 :** cadrage, architecture, backlog et dépôt GitHub réalisés.

**Séance 2 :** pipeline ESCO–BGE-M3–Qdrant et recherche Top-K opérationnels. Benchmark comparatif en cours.

Les modules de CV Parsing, GraphRAG et Career Copilot ne sont pas encore finalisés.

---

## 8. Organisation GitHub

### Dépôt de référence

https://github.com/Yosr03/PathForge-AI

**Branche principale :** `main`

### Branches proposées

- `feature/profile-intelligence-*`
- `feature/job-intelligence-*`
- `feature/career-copilot-*`
- `feature/integration-*`

### Workflow de collaboration proposé

1. Créer une issue pour chaque tâche.
2. Développer dans une branche dédiée.
3. Exécuter les tests.
4. Ouvrir une Pull Request.
5. Effectuer une revue de code croisée.
6. Fusionner après validation.
7. Mettre à jour la documentation.

**État actuel :** le dépôt personnel et la branche `main` existent. Les branches de fonctionnalités et le workflow collectif sont proposés, mais leur mise en place n'est pas encore confirmée.

Le dépôt personnel ne doit pas être présenté comme un dépôt partagé par les trois membres tant que les accès et les règles de collaboration n'ont pas été configurés.

---

## 9. Règles de collaboration

Pour garantir la cohérence technique du projet :

1. Définir les schémas JSON et les contrats API avant l'intégration.
2. Utiliser des conventions de nommage communes.
3. Centraliser les composants de recherche partagés.
4. Préserver les identifiants officiels ESCO.
5. Conserver la provenance des compétences et des recommandations.
6. Documenter les API et les décisions techniques.
7. Tester chaque module séparément.
8. Effectuer régulièrement des tests d'intégration.
9. Partager les résultats des benchmarks.
10. Ne jamais publier de secrets ou de CV personnels non autorisés.
11. Utiliser Git et les Pull Requests pour les modifications collaboratives.
12. Vérifier les critères d'acceptation avant chaque démonstration.

---

## 10. Livrables attendus par personne

| Responsable | Livrable principal | Exemple de résultat |
|---|---|---|
| **Trabelsi Nidhal** | Profile Intelligence AI | Profil étudiant structuré avec compétences, expériences et preuves |
| **Fourati Yosr** | Job & Career Intelligence AI | Métiers compatibles, compétences exigées et relations justifiées |
| **Essaied Nour** | Career Copilot & Recommendation AI | Skill Gap Analysis, recommandations et Learning Roadmap |

### Livrable collectif

Une plateforme web PathForge AI intégrant les trois modules dans une expérience utilisateur cohérente.

**Chaîne fonctionnelle cible :**

CV étudiant

↓

Extraction des compétences

↓

Recherche des métiers et exigences

↓

Analyse des écarts

↓

Recommandations personnalisées

↓

Parcours d'apprentissage

---

## 11. Points de vigilance

### 11.1 Dépendances entre modules

Le Career Copilot dépend des sorties `StudentProfile` et `JobRequirements`.

Les schémas de données devront donc être définis suffisamment tôt pour permettre le développement parallèle.

### 11.2 Équilibre de la charge de travail

Le module Job & Career Intelligence comporte plusieurs composants techniques importants : ESCO, ingestion, recherche hybride, Neo4j et analyse des offres.

Le module Profile Intelligence comporte également des défis liés à l'extraction fiable des informations et à la traçabilité des compétences.

Le module Career Copilot doit assurer l'orchestration, la qualité des recommandations et leur évaluation.

L'équilibre sera évalué en fonction du temps de développement et des difficultés réelles, et non uniquement du nombre de tâches.

### 11.3 Mutualisation des composants

Les outils communs, notamment Qdrant, BGE-M3, BM25, Docker Compose et les contrats Pydantic, doivent être réutilisés entre les modules.

### 11.4 Validation progressive

Chaque module devra fournir :

- Un code exécutable.
- Des tests.
- Une documentation.
- Une API ou interface définie.
- Un résultat démontrable.
- Des références aux données utilisées.

---

## 12. Conclusion

PathForge AI repose sur trois axes complémentaires :

| Axe | Module | Responsable |
|---|---|---|
| **Comprendre le candidat** | Profile Intelligence AI | Trabelsi Nidhal |
| **Analyser le marché** | Job & Career Intelligence AI | Fourati Yosr |
| **Recommander un parcours** | Career Copilot & Recommendation AI | Essaied Nour |

Les travaux des séances 1 et 2 ont permis de définir l'architecture et de développer un premier pipeline de recherche vectorielle sur ESCO.

Ce socle sera progressivement enrichi par l'analyse des profils, les offres d'emploi, le Hybrid RAG, le GraphRAG et la génération de recommandations.

**PathForge AI : Analyser → Comparer → Recommander → Progresser.**
