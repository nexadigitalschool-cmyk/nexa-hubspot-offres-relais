# 02 — Les 59 bassins d'opportunité candidats

**Unité = bassin d'activation IE** (ville-centre + rayon 30 km), disjoint des autres, construit
algorithmiquement à partir de la population INSEE. Les frontières administratives ne sont pas
contraignantes : plusieurs bassins sont interdépartementaux.

## Comment lire ce tableau

| Colonne | Nature | Lecture |
|---|---|---|
| **Vivier B1 (Tle est.)** | **PROXY** | population × 1,05 % — ordre de grandeur, pas un effectif réel |
| **Affinité** | **ESTIMATION EXPERTE** | moyenne des 4 filières, sur 100 — **pas une donnée DEPP** |
| **Cyber / Dev / Data/IA / Mkt** | **ESTIMATION EXPERTE** | ••••• = 5/5, ····· = 1/5 |
| **Concentration** | **OBSERVÉ** | 0–100 : densité à 20 km + compacité + nombre de villes ≥ 10 000 hab. |
| **Éco. num.** | **ESTIMATION EXPERTE** | ancrée sur labels French Tech et grands employeurs |
| **Score** | calculé | 0,40 vivier + 0,25 affinité + 0,20 concentration + 0,15 économie |

Priorités : **P1** = 12 premières · **P2** = rangs 13–30 · **P3/TEST** = rangs 31–59.
Le rang P3 ne signifie pas « sans intérêt » : plusieurs zones expérimentales décisives y figurent —
Valence, Troyes et Dunkerque–Calais sont P3 et pourtant recommandées au portefeuille de test.

## Tableau de synthèse

