# Choix de la base vectorielle — PathForge AI

## 1. Contexte de la décision

PathForge AI est une plateforme intelligente d'orientation professionnelle destinée aux étudiants.

Elle vise à analyser les compétences documentées dans les CV, projets et expériences académiques, puis à les comparer aux exigences des métiers afin de proposer des recommandations personnalisées, explicables et sourcées.

Pour cela, la plateforme nécessite une **base vectorielle** capable d'indexer et de retrouver les informations pertinentes issues de plusieurs sources :

- Référentiel ESCO : métiers, compétences et relations.
- CV et profils étudiants.
- Projets et expériences académiques.
- Offres d'emploi historiques.

Les besoins techniques sont :

- Recherche sémantique par embeddings.
- Recherche hybride dense et lexicale.
- Filtrage par métadonnées.
- Récupération rapide des passages pertinents.
- Indexation de documents volumineux.
- Déploiement local avec Docker.
- Intégration avec Python et FastAPI.
- Compatibilité avec une future architecture GraphRAG.

Trois solutions ont été étudiées :

1. **Qdrant**
2. **Milvus**
3. **PostgreSQL avec pgvector**

## 2. Critères de comparaison

### 2.1 Recherche vectorielle

La base doit stocker des embeddings et permettre la recherche de vecteurs proches d'une requête.

Pour PathForge AI, les embeddings sont générés avec le modèle préentraîné **BAAI/bge-m3**, produisant des vecteurs denses de **1 024 dimensions**.

### 2.2 Recherche hybride

L'architecture cible prévoit la combinaison de deux méthodes :

- **Dense Retrieval** : recherche sémantique par embeddings.
- **Sparse / Lexical Retrieval** : recherche fondée sur les termes, notamment BM25.

Cette combinaison permettra de mieux traiter les requêtes contenant des compétences techniques précises, des intitulés de métiers ou des expressions sémantiquement proches.

À ce stade, seule la recherche dense est opérationnelle.

### 2.3 Filtrage par métadonnées

Les recherches doivent pouvoir être filtrées selon :

- La source documentaire.
- Le type de document.
- L'identifiant du métier.
- L'identifiant du profil étudiant.
- L'identifiant officiel ESCO.
- La catégorie ou le domaine professionnel.

Dans Qdrant, ces informations sont enregistrées sous forme de **payloads**.

### 2.4 Performance et évolutivité

La base doit assurer :

- Une latence de recherche raisonnable.
- Une indexation efficace.
- Une recherche Top-K pertinente.
- Une augmentation progressive du corpus.
- Une gestion des filtres sans complexité excessive.

### 2.5 Déploiement local

La solution doit fonctionner sur les machines de développement de l'équipe et être facilement reproductible avec Docker Compose.

## 3. Tableau comparatif

| Critère | Qdrant | Milvus | PostgreSQL + pgvector |
|---|---|---|---|
| Recherche vectorielle | Native | Native | Extension PostgreSQL |
| Index HNSW | Oui | Oui | Oui |
| Similarité Cosine | Oui | Oui | Oui |
| Filtrage des métadonnées | Payload filtering | Filtrage scalaire | SQL WHERE |
| Vecteurs denses | Oui | Oui | Oui |
| Recherche hybride | Dense + sparse | Fonctionnalités hybrides | Combinaison SQL, texte et vecteurs |
| Déploiement local | Simple avec Docker | Variable selon le mode | Simple si PostgreSQL est déjà disponible |
| Intégration Python | Client dédié | Client dédié | Bibliothèques PostgreSQL |
| Gestion des données relationnelles | Non spécialisée | Non spécialisée | Native |
| Complexité opérationnelle | Modérée | Variable | Faible à modérée |
| Adaptation au MVP PathForge AI | Très adaptée | Adaptée mais potentiellement plus lourde | Alternative pertinente |

Cette comparaison est qualitative. Elle ne constitue pas un benchmark expérimental des trois solutions.

## 4. Analyse des solutions

### 4.1 Qdrant

**Points forts :**

- Base spécialisée dans la recherche vectorielle.
- Support des vecteurs denses et sparse.
- Indexation HNSW.
- Similarité Cosine.
- Filtrage avancé des payloads.
- Client Python synchrone et asynchrone.
- Déploiement avec Docker Compose.
- Possibilité de conserver les données dans des volumes persistants.

**Limites :**

- Nécessite un service distinct de PostgreSQL.
- Synchronisation à prévoir entre les identifiants des documents, les profils et le futur graphe Neo4j.
- La recherche hybride et les mécanismes de fusion doivent être configurés et évalués.

### 4.2 Milvus

**Points forts :**

- Moteur spécialisé dans la recherche vectorielle.
- Plusieurs stratégies d'indexation.
- Fonctionnalités de recherche hybride.
- Possibilités de montée en charge.

**Limites :**

- Déploiement et exploitation potentiellement plus complexes selon la configuration.
- Certaines architectures peuvent être surdimensionnées pour notre MVP.

