# Mobilanalyse marked

Lokal marimo-app for analyse av `data/mobil.parquet`.

## Start lokalt

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