| # | Zone / bassin | Prio | Région(s) | Départements | Villes principales | Vivier B1 (Tle est.) | Affinité | Cyber | Dev | Data/IA | Mkt | Concentration | Éco. num. | Score | Filières dominantes | Pourquoi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Marseille** | P1 | Provence-Alpes-Côte d'Azur | 13 | Marseille, Aix-en-Provence, Martigues | ~18 520 | 94/100 | ••••• | ••••• | ••••• | ••••· | 60/100 | ••••• | **90.4** | Cyber+Dev+Data/IA | 2e ville de France ; 4e hub internet europeen (cables sous-marins, data centers), CMA CGM, STMicroelectronics Rousset, Airbus Helicopters ; Aix-Marseille Universite |
| 2 | **Toulouse** | P1 | Occitanie | 31, 32, 81 | Toulouse, Colomiers, Tournefeuille | ~13 900 | 94/100 | ••••• | ••••• | ••••• | ••••· | 81/100 | ••••• | **86.3** | Cyber+Dev+Data/IA | Aeronautique-spatial (Airbus, Thales, CNES), 1er bassin d'emploi ingenieur hors IDF |
| 3 | **Bordeaux** | P1 | Nouvelle-Aquitaine | 33 | Bordeaux, Mérignac, Pessac | ~12 650 | 88/100 | ••••· | ••••• | ••••· | ••••• | 74/100 | ••••• | **80.9** | Dev+Marketing | Capitale French Tech ; Cdiscount, Ubisoft, aeronautique-defense-spatial (Dassault, Thales, ArianeGroup) ; vin et tourisme = fort vivier marketing |
| 4 | **Nantes** | P1 | Pays de la Loire | 44, 85 | Nantes, Saint-Herblain, Rezé | ~10 390 | 88/100 | ••••· | ••••• | ••••· | ••••• | 78/100 | ••••• | **76.9** | Dev+Marketing | Capitale French Tech, Atlanpole et quartier de la creation ; Airbus, forte densite d'ESN ; premier ecosysteme numerique de l'Ouest |
| 5 | **Nice** | P1 | Provence-Alpes-Côte d'Azur | 06, 83 | Nice, Antibes, Cannes | ~11 480 | 88/100 | ••••• | ••••• | ••••· | ••••· | 58/100 | ••••• | **75.3** | Cyber+Dev | Sophia Antipolis, 1er technopole europeen ; Amadeus, Orange Labs ; economie touristique = vivier marketing |
| 6 | **Rennes** | P1 | Bretagne | 35 | Rennes, Bruz, Cesson-Sévigné | ~7 500 | 88/100 | ••••• | ••••• | ••••· | ••••· | 87/100 | ••••• | **71.9** | Cyber+Dev | Pole cyber national (COMCYBER, DGA-MI, campus cyber breton), b<>com, telecoms |
| 7 | **Grenoble** | P1 | Auvergne-Rhône-Alpes | 38 | Grenoble, Saint-Martin-d'Hères, Échirolles | ~7 210 | 88/100 | ••••• | ••••• | ••••• | •••·· | 88/100 | ••••• | **71.4** | Cyber+Dev+Data/IA | Microelectronique CEA-Leti, STMicroelectronics ; hub deeptech de rang mondial |
| 8 | **Strasbourg** | P1 | Grand Est | 67 | Strasbourg, Haguenau, Schiltigheim | ~8 950 | 75/100 | ••••· | ••••· | ••••· | ••••· | 67/100 | ••••· | **64.6** | Cyber+Dev+Data/IA+Marketing | Capitale europeenne, banque-assurance, industrie ; ecosysteme numerique structure |
| 9 | **Montpellier** | P1 | Occitanie | 34, 30 | Montpellier, Nîmes, Lunel | ~10 080 | 81/100 | ••••· | ••••• | ••••· | ••••· | 45/100 | ••••· | **64.4** | Dev | IBM, Dell, sante-numerique ; corridor Montpellier-Nimes tres dynamique demographiquement |
| 10 | **Angers** | P1 | Pays de la Loire | 49 | Angers, Mauges-sur-Loire, Loire-Authion | ~5 070 | 81/100 | ••••· | ••••• | ••••· | ••••· | 72/100 | ••••· | **56.7** | Dev | Capitale French Tech, Cite de l'objet connecte, electronique-IoT, Thales |
| 11 | **Rouen** | P1 | Normandie | 76, 27 | Rouen, Saint-Étienne-du-Rouvray, Sotteville-lès-Rouen | ~8 080 | 56/100 | ••••· | •••·· | •••·· | •••·· | 74/100 | •••·· | **55.4** | Cyber | Chimie-industrie-logistique portuaire, assurance (Matmut) ; besoins IT industriels |
| 12 | **Clermont-Ferrand** | P1 | Auvergne-Rhône-Alpes | 63 | Clermont-Ferrand, Cournon-d'Auvergne, Riom | ~5 560 | 69/100 | ••••· | ••••· | ••••· | •••·· | 72/100 | ••••· | **55.0** | Cyber+Dev+Data/IA | Michelin (data/IA industrielle), Limagrain ; universite scientifique |
| 13 | **Annecy** | P2 | Auvergne-Rhône-Alpes, Bourgogne-Franch | 74, 01, 39 | Annecy, Annemasse, Valserhône | ~7 240 | 62/100 | •••·· | ••••· | •••·· | ••••· | 50/100 | ••••· | **53.8** | Dev+Marketing | Mecatronique-decolletage vallee de l'Arve, frontalier Geneve, tertiaire haut de gamme |
| 14 | **Toulon** | P2 | Provence-Alpes-Côte d'Azur | 83, 13 | Toulon, La Seyne-sur-Mer, Hyères | ~7 560 | 62/100 | ••••• | •••·· | •••·· | •••·· | 62/100 | •••·· | **53.3** | Cyber | 1er port militaire francais : Marine nationale, Naval Group, cyberdefense navale ; Universite de Toulon |
| 15 | **Brest** | P2 | Bretagne | 29 | Brest, Landerneau, Guipavas | ~4 600 | 75/100 | ••••• | ••••· | ••••· | •••·· | 64/100 | ••••· | **51.8** | Cyber | Capitale French Tech Brest Bretagne Ouest ; cyberdefense navale, Naval Group, Thales, IMT Atlantique |
| 16 | **Tours** | P2 | Centre-Val de Loire | 37 | Tours, Joué-lès-Tours, Saint-Cyr-sur-Loire | ~5 390 | 62/100 | •••·· | ••••· | •••·· | ••••· | 84/100 | •••·· | **51.6** | Dev+Marketing | Banque-assurance, tertiaire superieur, universite ; bassin bien structure |
| 17 | **Saint-Denis** | P2 | La Réunion | 974 | Saint-Denis, Saint-Pierre, Le Tampon | ~7 120 | 62/100 | •••·· | ••••· | •••·· | ••••· | 52/100 | •••·· | **50.2** | Dev+Marketing | La Reunion : Capitale French Tech ; forte demande numerique locale, eloignement structurel |
| 18 | **Pau** | P2 | Nouvelle-Aquitaine, Occitanie | 64, 65 | Pau, Billère, Lons | ~3 540 | 75/100 | ••••· | ••••· | ••••• | •••·· | 71/100 | ••••· | **49.5** | Data/IA | TotalEnergies et supercalculateur Pangea : l'un des plus gros centres de calcul prives d'Europe |
| 19 | **Vannes** | P2 | Bretagne | 56 | Vannes, Auray, Saint-Avé | ~3 460 | 75/100 | ••••• | ••••· | •••·· | ••••· | 70/100 | ••••· | **49.0** | Cyber | Pole cyber breton (Vannes-Ploermel), DGA, Universite Bretagne Sud, ESN |
| 20 | **Orléans** | P2 | Centre-Val de Loire | 45 | Orléans, Olivet, Saint-Jean-de-Braye | ~4 640 | 56/100 | •••·· | •••·· | •••·· | ••••· | 89/100 | •••·· | **48.6** | Marketing | Logistique, cosmetique, tertiaire ; effet de desserrement francilien |
| 21 | **Mulhouse** | P2 | Bourgogne-Franche-Comté, Grand Est | 68, 90 | Mulhouse, Saint-Louis, Wittenheim | ~6 050 | 50/100 | •••·· | •••·· | •••·· | •••·· | 74/100 | •••·· | **48.5** | Cyber+Dev+Data/IA+Marketing | Industrie automobile (Stellantis), textile, frontalier Bale-Suisse |
| 22 | **Metz** | P2 | Grand Est | 57, 54 | Metz, Thionville, Montigny-lès-Metz | ~7 230 | 50/100 | •••·· | •••·· | •••·· | •••·· | 57/100 | •••·· | **48.3** | Cyber+Dev+Data/IA+Marketing | Siderurgie-logistique, frontalier Luxembourg (emploi transfrontalier tres attractif) |
| 23 | **Caen** | P2 | Normandie | 14 | Caen, Hérouville-Saint-Clair, Bayeux | ~5 040 | 62/100 | ••••· | ••••· | •••·· | •••·· | 73/100 | •••·· | **48.3** | Cyber+Dev | Normandie Capitale French Tech 2026, NXP, Orange Labs, filiere cyber normande |
| 24 | **Dijon** | P2 | Bourgogne-Franche-Comté | 21 | Dijon, Chenôve, Talant | ~4 270 | 69/100 | •••·· | ••••· | ••••· | ••••· | 77/100 | •••·· | **48.1** | Dev+Data/IA+Marketing | OnDijon (smart city), agro-sante, universite ; tertiaire regional |
| 25 | **Bayonne** | P2 | Nouvelle-Aquitaine | 64, 40 | Bayonne, Anglet, Biarritz | ~3 930 | 69/100 | •••·· | ••••· | •••·· | ••••• | 80/100 | •••·· | **47.5** | Marketing | French Tech Pays Basque ; economie de marque, tourisme, sport-glisse = vivier marketing fort |
| 26 | **Nancy** | P2 | Grand Est | 54, 57 | Nancy, Vandœuvre-lès-Nancy, Lunéville | ~5 230 | 69/100 | ••••· | ••••· | ••••· | •••·· | 58/100 | •••·· | **47.3** | Cyber+Dev+Data/IA | LORIA (recherche informatique), industrie, universite de Lorraine |
| 27 | **Niort** | P2 | Nouvelle-Aquitaine, Pays de la Loire | 79, 17, 85 | Niort, Saint-Maixent-l'École, Chauray | ~2 390 | 88/100 | ••••· | ••••• | ••••• | ••••· | 66/100 | ••••· | **46.9** | Dev+Data/IA | Capitale de la mutualite (MAIF, MACIF, MAAF, Groupama) : besoins IT et data massifs, Niort Tech |
| 28 | **Avignon** | P2 | Occitanie, Provence-Alpes-Côte d'Azur | 84, 13, 30 | Avignon, Carpentras, Orange | ~6 820 | 56/100 | •••·· | •••·· | •••·· | ••••· | 61/100 | ••··· | **45.8** | Marketing | Agro-logistique-tourisme ; tissu numerique limite, vivier tertiaire important |
| 29 | **Belfort** | P2 | Bourgogne-Franche-Comté | 25, 90, 70 | Belfort, Montbéliard, Audincourt | ~3 700 | 62/100 | ••••· | ••••· | ••••· | ••··· | 80/100 | •••·· | **45.1** | Cyber+Dev+Data/IA | Alstom, GE, Stellantis Sochaux, UTBM : bassin tres technique et industriel |
| 30 | **Le Havre** | P2 | Normandie | 76, 14, 27 | Le Havre, Montivilliers, Bolbec | ~4 310 | 56/100 | ••••· | •••·· | •••·· | •••·· | 71/100 | •••·· | **43.8** | Cyber | 1er port francais : cybersecurite portuaire et logistique, industrie |
| 31 | **Le Mans** | P3/TEST | Pays de la Loire | 72 | Le Mans, Allonnes, Coulaines | ~4 230 | 56/100 | •••·· | •••·· | ••••· | •••·· | 72/100 | •••·· | **43.7** | Data/IA | Assurance (groupe Covea/MMA) : gros besoins data et IT ; industrie automobile |
| 32 | **Valence** | P3/TEST | Auvergne-Rhône-Alpes | 26, 07 | Valence, Romans-sur-Isère, Bourg-lès-Valence | ~4 340 | 50/100 | •••·· | •••·· | •••·· | •••·· | 77/100 | •••·· | **43.6** | Cyber+Dev+Data/IA+Marketing | Valence-Romans : industrie, electronique, nucleaire ; corridor rhodanien |
| 33 | **Lorient** | P3/TEST | Bretagne | 56, 29 | Lorient, Lanester, Ploemeur | ~2 960 | 62/100 | ••••· | ••••· | •••·· | •••·· | 84/100 | •••·· | **43.0** | Cyber+Dev | Naval Group, cyberdefense navale, Universite Bretagne Sud, pole mer |
| 34 | **Chambéry** | P3/TEST | Auvergne-Rhône-Alpes | 73, 38, 01, 74 | Chambéry, Aix-les-Bains, La Motte-Servolex | ~3 970 | 56/100 | •••·· | ••••· | •••·· | •••·· | 72/100 | •••·· | **42.8** | Dev | Savoie Technolac, energies, tourisme ; tissu tech de taille moyenne |
| 35 | **Poitiers** | P3/TEST | Nouvelle-Aquitaine | 86 | Poitiers, Buxerolles, Jaunay-Marigny | ~3 210 | 69/100 | •••·· | ••••· | ••••· | ••••· | 69/100 | •••·· | **42.5** | Dev+Data/IA+Marketing | Futuroscope (image-numerique), laboratoire informatique universitaire, mutuelles proches |
| 36 | **Besançon** | P3/TEST | Bourgogne-Franche-Comté | 25, 70, 39 | Besançon, Valdahon, Baume-les-Dames | ~3 030 | 69/100 | ••••· | ••••· | ••••· | •••·· | 69/100 | •••·· | **41.8** | Cyber+Dev+Data/IA | Microtechniques, FEMTO-ST, biomedical : culture technique tres marquee |
| 37 | **La Rochelle** | P3/TEST | Nouvelle-Aquitaine | 17 | La Rochelle, Rochefort, Aytré | ~4 000 | 69/100 | •••·· | ••••· | ••••· | ••••· | 49/100 | •••·· | **41.5** | Dev+Data/IA+Marketing | Ecosysteme French Tech, universite, port ; territoire pilote sur la donnee environnementale |
| 38 | **Troyes** | P3/TEST | Grand Est | 10 | Troyes, Saint-André-les-Vergers, La Chapelle-Saint-Luc | ~2 280 | 69/100 | ••••· | ••••· | •••·· | ••••· | 80/100 | •••·· | **40.7** | Cyber+Dev+Marketing | Universite de technologie de Troyes (ingenierie info et cyber), logistique-textile |
| 39 | **Perpignan** | P3/TEST | Occitanie | 66, 11 | Perpignan, Canet-en-Roussillon, Saint-Cyprien | ~4 720 | 38/100 | ••··· | ••··· | ••··· | ••••· | 86/100 | ••··· | **39.9** | Marketing | Tourisme-agriculture ; tissu numerique faible mais gros etablissements scolaires |
| 40 | **Saint-Nazaire** | P3/TEST | Bretagne, Pays de la Loire | 44, 56 | Saint-Nazaire, Pornic, La Baule-Escoublac | ~3 760 | 50/100 | •••·· | •••·· | •••·· | •••·· | 68/100 | •••·· | **39.7** | Cyber+Dev+Data/IA+Marketing | Chantiers de l'Atlantique, Airbus, eolien offshore : industrie lourde a forts besoins de numerisation |
| 41 | **Reims** | P3/TEST | Grand Est, Hauts-de-France | 51, 02, 08 | Reims, Épernay, Tinqueux | ~4 060 | 56/100 | •••·· | •••·· | •••·· | ••••· | 72/100 | ••··· | **39.4** | Marketing | Champagne-agro-logistique ; tissu numerique modeste, tertiaire important |
| 42 | **Angoulême** | P3/TEST | Nouvelle-Aquitaine | 16 | Angoulême, Soyaux, La Couronne | ~2 390 | 69/100 | •••·· | ••••· | •••·· | ••••• | 69/100 | •••·· | **39.1** | Marketing | Pole Magelis : image animee, jeu video, BD - vivier creatif et numerique atypique |
| 43 | **Fort-de-France** | P3/TEST | Martinique | 972 | Fort-de-France, Le Lamentin, Le Robert | ~3 740 | 44/100 | ••··· | •••·· | ••··· | ••••· | 88/100 | ••··· | **38.4** | Marketing | Martinique : tertiaire-administration, eloignement maximal, offre superieure numerique reduite |
| 44 | **Amiens** | P3/TEST | Hauts-de-France | 80, 60 | Amiens, Albert, Corbie | ~3 780 | 50/100 | •••·· | •••·· | •••·· | •••·· | 66/100 | ••··· | **35.6** | Cyber+Dev+Data/IA+Marketing | Industrie et universite ; tissu numerique limite, effet de proximite francilienne |
| 45 | **Dunkerque** | P3/TEST | Hauts-de-France | 62, 59 | Dunkerque, Calais, Grande-Synthe | ~3 840 | 50/100 | •••·· | •••·· | •••·· | •••·· | 39/100 | •••·· | **34.3** | Cyber+Dev+Data/IA+Marketing | Reindustrialisation majeure (gigafactories batteries), logistique transmanche : besoins IT emergents |
| 46 | **Limoges** | P3/TEST | Nouvelle-Aquitaine | 87 | Limoges, Saint-Junien, Panazol | ~3 210 | 50/100 | •••·· | •••·· | •••·· | •••·· | 70/100 | ••··· | **34.2** | Cyber+Dev+Data/IA+Marketing | Legrand, ceramique, universite ; economie numerique peu dense |
| 47 | **Les Abymes** | P3/TEST | Guadeloupe | 971 | Les Abymes, Baie-Mahault, Le Gosier | ~3 320 | 44/100 | ••··· | •••·· | ••··· | ••••· | 67/100 | ••··· | **32.6** | Marketing | Guadeloupe : eloignement, offre superieure numerique reduite, tertiaire dominant |
| 48 | **Saint-Brieuc** | P3/TEST | Bretagne | 22 | Saint-Brieuc, Lamballe-Armor, Plérin | ~2 970 | 38/100 | ••··· | •••·· | ••··· | •••·· | 73/100 | ••··· | **30.8** | Dev+Marketing | Agroalimentaire ; tissu numerique faible, offre superieure limitee |
| 49 | **Mamoudzou** | P3/TEST | Mayotte | 976 | Mamoudzou, Koungou, Dzaoudzi | ~2 690 | 38/100 | ••··· | •••·· | ••··· | •••·· | 98/100 | •···· | **30.8** | Dev+Marketing | Mayotte : demographie la plus jeune de France, offre superieure quasi inexistante |
| 50 | **Colmar** | P3/TEST | Grand Est | 68, 67, 88 | Colmar, Sélestat, Wintzenheim | ~2 970 | 38/100 | ••··· | •••·· | ••··· | •••·· | 72/100 | ••··· | **30.6** | Dev+Marketing | Industrie et viticulture ; bassin dense mais peu tech |
| 51 | **Quimper** | P3/TEST | Bretagne | 29 | Quimper, Concarneau, Douarnenez | ~3 100 | 38/100 | ••··· | •••·· | ••··· | •••·· | 64/100 | ••··· | **29.6** | Dev+Marketing | Agroalimentaire et tourisme ; tissu numerique faible |
| 52 | **Cholet** | P3/TEST | Nouvelle-Aquitaine, Pays de la Loire | 85, 49, 79 | Cholet, Sèvremoine, Montaigu-Vendée | ~3 170 | 44/100 | •••·· | •••·· | ••··· | •••·· | 53/100 | ••··· | **29.2** | Cyber+Dev+Marketing | Tissu tres dense de PME industrielles (mecanique, agroalimentaire, mode) ; offre superieure locale limitee |
| 53 | **Saint-Malo** | P3/TEST | Bretagne | 35, 22 | Saint-Malo, Dinan, Dinard | ~2 620 | 44/100 | ••··· | •••·· | ••··· | ••••· | 64/100 | ••··· | **29.0** | Marketing | Tourisme et agro ; tissu numerique faible, vivier tertiaire |
| 54 | **Albi** | P3/TEST | Occitanie | 81 | Albi, Gaillac, Graulhet | ~2 430 | 50/100 | •••·· | •••·· | •••·· | •••·· | 56/100 | ••··· | **28.1** | Cyber+Dev+Data/IA+Marketing | IMT Mines Albi, agro ; bassin moyen a culture d'ingenierie |
| 55 | **Béziers** | P3/TEST | Occitanie | 34, 11 | Béziers, Narbonne, Agde | ~4 410 | 38/100 | ••··· | ••··· | ••··· | ••••· | 50/100 | •···· | **27.7** | Marketing | Tourisme-viticulture ; economie numerique tres faible, vivier surtout tertiaire et pro |
| 56 | **Évreux** | P3/TEST | Centre-Val de Loire, Normandie, Île-de | 27, 78, 28 | Évreux, Vernon, Gaillon | ~3 040 | 31/100 | ••··· | ••··· | ••··· | •••·· | 64/100 | ••··· | **27.6** | Marketing | Pharma-cosmetique, sous-traitance ; forte dependance francilienne |
| 57 | **Forbach** | P3/TEST | Grand Est | 57, 67 | Forbach, Sarreguemines, Saint-Avold | ~2 940 | 31/100 | ••··· | ••··· | ••··· | •••·· | 67/100 | •···· | **24.2** | Marketing | Bassin houiller en reconversion, frontalier Sarre ; economie numerique tres faible |
| 58 | **Montélimar** | P3/TEST | Auvergne-Rhône-Alpes, Provence-Alpes-C | 26, 07, 84 | Montélimar, Bollène, Pierrelatte | ~2 700 | 38/100 | •••·· | ••··· | ••··· | •••·· | 44/100 | ••··· | **23.8** | Cyber+Marketing | Nucleaire (Tricastin), agro ; bassin etale et peu tech |
| 59 | **Saint-Quentin** | P3/TEST | Hauts-de-France | 02, 80, 59, 60 | Saint-Quentin, Tergnier, Péronne | ~2 650 | 31/100 | ••··· | ••··· | ••··· | •••·· | 61/100 | •···· | **21.7** | Marketing | Industrie en reconversion ; economie numerique tres faible |
---

