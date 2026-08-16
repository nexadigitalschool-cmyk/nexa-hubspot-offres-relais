# Débloquer un domaine dans une session Claude Code sur le web

Les sessions cloud passent par un proxy qui applique la politique réseau de
l'environnement. Un domaine hors politique renvoie `EGRESS_BLOCKED` (ou 403/407).
Ça ne se contourne pas depuis la session : ça se change dans la configuration de
l'environnement.

## Où

1. [claude.ai/code](https://claude.ai/code)
2. Au-dessus de la zone de message, l'**icône nuage** affichant le nom de
   l'environnement. Il n'y a ni page de réglages ni URL directe.
3. Survoler l'environnement → **icône engrenage**, ou **Add cloud environment**
   pour en créer un dédié.

## Niveaux de `Network access`

| Niveau | Sorties autorisées |
|---|---|
| **None** | aucune |
| **Trusted** | allowlist par défaut : registres de paquets, GitHub, SDK cloud |
| **Custom** | votre propre liste |
| **Full** | tout domaine |

## Domaines utiles pour ce dépôt

En **Custom**, un domaine par ligne dans `Allowed domains` :

```text
generativelanguage.googleapis.com
api.groq.com
api.openai.com
*.googlevideo.com
www.youtube.com
```

Cocher **« Also include default list of common package managers »** pour conserver
la liste Trusted — sinon npm, pip et le reste sautent.

`*.` couvre tous les sous-domaines. Le trafic GitHub passe par un proxy séparé et
reste disponible quel que soit le niveau.

## À savoir

- La configuration est lue au démarrage du conteneur : **il faut une nouvelle
  session** pour qu'un changement prenne effet.
- Chaque environnement a sa propre liste. Il n'existe pas d'allowlist poussée au
  niveau organisation.
- Instagram reste inexploitable même autorisé : les Reels sont derrière un mur de
  connexion.

## Diagnostic

```bash
curl -sS "$HTTPS_PROXY/__agentproxy/status"
cat /root/.ccr/README.md
```

Ne jamais désactiver la vérification TLS ni retirer `HTTPS_PROXY`.

Référence : [Configure cloud environments](https://code.claude.com/docs/en/cloud-environments)