### 4.3 PostgreSQL avec pgvector

**Points forts :**

- Intégration directe à PostgreSQL.
- Stockage relationnel et vectoriel dans le même système.
- Requêtes SQL et filtrage avancé.
- Possibilité de combiner recherche textuelle PostgreSQL et recherche vectorielle.

**Limites :**

- Certaines stratégies hybrides nécessitent davantage d'assemblage applicatif.
- Les charges relationnelles et vectorielles partagent la même infrastructure.
- Des réglages spécifiques peuvent être nécessaires pour optimiser les performances.

## 5. Décision retenue

**Base vectorielle sélectionnée : Qdrant.**

Les raisons principales sont :

1. **Recherche sémantique native** adaptée aux embeddings BGE-M3.
2. **Index HNSW** pour accélérer la recherche approximative des plus proches voisins.
3. **Filtrage des payloads** pour distinguer les sources et les types de documents.
4. **Client Python asynchrone** adapté à notre pipeline d'ingestion.
5. **Déploiement local simple** avec Docker Compose.
6. **Évolution possible vers la recherche hybride**.
7. **Séparation des responsabilités** entre les différents systèmes de stockage.

Dans l'architecture cible :

- **Qdrant** : indexation vectorielle et recherche documentaire.
- **Neo4j** : relations entre étudiants, compétences, métiers et formations.
- **PostgreSQL** : données applicatives structurées et autorisées.

Neo4j et la logique métier PostgreSQL ne sont pas encore pleinement intégrés.

## 6. Validation locale de Qdrant — Séance 2

### 6.1 Environnement

Configuration utilisée dans le projet personnel :

| Élément | Configuration |
|---|---|
| Image Docker | `qdrant/qdrant:v1.9.0` |
| Port REST | 6333 |
| Stockage | Volume Docker persistant |
| Client Python | `qdrant-client==1.9.2` |
| Base relationnelle complémentaire | PostgreSQL 16 |
| Orchestration | Docker Compose |

Le port gRPC 6334 est un port standard de Qdrant ; son exposition sur l'hôte doit être vérifiée dans le fichier Docker Compose.

### 6.2 Démarrage des services

Depuis la racine du projet :

```powershell
docker compose up -d
```

Vérification :

```powershell
docker compose ps
```

Accès au tableau de bord :

http://localhost:6333/dashboard

Les services Qdrant et PostgreSQL ont été démarrés et vérifiés localement.

### 6.3 Préparation du corpus ESCO

Nous utilisons le référentiel **ESCO v1.2.1**.

Données sources :

- 3 043 lignes de métiers.
- 13 960 compétences.
- 126 051 relations métiers-compétences.

Après nettoyage et suppression des doublons, nous avons obtenu :

**3 039 documents métiers uniques.**

Chaque document est associé à son identifiant ESCO officiel et à ses informations métier-compétences.

### 6.4 Chunking

Les documents ont été découpés avec une stratégie **Token-based Chunking**.

Configuration principale :

| Paramètre | Valeur |
|---|---|
| Chunk size | 512 tokens |
| Chunk overlap | 64 tokens |
| Tokenizer | BGE-M3 |
| Nombre total de chunks | **3 314** |

Le chevauchement permet de préserver une partie du contexte entre deux chunks.

Cette configuration constitue une hypothèse technique initiale, et non une taille optimale déjà démontrée.

### 6.5 Génération des embeddings

Nous utilisons **BAAI/bge-m3**, un modèle préentraîné adapté à la recherche sémantique multilingue.

Configuration :

- Embeddings denses.
- Dimension vectorielle : **1 024**.
- Normalisation des vecteurs.
- Génération locale sur CPU.
- Traitement par lots.

Chaque chunk est transformé en un vecteur numérique qui représente son contenu sémantique.

### 6.6 Indexation dans Qdrant

Collection principale :

`pathforge_esco`

Caractéristiques :

| Paramètre | Valeur |
|---|---|
| Dimension | 1 024 |
| Distance | Cosine |
| Nombre de points | **3 314** |
| Métadonnées | Payloads |
| Persistance | Docker Volume |
| Recherche | Top-K vectoriel |

**Résultat vérifié : 3 314 points présents dans Qdrant pour 3 314 chunks attendus.**

Le nombre de points est supérieur au nombre de métiers parce qu'un document métier peut produire plusieurs chunks.

### 6.7 Ingestion asynchrone

Le script `scripts/ingest.py` utilise `AsyncQdrantClient`.

Il comprend :

- La lecture des documents préparés.
- La génération des chunks.
- La création d'identifiants stables.
- La vérification des points déjà présents.
- L'encodage des chunks manquants.
- L'indexation par lots de 64.
- La vérification du nombre final de points.
- Un mode `--dry-run`.

La reprise a été testée sur la collection déjà indexée.

**Résultat :**

- 3 314 points attendus.
- 3 314 points existants.
- Aucun point manquant.
- Aucune génération d'embeddings inutile.