## Lectures transversales

### Le déplacement : une information opérationnelle, jamais un critère de sélection

La colonne `d_campus_nexa_km` (distance à Paris, Lyon ou Lille) figure dans les données et **n'entre
ni dans le score, ni dans le classement, ni dans le choix des zones de test**. Elle est là pour
organiser les tournées **une fois les zones retenues** — pas pour écarter un territoire pertinent
parce qu'il est loin.

Ce choix est délibéré : intégrer le coût de déplacement à la sélection reviendrait à confondre
*« où le potentiel est-il réel ? »* avec *« où est-il commode d'aller ? »*, et conduirait
mécaniquement à concentrer l'expérimentation autour du Bassin parisien, de Rhône-Alpes et des
Hauts-de-France — c'est-à-dire à reproduire, sous une autre forme, le biais que la règle des 60 km
cherchait précisément à éviter.

La contrainte budgétaire est prise en compte **sur le nombre de zones testées** (9 recommandées sur
59), pas sur leur identité.

### Les zones où le vivier est important mais l'offre supérieure locale absente

Ces bassins **ne contiennent aucun pôle étudiant majeur** (université de plein exercice). Ce sont les
supports directs des hypothèses H1 et H2 — celles que NEXA veut pouvoir vérifier, pas confirmer.

