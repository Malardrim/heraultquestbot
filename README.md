<h1 align="center">HeraultQuestBot</h1>
<p align="center">
<a href="https://pypi.org/project/hikari"><img height="20" alt="Supported python versions" src="https://img.shields.io/pypi/pyversions/hikari"></a>
</p>

Un bot pour aider a organiser les sessions wargame de l'association HéraultQuest

### Inviter le bot sur son discord
Pour inviter le bot sur votre discord suivez ce <a href="https://discord.com/api/oauth2/authorize?client_id=1015619039827087400&permissions=17179946048&scope=bot" target="_blank">lien</a><br>
Pour inviter le bot sur le serveur en mode admin (que pour les tests), veuillez suivre ce <a href="https://discord.com/api/oauth2/authorize?client_id=1015619039827087400&permissions=8&scope=bot" target="_blank">lien</a>

## Commandes
----
### Inscription
S'inscrire à une session dans le channel organisation<br>
Cette commande ne peut être lancée que dans le channel des inscriptions definis à l'avance

```
/inscription
```
```
    session: date de la session a laquelle il faut s'inscrire, une liste vous est proposée (ex: 09/09/2022)
```
```
    participants: Indique les tags des participants pour la partie (ex: @Malardrim ...)
```
```
    game_size: Indique la taille de la partie (2000pts, 1k pts)
```
```
    game_type: Type de jeu, une liste vous est proposée, il faut prendre une des options (1v1, FFA ...)
```
```
    game_system: Système de jeu, une liste vous est proposée, il faut prendre une des options (AoS, 40k ...)
```
```
    table (optionel): Table à laquelle on souhaite s'inscrire (si cette option est pas mise on inscrit sur la 1ere table dispo) (ex: 1,2)
```
----
### Desincription
Se desinscrire d'une session dans le channel organisation, seuls les inscrits peuvent desinscrire la table<br>
Cette commande ne peut être lancée que dans le channel des inscriptions definis à l'avance

```
/unsubscribe_session
```
```
    session: date de la session a laquelle il faut s'inscrire, une liste vous est proposée
```
```
    table: Table à laquelle on souhaite se desinscrire
```
----
### Configuration  ```Organisateurs```
Configure les salons textuels utilisés pour les inscriptions et l'organisation
```
/config
```
```
    channel_organisation: salon dans lequel seront postées les annonces de session
```
```
    channel_inscriptions: salon acceptant les inscriptions
```
----
### Création de session ```Organisateurs```
Crée une session dans le channel organisation
```
/create_session
```
```
    date: date de la session (ex: 09/09/2022)
```
```
    hour: heure de début de la session (affichage seulement)
```
```
    tables: nombre de tables dans la session
```
----
### Ajout d'une table a une session ```Organisateurs```
Ajoute une table a une session existante
```
/add_table_session
```
```
    session: date de la session a laquelle il faut s'inscrire, une liste vous est proposée
```
```
    table: nom de la table a ajouter
```
----
### Suppression d'une table a une session ```Organisateurs```
Supprime une table d'une session existante
```
/add_table_session
```
```
    session: date de la session a laquelle il faut s'inscrire, une liste vous est proposée
```
```
    table: nom de la table a supprimmer
```
----