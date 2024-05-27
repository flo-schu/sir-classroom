# Modellregeln

A: Bewegung so lassen. Dann ist das nicht so realistisch
B: 

Wie könnte die Modelldynamik aussehen

## Startbedingungen
1. Initiale positionen der agenten
2. Initiale viruslast
3. Initiale antikörper konzentration 

## Modellparameter
- Dauer infektiösität
- Schwellwerte
  - ab wann fühle ich mich Krank
- ratenkonstanten
  - wachstumsrate der erreger
  - wachstumsrate der antikörper
  - überlebensdauer der erreger
  - überlebensdauer der antikörper
  - Erregerbekämpfung
  - diffusionsrate in Raumluft
  - 

## Regeln
- Lüften: Verteilt die Viruslast homogen über den Raum und reduziert die Last um einen prozentualen Anteil
- Schüler essen sehr gesundes Essen in der Schule: --> Erhöht die Wachstumsrate der antikörper
- Masken: Redukton der Emissionsrate
- Zuhause bleiben: Agenten temporär entfernen
- Impfstoff: Versuch (Virenlast erhöhen); sonst Antikörper konzentration erhöhen.
- Schule ließen: Agenten werden weiter simuliert aber sind nicht mehr im Raum
- Alle setzen sich weiter von einander entfernt hin
- Halbe klassengröße
- Kranke schüler isolieren
- nichts tun
- Hände waschen: Systemgrenze

## Simulation wird immer von vorne laufen gelassen

- Future: Entscheidungsbaumartiges zeitdynamisches pandemiegeschehen mit entscheidungen die den Ausgang beeinflussen


## Nötige konzepte zum Verständnis

- Diffusion


## Implementierung

- Basismodell mit Aerosoldiffusionsmodul + Infektionsdynamik in agenten
- Loop

- Mehtoden für die verschiedenen Regeln, die als Handlung von Agenten verstanden werden können.


2. räumliche ausbreitung der Erreger modellieren
    - Agenten werte zuweisen (Viruslast)


## Next steps:

- [ ] Wochenende einbauen + parameter justieren
- [ ] 2. Schwellwert ich fühle mich nicht gut.
- [ ] Infektionparameter aus verteilung ziehen (wachstumsrate antikörper individuell)
- [x] minimalistische version für den workshop
- [ ] Simulation pause/play button

- [ ] Kurven für infektionsdynamik dynamisch plotten
- [ ] Boxen ausgrauen wenn schüler zuhause bleiben
- [ ] Namen in Zellen schreiben

- [ ] Regeln einbauen die wir uns überlegt haben
- [ ] Schwellwert bleibt fix und kann als scenario variiert werden
- [ ] Alternierende Tage mit Leuten die in die Schule
- [ ] Weitere sitzscenarien
- [ ] Positionswechsel (das sollte hervorgehoben werden)