| Bassin | Prio | Tle est. | Pôle étudiant le plus proche | Filières dominantes |
|---|---|---|---|---|
| Vannes | P2 | ~3 460 | 47 km | Cyber |
| Bayonne | P2 | ~3 930 | 91 km | Marketing |
| Niort | P2 | ~2 390 | 56 km | Dev + Data/IA |
| Belfort–Montbéliard | P2 | ~3 700 | 38 km | Cyber + Dev + Data/IA |
| Valence | P3/TEST | ~4 340 | 70 km | polyvalent |
| Saint-Nazaire | P3/TEST | ~3 760 | 53 km | polyvalent |
| Angoulême | P3/TEST | ~2 390 | 89 km | Marketing |
| Dunkerque–Calais | P3/TEST | ~3 840 | 69 km | polyvalent |
| Saint-Brieuc | P3/TEST | ~2 970 | 92 km | Dev + Marketing |
| Colmar | P3/TEST | ~2 970 | 40 km | Dev + Marketing |
| Quimper | P3/TEST | ~3 100 | 53 km | Dev + Marketing |
| Saint-Malo | P3/TEST | ~2 620 | 62 km | Marketing |
| **Béziers–Narbonne** | P3/TEST | **~4 410** | 59 km | Marketing |
| Évreux | P3/TEST | ~3 040 | 47 km | Marketing |
| Forbach | P3/TEST | ~2 940 | 53 km | Marketing |
| Montélimar | P3/TEST | ~2 700 | 68 km | Cyber + Marketing |
| Saint-Quentin | P3/TEST | ~2 650 | 57 km | Marketing |
| Mamoudzou (Mayotte) | P3/TEST | ~2 690 | 1 415 km | Dev + Marketing |

