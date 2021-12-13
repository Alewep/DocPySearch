# Installer le projet 
### Créer un environnement virtuel python et excuter 
- Ce projet à été écrit en python 3.7.10
- Créer un environnement virtuel avec **venv** nommé "venv"  
`python3 -m venv venv`
- Démarrer l'environnement virtuel "venv"  
`source venv/bin/activate`
- Installer les modules python avec le fichier _requirement_.txt  
`pip install -r requirements.txt`
- Démarrer le projet `python mvc.py`


# Configurer le moteur 
Vous avez à disposition un fichier index.json qui permet d'éditer les 
chemins :
- le chemin de l'index `index_path` (recommandé de ne pas changer)
- le chemin du dossier `folder_path`  qui contient les divers fichier (peut être aussi changer depuis l'interface)

Le moteur permet d'analyser uniquement des fichier XML bienformé !
Vous pouver convertir un ensemble de fichiers au format SGML en XML
avec le script *sgml_to_xml*

# Fonctionnement du moteur
##
## Indexation
les différents documents au format xml sont indexé à l'aide 
de la classe **Indexer** dans *indexer.py* qui à été conçu pour géneraliser l'indexation.
Nous pourrions à l'avenir utilisé cette classe pour indexer tout type de document.
Cette classe permet de faire beaucoup de choses :
- Creer une posting list 
- Calculer le tf-idf
- Calculer la normalisation
- Calculer une stop list à partir d'un seuil en fonction de la document frequency pour chaque mots


une fonction qui implémente cette classe pour notre format  (ici xml ) dans *indexer.py* nommé **index_xml()**
Nous avons fait ici le choix d'ignorer les balises XML est de ne pas les inclures dans l'indexation.
## Requête
### Requête de cosinus avec normalisation
- Calculer le cosinus entre la entre la rêquete et les documents
- Trier les documents en fonction d'un score donné 

### Minimiser la proximité
Pour la pertinance des rêquetes nous considerons que plus les mots sont proches entre eux dans le documents 
plus il est pertinant.
- prendre le documents qui à la plus petite distance entre les mots minimale

### Fusion des deux méthodes
Nous fusionnons les deux score de cosinus et de distance pour parvenir à un équilibre entre les deux indiquateurs.
### Correction automatique
Le moteur l'orsque une requête classique retourne pas de résultats elle déclanche une demande de correction
gourmande qui permet de retourner des résultats malgé tout.
### wildcard
nous pouvons utilisé le caractère `*` entre les mots cela va permettre d'étendre la requête à toutes les extension du mot
### Interface Graphique
Nous utilisons la librairie **tkinter** pour dévelloper l'ensemble de l'inteface graphique


