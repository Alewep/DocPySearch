# Installer le projet
Ce guide explique comment configurer et exécuter le moteur de recherche basé sur des documents XML.

## Pré-requis
- Python 3.7.10 est recommandé pour ce projet.

## Étapes d'installation
1. **Créez un environnement virtuel**: Ceci est recommandé pour isoler les dépendances du projet.
    ```
    python3 -m venv venv
    ```
2. **Activez l'environnement virtuel**:
    ```
    source venv/bin/activate
    ```
3. **Installez les dépendances** requises à partir du fichier `requirements.txt`.
    ```
    pip install -r requirements.txt
    ```
4. **Lancez le projet**:
    ```
    python mvc.py
    ```

# Configuration du moteur
Un fichier `index.json` est disponible pour vous permettre de configurer les chemins utilisés par le moteur.
- `index_path`: chemin vers l'index (il est recommandé de ne pas le modifier).
- `folder_path`: chemin vers le dossier contenant les fichiers XML. Ce chemin peut également être modifié via l'interface utilisateur.

**Note**: Le moteur est uniquement compatible avec des fichiers XML bien formés. Utilisez le script `sgml_to_xml` pour convertir des fichiers SGML en XML si nécessaire.

# Fonctionnement du moteur

## Indexation
Les documents XML sont indexés à l'aide de la classe `Indexer` présente dans `indexer.py`. Cette classe est conçue de manière générique et peut potentiellement être utilisée pour indexer différents types de documents. Les fonctionnalités incluent:
- Création d'une posting list.
- Calcul du TF-IDF.
- Normalisation.
- Génération d'une stop-list basée sur la fréquence des documents.

Il existe une fonction nommée `index_xml()` dans `indexer.py` qui utilise la classe `Indexer` spécifiquement pour l'indexation de documents XML. Les balises XML sont ignorées pendant l'indexation.

## Requêtes
### Similarité cosinus avec normalisation
- Calcul de la similarité cosinus entre la requête et les documents.
- Classement des documents en fonction de la similarité.

### Minimisation de la proximité
Cette méthode considère que la pertinence d'un document augmente lorsque les termes de la requête sont plus proches les uns des autres dans le document.
- Sélection des documents avec la plus petite distance minimale entre les termes de la requête.

### Combinaison des deux méthodes
Cette approche fusionne les scores de similarité cosinus et de distance minimale pour obtenir un équilibre entre les deux critères.

### Correction automatique
Si une requête standard ne renvoie aucun résultat, le moteur déclenche une correction automatique qui tente de renvoyer des résultats pertinents malgré les erreurs potentielles dans la requête.

### Utilisation de caractères génériques (wildcards)
Le caractère `*` peut être utilisé entre les termes pour étendre la requête à toutes les extensions possibles du terme.

## Interface graphique
Le projet utilise la bibliothèque **tkinter** pour développer l'interface graphique, permettant une interaction facile avec le moteur de recherche.

# Remarques
Veillez à ce que les chemins dans `index.json` soient correctement configurés avant de démarrarrer le moteur. Assurez-vous également que tous les fichiers XML soient bien formés et placés dans le dossier spécifié par folder_path.