**Béziers–Narbonne est le meilleur support de H1/H2 du panel** : c'est le plus gros vivier de la
liste (~4 410 Terminales estimées, supérieur à Niort et à Vannes), sans aucun pôle étudiant à moins
de 59 km, et avec une économie numérique notée 1/5 — il teste donc **simultanément H1 et H3**.
Viennent ensuite **Valence** (~4 340, pôle à 70 km) et **Dunkerque–Calais** (~3 840, pôle à 69 km).

Saint-Quentin est le contre-test le plus radical (économie numérique 1/5 également), mais son vivier
est le plus faible du panel : un résultat nul y serait ambigu.

### Les anomalies : forte affinité, vivier modeste

Le classement par volume ferait remonter les métropoles. Ces bassins sont ceux dont **l'affinité NEXA
dépasse le plus largement le poids démographique** — les « pépites » à surveiller :

| Bassin | Affinité | Vivier (indice) | Écart | Pourquoi |
|---|---|---|---|---|
| **Niort** | 88 | 1 | **+86** | MAIF, MACIF, MAAF, Groupama : besoins IT/data massifs pour ~2 400 Terminales |
| **Troyes** | 69 | 0 | +69 | Université de technologie (ingénierie informatique et cyber) dans une ville moyenne |
| **Angoulême** | 69 | 1 | +67 | Pôle Magelis : image animée, jeu vidéo — vivier créatif atypique |
| **Vannes** | 75 | 13 | +62 | Pôle cyber breton, DGA, Université Bretagne Sud |
| **Pau** | 75 | 13 | +62 | Supercalculateur Pangea (TotalEnergies) : l'un des plus gros centres de calcul privés d'Europe |
| **Besançon** | 69 | 8 | +60 | Microtechniques, FEMTO-ST : culture technique très marquée |
| **Poitiers** | 69 | 10 | +59 | Futuroscope, laboratoire d'informatique universitaire |
| **Lorient** | 62 | 8 | +55 | Naval Group, cyberdéfense navale |

Ces zones sont exactement celles qu'un classement mécanique par volume aurait manquées.
**Niort figure au portefeuille de test recommandé pour cette raison** : c'est l'anomalie la plus
marquée de tout le panel, et la seule qui permette de répondre à la question « une affinité très
forte peut-elle compenser un vivier faible ? ». **Vannes** y est associée pour la même logique, sur
un profil cyber spécialisé.

### La réserve : 16 bassins non scorés

Entre 110 000 et 250 000 habitants, sous le seuil de l'univers scoré, mais construits par
l'algorithme et disponibles dans `data/bassins.json` : La Roche-sur-Yon, Chalon-sur-Saône, Laval,
Chartres, Blois, Brive-la-Gaillarde, Épinal, Maubeuge, Draguignan, Soissons, Agen, Montauban, Alès,
La Teste-de-Buch, Montereau-Fault-Yonne, Saint-Paul (Réunion).

À réexaminer en année 2 si l'hypothèse H7 (villes moyennes) se confirme.
