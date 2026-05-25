# Mobilanalyse marked

Lokal marimo-app for analyse av `data/mobil.parquet`.

## Start lokalt som notebook

```bash
uv sync
uv run marimo edit mobilanalyse.py
```

Read-only appvisning:

```bash
uv run marimo run mobilanalyse.py
```

## Codex pairing

Start notebooken i marimo-browseren, åpne `Pair with an agent`, velg Codex og bruk kommandoen marimo viser. Token fra pair-dialogen er midlertidig og skal ikke committes.

Eksempel på formen marimo viser:

```bash
codex "$(uvx marimo@latest pair prompt --url 'http://localhost:2718/' --with-token --codex)"
```

Dette prosjektet er foreløpig kun satt opp for lokal kjøring. Publisering, snapshot-jobb og `dist/` kan legges til senere.

## Bygg statisk app

Den ferdige appen bygges som HTML/WASM og kan hostes på en ren static web app.
Koden vises ikke i appen, og brukeren trenger ikke Python eller marimo lokalt.

```bash
./scripts/build-static.sh
```

Dette lager:

```text
dist/
├── index.html
├── assets/
└── data/
    └── mobil.parquet
```

Publiser hele `dist/`-mappen. Appen må serveres over HTTP, ikke åpnes direkte
som `file://`, fordi WebAssembly-appen henter `data/mobil.parquet` via browseren.

## Publisering på GitHub Pages

Repoet har en GitHub Actions-workflow som bygger og publiserer appen til GitHub
Pages ved push til `main`.

Workflowen kjører:

```bash
uv sync --frozen
./scripts/build-static.sh
```

Deretter publiseres `dist/` som Pages-artifact. `data/mobil.parquet` er et lite
statisk snapshot som inngår i repoet slik at appen kan bygges uten tilgang til
lokal database.
