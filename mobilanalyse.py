# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "marimo>=0.23.3",
# ]
# ///

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    from mobilanalyse_generated import (
        FIG1_PERIOD_TEXT,
        FIG1_SUMMARY_LINES,
        FIG2_NOTE,
        FIG3_PERIOD_TEXT,
        FIG3_SUMMARY_LINES,
        FIGURE_PATHS,
    )

    def summary_box(title: str, lines: list[str], variant: str) -> str:
        return f"""
        <div class="summary-box summary-box--{variant}">
            <div class="summary-box__title">{title}</div>
            {"<br>".join(line for line in lines if line)}
        </div>
        """

    def figure_panel(title: str, image_path: str, alt: str) -> str:
        return f"""
        <section class="figure-panel">
            <div class="figure-panel__title">{title}</div>
            <img class="figure-panel__image" src="{image_path}" alt="{alt}">
        </section>
        """

    def two_figures(left: str, right: str) -> str:
        return f"""
        <div class="figure-grid">
            {left}
            {right}
        </div>
        """

    mo.Html(
        """
        <style>
            .mobilanalyse-title {
                margin: 0 0 24px;
                color: #0b2b66;
                font-size: 2.25rem;
                font-weight: 700;
                line-height: 1.1;
            }

            .figure-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 32px;
                align-items: start;
                width: 100%;
            }

            .figure-panel {
                min-width: 0;
            }

            .figure-panel__title {
                margin: 0 0 8px;
                color: #000;
                font-size: 1.25rem;
                font-weight: 700;
                line-height: 1.25;
            }

            .figure-panel__image {
                display: block;
                width: 100%;
                height: auto;
            }

            .summary-box {
                margin: 16px auto 0;
                max-width: 860px;
                padding: 18px 28px;
                border: 1px solid #0b2b66;
                border-radius: 28px;
                color: #000;
                font-size: 1.05rem;
                line-height: 1.45;
                text-align: center;
            }

            .summary-box__title {
                margin: 0 0 12px;
                font-size: 1.2rem;
                font-weight: 700;
            }

            .summary-box--market-share {
                background: #f6c7a7;
            }

            .summary-box--trend {
                width: fit-content;
                max-width: 560px;
                padding: 22px 44px;
                border-radius: 999px;
                background: #c9570d;
                color: #fff;
                font-weight: 700;
            }

            .summary-box--segment {
                background: #dcefd2;
            }

            .section-divider {
                width: 100%;
                margin: 46px 0 24px;
                border-top: 3px solid #0b2b66;
            }

            @media (max-width: 900px) {
                .figure-grid {
                    grid-template-columns: 1fr;
                    gap: 24px;
                }

                .summary-box {
                    border-radius: 20px;
                    padding: 16px 18px;
                }
            }
        </style>
        <div class="mobilanalyse-title">Mobilanalyse marked</div>
        """
    )
    return (
        FIG1_PERIOD_TEXT,
        FIG1_SUMMARY_LINES,
        FIG2_NOTE,
        FIG3_PERIOD_TEXT,
        FIG3_SUMMARY_LINES,
        FIGURE_PATHS,
        figure_panel,
        mo,
        summary_box,
        two_figures,
    )


@app.cell
def _(mo):
    mo.md("""
    ## 1 - Utvikling i markedsandeler
    """)
    return


@app.cell
def _(FIG1_PERIOD_TEXT, FIG1_SUMMARY_LINES, FIGURE_PATHS, figure_panel, mo, summary_box, two_figures):
    mo.Html(
        two_figures(
            figure_panel(
                "Basert på abonnement",
                FIGURE_PATHS["fig1_abonnement"],
                "Utvikling i markedsandeler basert på abonnement",
            ),
            figure_panel(
                "Basert på omsetning",
                FIGURE_PATHS["fig1_omsetning"],
                "Utvikling i markedsandeler basert på omsetning",
            ),
        )
        + summary_box(FIG1_PERIOD_TEXT, FIG1_SUMMARY_LINES, "market-share")
    )
    return


@app.cell
def _(mo):
    mo.Html('<div class="section-divider"></div>')
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2 - Lineær trend i markedsandeler
    """)
    return


@app.cell
def _(FIG2_NOTE, FIGURE_PATHS, figure_panel, mo, two_figures):
    mo.Html(
        two_figures(
            figure_panel(
                "Abonnement",
                FIGURE_PATHS["fig2_abonnement"],
                "Lineær trend i markedsandeler basert på abonnement",
            ),
            figure_panel(
                "Omsetning",
                FIGURE_PATHS["fig2_omsetning"],
                "Lineær trend i markedsandeler basert på omsetning",
            ),
        )
        + f'<div class="summary-box summary-box--trend">{FIG2_NOTE}</div>'
    )
    return


@app.cell
def _(mo):
    mo.Html('<div class="section-divider"></div>')
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3 - Abonnement fordelt på privat og bedrift
    """)
    return


@app.cell
def _(FIG3_PERIOD_TEXT, FIG3_SUMMARY_LINES, FIGURE_PATHS, figure_panel, mo, summary_box, two_figures):
    mo.Html(
        two_figures(
            figure_panel(
                "Privat",
                FIGURE_PATHS["fig3_privat"],
                "Abonnement fordelt på tilbydere i privatmarkedet",
            ),
            figure_panel(
                "Bedrift",
                FIGURE_PATHS["fig3_bedrift"],
                "Abonnement fordelt på tilbydere i bedriftsmarkedet",
            ),
        )
        + summary_box(FIG3_PERIOD_TEXT, FIG3_SUMMARY_LINES, "segment")
    )
    return


if __name__ == "__main__":
    app.run()
