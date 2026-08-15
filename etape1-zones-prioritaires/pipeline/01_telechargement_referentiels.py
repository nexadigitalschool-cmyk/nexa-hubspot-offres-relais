# -*- coding: utf-8 -*-
"""
ETAPE 1 / SCRIPT 1 - Telechargement des referentiels geographiques.

Produit les deux fichiers d'entree consommes par 02_bassins.py :
  - deco/package/data/communes.json  : referentiel Etalab (population INSEE, dept, region)
  - communes.json                    : referentiel La Poste (coordonnees GPS par code INSEE)

Sources :
  - @etalab/decoupage-administratif (npm) - Etalab / INSEE, population legale
  - high54/Communes-France-JSON (GitHub) - base officielle des codes postaux (La Poste)

Usage : python3 01_telechargement_referentiels.py
"""
import io
import json
import os
import tarfile
import urllib.request

NPM = "https://registry.npmjs.org/@etalab/decoupage-administratif"
LAPOSTE = "https://raw.githubusercontent.com/high54/Communes-France-JSON/master/france.json"


def get(url, binary=False):
    with urllib.request.urlopen(url, timeout=120) as r:
        data = r.read()
    return data if binary else json.loads(data)


def main():
    print("[1/2] Referentiel Etalab (population INSEE)...")
    meta = get(NPM)
    version = meta["dist-tags"]["latest"]
    tarball = meta["versions"][version]["dist"]["tarball"]
    print(f"      version {version}")
    with tarfile.open(fileobj=io.BytesIO(get(tarball, binary=True)), mode="r:gz") as tf:
        tf.extractall("deco")
    n = len(json.load(open("deco/package/data/communes.json")))
    print(f"      OK - {n} entrees")

    print("[2/2] Referentiel La Poste (coordonnees GPS)...")
    raw = get(LAPOSTE)
    json.dump(raw, open("communes.json", "w"), ensure_ascii=False)
    print(f"      OK - {len(raw)} entrees")

    with open("REFERENTIELS.txt", "w") as f:
        f.write(f"decoupage-administratif version={version} url={tarball}\n")
        f.write(f"laposte url={LAPOSTE}\n")
    print("\nTermine. Enchainer avec : python3 02_bassins.py")


if __name__ == "__main__":
    main()
