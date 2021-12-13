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
- prendre le documents qui à la plus petite distance minimale

### Fusion des deux méthodes
Nous fusionnons les deux score de cosinus et de distance pour parvenir à un équilibre entre les deux indiquateurs.
### Correction automatique
Le moteur l'orsque une requête classique retourne pas de résultats elle déclanche une demande de correction
gourmande qui permet de retourner des résultats malgé tout.
### wildcard
nous pouvons utilisé le caractère `*` entre les mots cela va permettre d'étendre la requêtes à tout les extension du mot