La capacité de reprise a donc été vérifiée sur une collection complète. Une nouvelle insertion asynchrone de points manquants reste à tester pour valider ce scénario.

### 6.8 Recherche sémantique Top-5

Le script `scripts/search_test.py` permet de :

1. Recevoir une question utilisateur.
2. Générer son embedding avec BGE-M3.
3. Interroger Qdrant.
4. Récupérer les cinq meilleurs résultats.
5. Afficher leurs scores et métadonnées.
6. Appliquer un filtre par catégorie lorsque demandé.

**Exemple de requête :**

`Which occupations require Python, SQL and data analysis skills?`

Résultat observé :

- Premier métier : **Data Analyst**.
- Score de similarité : **0,6368**.

Ce résultat illustre la capacité de Qdrant à retrouver des métiers sémantiquement proches de la requête.

Il ne suffit toutefois pas à démontrer la qualité globale du moteur sur toutes les questions.

## 7. Benchmark de chunking — En préparation

Pour évaluer l'effet de la taille des chunks, nous comparons deux configurations.

| Configuration | Chunk size | Overlap | Collection |
|---|---:|---:|---|
| A | 512 | 64 | `pathforge_esco` |
| B | 256 | 32 | `pathforge_esco_256` |

Un ensemble de **10 questions** avec métiers ESCO attendus a été préparé.

### Métriques retenues

**Hit@5**

Indique la proportion de questions pour lesquelles le métier attendu apparaît parmi les cinq premiers métiers distincts.

**MRR@5**

Mesure la qualité du classement en tenant compte du rang du métier attendu, dans la limite des cinq premiers résultats.

**Latence**

Mesure le temps nécessaire pour exécuter une recherche, sous des conditions comparables.

### Objectif

Déterminer si la réduction de la taille des chunks améliore ou dégrade :

- La pertinence de la recherche.
- Le classement des métiers.
- La latence.
- Le nombre de vecteurs à stocker.

**État actuel :** le jeu de questions est préparé et la deuxième indexation a été lancée. Les résultats finaux ne sont pas encore confirmés.

Aucune conclusion sur la supériorité de 512 ou 256 tokens n'est annoncée à ce stade.

## 8. Benchmark comparatif Qdrant / Milvus / pgvector — Éventuel

Si les ressources et le calendrier le permettent, les trois solutions pourront être évaluées sur un corpus identique.

Critères envisagés :

- Latence moyenne.
- Latence P95.
- Recall@10.
- Impact des filtres de métadonnées.
- Consommation mémoire.
- Facilité de déploiement.
- Complexité opérationnelle.

Pour garantir une comparaison équitable, les tests devront utiliser les mêmes embeddings, le même corpus, des requêtes identiques et des conditions matérielles documentées.

**Aucun benchmark expérimental entre les trois bases n'a encore été réalisé.**

Ce benchmark est distinct du benchmark de chunking de la séance 2.

## 9. Limites et prochaines étapes

### Limites actuelles

- Seule la recherche dense est opérationnelle.
- BM25 et la fusion hybride ne sont pas encore intégrés.
- Le graphe Neo4j n'est pas encore construit.
- Les profils étudiants et les offres d'emploi ne sont pas encore indexés.
- La recherche vectorielle ne constitue pas encore un système RAG complet.
- Les recommandations personnalisées ne sont pas encore générées.
- Les performances n'ont pas encore fait l'objet d'un benchmark complet.

### Prochaines étapes

1. Finaliser le benchmark 512/64 contre 256/32.
2. Sélectionner une configuration sur la base des métriques.
3. Intégrer la recherche lexicale BM25.
4. Développer le Hybrid Retrieval.
5. Intégrer les profils étudiants et les offres d'emploi.
6. Construire les relations métiers-compétences dans Neo4j.
7. Combiner Vector Retrieval et Graph Retrieval.
8. Ajouter le reranking avec Cross-Encoder.
9. Évaluer la chaîne RAG avec Ragas et des métriques métier.

## 10. Conclusion

**Qdrant est la base vectorielle retenue pour PathForge AI.**

Ce choix repose sur ses fonctionnalités de recherche sémantique, son filtrage par métadonnées, son intégration Python et sa simplicité de déploiement local.

La séance 2 a permis de dépasser la simple installation du service en validant :

- Un corpus de **3 039 métiers uniques**.
- Un découpage en **3 314 chunks**.
- Des embeddings BGE-M3 de **1 024 dimensions**.
- Une collection Qdrant contenant **3 314 points**.
- Une recherche sémantique Top-K fonctionnelle.
- Un script d'ingestion asynchrone avec vérification de reprise.
- Un protocole de benchmark de chunking en préparation.

Qdrant constitue ainsi une **première brique technique fonctionnelle** de la future architecture Hybrid RAG et GraphRAG.

Son choix pourra être réévalué si les résultats expérimentaux ou les contraintes du projet le justifient.
