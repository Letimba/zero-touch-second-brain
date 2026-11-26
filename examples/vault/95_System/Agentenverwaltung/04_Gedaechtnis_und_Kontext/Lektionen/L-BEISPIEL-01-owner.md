---
typ: lektion
status: aktiv
erstellt: 2026-11-27
prioritaet: P1
bestaetigt_am: [2026-11-27]
tags: [agenten, pg]
---
# Ein Owner pro Arbeitspaket

## Regel
Jedes Arbeitspaket hat genau einen verantwortlichen Agenten und einen
abgegrenzten Schreibbereich.

## Warum
Zwei Schreiber im selben Dateibereich erzeugen versteckte Konflikte und
überschreiben sich gegenseitig.

## Anwendung
Vor der Delegation Owner und Schreibpfad festlegen; parallele Reviewer dürfen
nur lesen.

## Grenzen
Reine Analyse darf parallelisiert werden, solange niemand schreibt.
