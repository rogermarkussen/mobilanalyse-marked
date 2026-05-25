# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "marimo>=0.23.3",
#   "matplotlib>=3.8.0",
#   "openpyxl>=3.1.0",
#   "pyarrow>=16.0.0",
#   "polars>=1.0.0",
# ]
# ///

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="full")


@app.cell
def _():
    from io import BytesIO
    from pathlib import Path

    import matplotlib.pyplot as plt
    import marimo as mo
    import polars as pl
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.worksheet.table import Table, TableStyleInfo

    try:
        from pyodide.http import pyfetch
    except ImportError:
        pyfetch = None
    return (
        Alignment,
        Border,
        BytesIO,
        Font,
        Path,
        PatternFill,
        Side,
        Table,
        TableStyleInfo,
        Workbook,
        mo,
        pl,
        plt,
        pyfetch,
    )


@app.cell
async def _(Path, pl, pyfetch):
    if pyfetch is None:
        parquet_path = Path(__file__).parent / "data" / "mobil.parquet"
    else:
        response = await pyfetch("../data/mobil.parquet")
        parquet_path = Path("/tmp/mobil.parquet")
        parquet_path.write_bytes(await response.bytes())

    df = pl.scan_parquet(parquet_path)
    return (df,)


@app.cell
def _(
    Alignment,
    Border,
    BytesIO,
    Font,
    PatternFill,
    Side,
    Table,
    TableStyleInfo,
    Workbook,
    mo,
    pl,
):
    def excel_download(_data, _filename, _title, _sheet_name="Data"):
        def _build_workbook():
            _export_data = _data.with_columns(
                (pl.col("markedsandel") / 100).alias("markedsandel")
            )
            _headers = _export_data.columns
            _workbook = Workbook()
            _sheet = _workbook.active
            _sheet.title = _sheet_name[:31]

            _sheet["A1"] = _title
            _sheet["A1"].font = Font(bold=True, size=14, color="0B2B66")
            _sheet.merge_cells(
                start_row=1,
                start_column=1,
                end_row=1,
                end_column=max(1, len(_headers)),
            )

            _sheet.append([])
            _sheet.append(_headers)
            for _row in _export_data.iter_rows():
                _sheet.append(list(_row))

            _header_fill = PatternFill("solid", fgColor="0B2B66")
            _header_font = Font(bold=True, color="FFFFFF")
            _thin = Side(style="thin", color="D9D9D9")
            _border = Border(bottom=_thin)

            for _cell in _sheet[3]:
                _cell.fill = _header_fill
                _cell.font = _header_font
                _cell.alignment = Alignment(horizontal="center")

            for _row in _sheet.iter_rows(
                min_row=4,
                max_row=_sheet.max_row,
                max_col=_sheet.max_column,
            ):
                for _cell in _row:
                    _cell.border = _border
                    if _cell.column_letter == "A":
                        _cell.alignment = Alignment(horizontal="center")
                    if _headers[_cell.column - 1] == "markedsandel":
                        _cell.number_format = "0.0%"

            _table_ref = f"A3:{_sheet.cell(_sheet.max_row, _sheet.max_column).coordinate}"
            _table = Table(displayName="Markedsandeler", ref=_table_ref)
            _table.tableStyleInfo = TableStyleInfo(
                name="TableStyleMedium2",
                showFirstColumn=False,
                showLastColumn=False,
                showRowStripes=True,
                showColumnStripes=False,
            )
            _sheet.add_table(_table)
            _sheet.freeze_panes = "A4"
            _sheet.auto_filter.ref = _table_ref

            for _column in _sheet.columns:
                _max_length = max(
                    len(str(_cell.value)) if _cell.value is not None else 0
                    for _cell in _column
                )
                _sheet.column_dimensions[_column[0].column_letter].width = min(
                    max(_max_length + 2, 12),
                    28,
                )

            _buffer = BytesIO()
            _workbook.save(_buffer)
            return _buffer.getvalue()

        return mo.download(
            data=_build_workbook,
            filename=_filename,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            label="Excel-eksport",
        )

    return (excel_download,)


@app.cell
def _(mo):
    mo.Html(
        """
        <div style="margin-bottom: 20px;">
            <div style="font-size: 2.2rem; font-weight: 700; color: #0b2b66;">
                Mobilanalyse marked
            </div>
        </div>
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 1 - Utvikling i markedsandeler
    """)
    return


@app.cell
def _(df, pl):
    _provider_name = pl.col("fusnavn").str.to_lowercase()
    _provider_group = (
        pl.when(_provider_name.str.contains("telenor"))
        .then(pl.lit("Telenor"))
        .when(_provider_name.str.contains("telia"))
        .then(pl.lit("Telia"))
        .when(
            _provider_name.is_in(["ice communication norge", "lyse tele"])
            | _provider_name.str.contains("lyse")
            | _provider_name.str.contains("ice")
        )
        .then(pl.lit("Lyse Tele (Ice)"))
        .otherwise(pl.lit("Øvrige"))
    )

    market_share_abonnement = (
        df.filter(
            (pl.col("dk") == "Mobiltelefoni")
            & (pl.col("hg") == "Abonnement")
            & (pl.col("n1").is_in(["Fakturert", "Kontantkort"]))
            & (pl.col("n2") == "Ingen")
            & (pl.col("tp") == "Sum")
            & (pl.col("sk") == "Sluttbruker")
            & (pl.col("delar") == "Helår")
        )
        .with_columns(tilbyder=_provider_group)
        .group_by("ar", "tilbyder")
        .agg(pl.col("svar").sum().alias("abonnement"))
        .with_columns(
            markedsandel=pl.col("abonnement")
            * 100
            / pl.col("abonnement").sum().over("ar")
        )
        .select("ar", "tilbyder", "markedsandel")
        .sort("ar", "tilbyder")
        .collect()
    )
    return (market_share_abonnement,)


@app.cell
def _(df, pl):
    _provider_name = pl.col("fusnavn").str.to_lowercase()
    _provider_group = (
        pl.when(_provider_name.str.contains("telenor"))
        .then(pl.lit("Telenor"))
        .when(_provider_name.str.contains("telia"))
        .then(pl.lit("Telia"))
        .when(
            _provider_name.is_in(["ice communication norge", "lyse tele"])
            | _provider_name.str.contains("lyse")
            | _provider_name.str.contains("ice")
        )
        .then(pl.lit("Lyse Tele (Ice)"))
        .otherwise(pl.lit("Øvrige"))
    )

    market_share_omsetning = (
        df.filter(
            (pl.col("dk") == "Mobiltelefoni")
            & (pl.col("hg") == "Inntekter")
            & (pl.col("tp") == "Sum")
            & (pl.col("sk") == "Sluttbruker")
            & (pl.col("delar") == "Helår")
        )
        .with_columns(tilbyder=_provider_group)
        .group_by("ar", "tilbyder")
        .agg(pl.col("svar").sum().alias("omsetning"))
        .with_columns(
            markedsandel=pl.col("omsetning")
            * 100
            / pl.col("omsetning").sum().over("ar")
        )
        .select("ar", "tilbyder", "markedsandel")
        .sort("ar", "tilbyder")
        .collect()
    )
    return (market_share_omsetning,)


@app.cell
def _(
    excel_download,
    market_share_abonnement,
    market_share_omsetning,
    mo,
    pl,
    plt,
):
    _colors = {
        "Telenor": "#156082",
        "Telia": "#7030a0",
        "Lyse Tele (Ice)": "#ffc000",
        "Øvrige": "#00b050",
    }
    _order = ["Telenor", "Telia", "Lyse Tele (Ice)", "Øvrige"]

    def _percent(_value):
        return f"{_value:.1f} %".replace(".", ",")

    def _plot_market_share(_data, _upper_y):
        _fig, _ax = plt.subplots(figsize=(7.2, 4.8), dpi=120)
        for _provider in _order:
            _provider_data = _data.filter(_data["tilbyder"] == _provider).sort("ar")
            if _provider_data.is_empty():
                continue

            _xs = _provider_data["ar"].to_list()
            _ys = _provider_data["markedsandel"].to_list()
            _ax.plot(
                _xs,
                _ys,
                color=_colors[_provider],
                linewidth=3.0,
                solid_capstyle="round",
                label=_provider,
            )

            if len(_ys) >= 2:
                _ax.annotate(
                    _percent(_ys[-2]),
                    xy=(_xs[-2], _ys[-2]),
                    xytext=(10, 6),
                    textcoords="offset points",
                    color="#404040",
                    fontsize=9,
                )
            _ax.annotate(
                _percent(_ys[-1]),
                xy=(_xs[-1], _ys[-1]),
                xytext=(10, 6),
                textcoords="offset points",
                color="#404040",
                fontsize=9,
            )

        _ax.set_ylim(0, _upper_y)
        _ax.set_yticks(range(0, _upper_y + 1, 10))
        _ax.set_yticklabels([_percent(_value) for _value in range(0, _upper_y + 1, 10)])
        _ax.set_xticks(sorted(_data["ar"].unique().to_list()))
        _ax.grid(axis="y", color="#d9d9d9", linewidth=0.8)
        _ax.grid(axis="x", visible=False)
        _ax.spines[["top", "right", "left"]].set_visible(False)
        _ax.spines["bottom"].set_color("#d9d9d9")
        _ax.tick_params(axis="both", colors="#555555", length=0)
        _ax.legend(
            loc="lower center",
            bbox_to_anchor=(0.5, -0.18),
            ncol=4,
            frameon=False,
            fontsize=10,
        )
        _fig.tight_layout()
        return _fig

    def _latest_change(_data, _provider):
        _provider_data = _data.filter(pl.col("tilbyder") == _provider).sort("ar")
        _periods = _provider_data["ar"].to_list()
        _values = _provider_data["markedsandel"].to_list()
        if len(_values) < 2:
            return None
        return {
            "previous_period": _periods[-2],
            "current_period": _periods[-1],
            "previous": _values[-2],
            "current": _values[-1],
            "delta": _values[-1] - _values[-2],
        }

    def _direction(_change):
        if _change["delta"] > 0.05:
            return "øker"
        if _change["delta"] < -0.05:
            return "går ned"
        return "er om lag uendret"

    def _pair_text(_provider):
        _ab = _latest_change(market_share_abonnement, _provider)
        _om = _latest_change(market_share_omsetning, _provider)
        if _ab is None or _om is None:
            return ""
        return (
            f"<strong>{_provider}</strong> {_direction(_om)} i omsetningsandel "
            f"(<strong>{_percent(_om['previous'])}→{_percent(_om['current'])}</strong>) "
            f"og {_direction(_ab)} i abonnementsandel "
            f"(<strong>{_percent(_ab['previous'])}→{_percent(_ab['current'])}</strong>)."
        )

    def _last_two_periods():
        _all_years = sorted(
            set(
                market_share_abonnement["ar"].to_list()
                + market_share_omsetning["ar"].to_list()
            )
        )
        if len(_all_years) < 2:
            return None, None
        return _all_years[-2], _all_years[-1]

    _prev_period, _curr_period = _last_two_periods()
    _period_text = (
        f"Endring fra {_prev_period} til {_curr_period}"
        if _prev_period is not None and _curr_period is not None
        else "Endring mellom siste perioder"
    )

    _abonnement_fig = _plot_market_share(market_share_abonnement, 60)
    _omsetning_fig = _plot_market_share(market_share_omsetning, 60)
    _abonnement_export = excel_download(
        market_share_abonnement,
        "figur-1-abonnement.xlsx",
        "Figur 1 - Markedsandeler basert på abonnement",
        "Abonnement",
    )
    _omsetning_export = excel_download(
        market_share_omsetning,
        "figur-1-omsetning.xlsx",
        "Figur 1 - Markedsandeler basert på omsetning",
        "Omsetning",
    )

    _summary = mo.Html(
        f"""
        <div style="
            margin: 8px auto 0;
            max-width: 820px;
            padding: 18px 26px;
            border: 1px solid #0b2b66;
            border-radius: 28px;
            background: #f6c7a7;
            color: #000;
            font-size: 1.05rem;
            line-height: 1.45;
            text-align: center;
        ">
            <div style="margin: 0 0 12px; font-size: 1.2rem; font-weight: 700;">{_period_text}</div>
            {_pair_text("Lyse Tele (Ice)")}<br>
            {_pair_text("Telenor")}<br>
            {_pair_text("Telia")}<br>
            {_pair_text("Øvrige")}
        </div>
        """
    )

    mo.vstack(
        [
            mo.hstack(
                [
                    mo.vstack(
                        [
                            mo.Html(
                                '<div style="font-size: 1.25rem; font-weight: 700; margin-bottom: 8px;">Basert på abonnement</div>'
                            ),
                            _abonnement_export,
                            _abonnement_fig,
                        ],
                        gap=0.5,
                    ),
                    mo.vstack(
                        [
                            mo.Html(
                                '<div style="font-size: 1.25rem; font-weight: 700; margin-bottom: 8px;">Basert på omsetning</div>'
                            ),
                            _omsetning_export,
                            _omsetning_fig,
                        ],
                        gap=0.5,
                    ),
                ],
                justify="center",
                gap=2,
            ),
            _summary,
        ],
        gap=2,
    )
    return


@app.cell
def _(mo):
    mo.Html(
        """
        <div style="
            width: 100%;
            margin: 46px 0 24px;
            border-top: 3px solid #0b2b66;
        "></div>
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 2 - Lineær trend i markedsandeler
    """)
    return


@app.cell
def _(market_share_abonnement, market_share_omsetning, pl):
    def _linear_projection(_data, _periods_ahead=3):
        _rows = []
        for _provider in ["Telenor", "Telia", "Lyse Tele (Ice)", "Øvrige"]:
            _provider_data = _data.filter(pl.col("tilbyder") == _provider).sort("ar")
            if _provider_data.height < 2:
                continue

            _xs = [float(_x) for _x in _provider_data["ar"].to_list()]
            _ys = [float(_y) for _y in _provider_data["markedsandel"].to_list()]
            _x_mean = sum(_xs) / len(_xs)
            _y_mean = sum(_ys) / len(_ys)
            _denominator = sum((_x - _x_mean) ** 2 for _x in _xs)
            _slope = (
                sum((_x - _x_mean) * (_y - _y_mean) for _x, _y in zip(_xs, _ys))
                / _denominator
                if _denominator
                else 0
            )
            _intercept = _y_mean - _slope * _x_mean
            _last_year = int(max(_xs))

            for _year in range(int(min(_xs)), _last_year + _periods_ahead + 1):
                _rows.append(
                    {
                        "ar": _year,
                        "tilbyder": _provider,
                        "markedsandel": _intercept + _slope * _year,
                    }
                )

        return pl.DataFrame(_rows)

    market_share_abonnement_projection = _linear_projection(market_share_abonnement)
    market_share_omsetning_projection = _linear_projection(market_share_omsetning)
    return (
        market_share_abonnement_projection,
        market_share_omsetning_projection,
    )


@app.cell
def _(
    excel_download,
    market_share_abonnement,
    market_share_abonnement_projection,
    market_share_omsetning,
    market_share_omsetning_projection,
    mo,
    pl,
    plt,
):
    _colors = {
        "Telenor": "#156082",
        "Telia": "#7030a0",
        "Lyse Tele (Ice)": "#ffc000",
        "Øvrige": "#00b050",
    }
    _order = ["Telenor", "Telia", "Lyse Tele (Ice)", "Øvrige"]

    def _percent(_value):
        return f"{_value:.1f} %".replace(".", ",")

    def _plot_projection(_actual, _projection, _title, _upper_y):
        _fig, _ax = plt.subplots(figsize=(7.8, 4.8), dpi=120)
        _last_actual_year = int(_actual["ar"].max())

        for _provider in _order:
            _actual_provider = _actual.filter(pl.col("tilbyder") == _provider).sort("ar")
            _projection_provider = _projection.filter(pl.col("tilbyder") == _provider).sort("ar")
            if _actual_provider.is_empty() or _projection_provider.is_empty():
                continue

            _actual_xs = _actual_provider["ar"].to_list()
            _actual_ys = _actual_provider["markedsandel"].to_list()
            _projection_xs = _projection_provider["ar"].to_list()
            _projection_ys = _projection_provider["markedsandel"].to_list()

            _ax.plot(
                _actual_xs,
                _actual_ys,
                color=_colors[_provider],
                linewidth=2.5,
                solid_capstyle="round",
                label=_provider,
            )
            _ax.plot(
                _projection_xs,
                _projection_ys,
                color=_colors[_provider],
                linewidth=1.8,
                linestyle=":",
                label=f"Lineær ({_provider})",
            )

            _latest_actual = _actual_provider.filter(pl.col("ar") == _last_actual_year)
            if not _latest_actual.is_empty():
                _ax.annotate(
                    _percent(_latest_actual["markedsandel"][0]),
                    xy=(_last_actual_year, _latest_actual["markedsandel"][0]),
                    xytext=(8, 7),
                    textcoords="offset points",
                    color="#404040",
                    fontsize=8,
                )

            _ax.annotate(
                _percent(_projection_ys[-1]),
                xy=(_projection_xs[-1], _projection_ys[-1]),
                xytext=(8, 0),
                textcoords="offset points",
                color="#202020",
                fontsize=8,
                bbox={
                    "boxstyle": "square,pad=0.35",
                    "facecolor": "white",
                    "edgecolor": _colors[_provider],
                    "linewidth": 0.8,
                },
            )

        _ax.set_title(_title, fontsize=10, fontweight="bold", pad=12)
        _ax.set_ylim(0, _upper_y)
        _ax.set_yticks(range(0, _upper_y + 1, 10))
        _ax.set_yticklabels([_percent(_value) for _value in range(0, _upper_y + 1, 10)])
        _ax.set_xticks(sorted(_projection["ar"].unique().to_list()))
        _ax.grid(axis="y", color="#d9d9d9", linewidth=0.8)
        _ax.grid(axis="x", visible=False)
        _ax.spines[["top", "right", "left"]].set_visible(False)
        _ax.spines["bottom"].set_color("#d9d9d9")
        _ax.tick_params(axis="both", colors="#555555", length=0)
        _ax.legend(
            loc="lower center",
            bbox_to_anchor=(0.5, -0.26),
            ncol=4,
            frameon=False,
            fontsize=8,
        )
        _fig.tight_layout()
        return _fig

    def _threshold_text(_data, _provider, _threshold):
        _provider_data = _data.filter(pl.col("tilbyder") == _provider).sort("ar")
        _xs = [float(_x) for _x in _provider_data["ar"].to_list()]
        _ys = [float(_y) for _y in _provider_data["markedsandel"].to_list()]
        _x_mean = sum(_xs) / len(_xs)
        _y_mean = sum(_ys) / len(_ys)
        _denominator = sum((_x - _x_mean) ** 2 for _x in _xs)
        _slope = (
            sum((_x - _x_mean) * (_y - _y_mean) for _x, _y in zip(_xs, _ys))
            / _denominator
            if _denominator
            else 0
        )
        if _slope <= 0:
            return f"Lyse Tele (Ice) når ikke {_threshold:.0f} % omsetningsandel med lineær trend."
        _year = (_threshold - (_y_mean - _slope * _x_mean)) / _slope
        return f"Lyse Tele (Ice) når {_threshold:.0f} % av omsetningen rundt {int(_year + 0.999)}."

    def _projection_export_data(_actual, _projection):
        _actual_export = _actual.with_columns(pl.lit("Historikk").alias("serie"))
        _projection_export = _projection.with_columns(pl.lit("Lineær trend").alias("serie"))
        return (
            pl.concat([_actual_export, _projection_export])
            .select("serie", "ar", "tilbyder", "markedsandel")
            .sort("serie", "ar", "tilbyder")
        )

    _abonnement_projection_fig = _plot_projection(
        market_share_abonnement,
        market_share_abonnement_projection,
        "Abonnement",
        60,
    )
    _omsetning_projection_fig = _plot_projection(
        market_share_omsetning,
        market_share_omsetning_projection,
        "Omsetning",
        60,
    )
    _abonnement_projection_export = excel_download(
        _projection_export_data(market_share_abonnement, market_share_abonnement_projection),
        "figur-2-abonnement-trend.xlsx",
        "Figur 2 - Lineær trend basert på abonnement",
        "Abonnement trend",
    )
    _omsetning_projection_export = excel_download(
        _projection_export_data(market_share_omsetning, market_share_omsetning_projection),
        "figur-2-omsetning-trend.xlsx",
        "Figur 2 - Lineær trend basert på omsetning",
        "Omsetning trend",
    )
    _forecast_note = mo.Html(
        f"""
        <div style="
            margin: 18px auto 0;
            width: fit-content;
            max-width: 520px;
            padding: 22px 44px;
            border: 1px solid #0b2b66;
            border-radius: 999px;
            background: #c9570d;
            color: white;
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.35;
            text-align: center;
        ">
            {_threshold_text(market_share_omsetning, "Lyse Tele (Ice)", 20)}
        </div>
        """
    )

    mo.vstack(
        [
            mo.hstack(
                [
                    mo.vstack([_abonnement_projection_export, _abonnement_projection_fig], gap=0.5),
                    mo.vstack([_omsetning_projection_export, _omsetning_projection_fig], gap=0.5),
                ],
                justify="center",
                gap=2,
            ),
            _forecast_note,
        ],
        gap=1,
    )
    return


@app.cell
def _(mo):
    mo.Html(
        """
        <div style="
            width: 100%;
            margin: 46px 0 24px;
            border-top: 3px solid #0b2b66;
        "></div>
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## 3 - Abonnement fordelt på privat og bedrift
    """)
    return


@app.cell
def _(df, pl):
    _provider_name = pl.col("fusnavn").str.to_lowercase()
    _provider_group = (
        pl.when(_provider_name.str.contains("telenor"))
        .then(pl.lit("Telenor"))
        .when(_provider_name.str.contains("telia"))
        .then(pl.lit("Telia"))
        .when(
            _provider_name.is_in(["ice communication norge", "lyse tele"])
            | _provider_name.str.contains("lyse")
            | _provider_name.str.contains("ice")
        )
        .then(pl.lit("Lyse Tele (Ice)"))
        .otherwise(pl.lit("Øvrige"))
    )

    market_share_abonnement_segment = (
        df.filter(
            (pl.col("dk") == "Mobiltelefoni")
            & (pl.col("hg") == "Abonnement")
            & (pl.col("ms").is_in(["Privat", "Bedrift"]))
            & (pl.col("n1").is_in(["Fakturert", "Kontantkort"]))
            & (pl.col("n2") == "Ingen")
            & (pl.col("tp") == "Sum")
            & (pl.col("sk") == "Sluttbruker")
            & (pl.col("delar") == "Helår")
        )
        .with_columns(tilbyder=_provider_group)
        .group_by("ar", "ms", "tilbyder")
        .agg(pl.col("svar").sum().alias("abonnement"))
        .with_columns(
            markedsandel=pl.col("abonnement")
            * 100
            / pl.col("abonnement").sum().over(["ar", "ms"])
        )
        .select("ar", "ms", "tilbyder", "markedsandel")
        .sort("ms", "ar", "tilbyder")
        .collect()
    )
    return (market_share_abonnement_segment,)


@app.cell
def _(excel_download, market_share_abonnement_segment, mo, pl, plt):
    _colors = {
        "Telenor": "#156082",
        "Telia": "#7030a0",
        "Lyse Tele (Ice)": "#ffc000",
        "Øvrige": "#00b050",
    }
    _order = ["Telenor", "Telia", "Lyse Tele (Ice)", "Øvrige"]

    def _percent(_value):
        return f"{_value:.1f} %".replace(".", ",")

    def _plot_segment(_segment, _upper_y=60):
        _data = market_share_abonnement_segment.filter(pl.col("ms") == _segment)
        _fig, _ax = plt.subplots(figsize=(7.2, 4.8), dpi=120)

        for _provider in _order:
            _provider_data = _data.filter(pl.col("tilbyder") == _provider).sort("ar")
            if _provider_data.is_empty():
                continue

            _xs = _provider_data["ar"].to_list()
            _ys = _provider_data["markedsandel"].to_list()
            _ax.plot(
                _xs,
                _ys,
                color=_colors[_provider],
                linewidth=3.0,
                solid_capstyle="round",
                label=_provider,
            )

            if len(_ys) >= 2:
                _ax.annotate(
                    _percent(_ys[-2]),
                    xy=(_xs[-2], _ys[-2]),
                    xytext=(8, 7),
                    textcoords="offset points",
                    color="#404040",
                    fontsize=9,
                )
            _ax.annotate(
                _percent(_ys[-1]),
                xy=(_xs[-1], _ys[-1]),
                xytext=(10, 0),
                textcoords="offset points",
                color="#404040",
                fontsize=9,
            )

        _ax.set_ylim(0, _upper_y)
        _ax.set_yticks(range(0, _upper_y + 1, 10))
        _ax.set_yticklabels([_percent(_value) for _value in range(0, _upper_y + 1, 10)])
        _ax.set_xticks(sorted(_data["ar"].unique().to_list()))
        _ax.grid(axis="y", color="#d9d9d9", linewidth=0.8)
        _ax.grid(axis="x", visible=False)
        _ax.spines[["top", "right", "left"]].set_visible(False)
        _ax.spines["bottom"].set_color("#d9d9d9")
        _ax.tick_params(axis="both", colors="#555555", length=0)
        _ax.legend(
            loc="lower center",
            bbox_to_anchor=(0.5, -0.22),
            ncol=4,
            frameon=False,
            fontsize=10,
        )
        _fig.tight_layout()
        return _fig

    def _latest_change(_segment, _provider):
        _provider_data = (
            market_share_abonnement_segment.filter(
                (pl.col("ms") == _segment) & (pl.col("tilbyder") == _provider)
            )
            .sort("ar")
        )
        _periods = _provider_data["ar"].to_list()
        _values = _provider_data["markedsandel"].to_list()
        if len(_values) < 2:
            return None
        return {
            "previous": _values[-2],
            "current": _values[-1],
            "delta": _values[-1] - _values[-2],
        }

    def _direction(_change):
        if _change["delta"] > 0.05:
            return "øker"
        if _change["delta"] < -0.05:
            return "går ned"
        return "er stabil"

    def _segment_text(_provider):
        _private = _latest_change("Privat", _provider)
        _business = _latest_change("Bedrift", _provider)
        if _private is None or _business is None:
            return ""
        return (
            f"<strong>{_provider}</strong> {_direction(_private)} i privatmarkedet "
            f"(<strong>{_percent(_private['previous'])}→{_percent(_private['current'])}</strong>) "
            f"og {_direction(_business)} i bedriftsmarkedet "
            f"(<strong>{_percent(_business['previous'])}→{_percent(_business['current'])}</strong>)."
        )

    def _last_two_periods():
        _years = sorted(market_share_abonnement_segment["ar"].unique().to_list())
        if len(_years) < 2:
            return None, None
        return _years[-2], _years[-1]

    _prev_period, _curr_period = _last_two_periods()
    _period_text = (
        f"Endring fra {_prev_period} til {_curr_period}"
        if _prev_period is not None and _curr_period is not None
        else "Endring mellom siste perioder"
    )
    _private_fig = _plot_segment("Privat", 50)
    _business_fig = _plot_segment("Bedrift")
    _private_export = excel_download(
        market_share_abonnement_segment.filter(pl.col("ms") == "Privat"),
        "figur-3-privat.xlsx",
        "Figur 3 - Abonnement i privatmarkedet",
        "Privat",
    )
    _business_export = excel_download(
        market_share_abonnement_segment.filter(pl.col("ms") == "Bedrift"),
        "figur-3-bedrift.xlsx",
        "Figur 3 - Abonnement i bedriftsmarkedet",
        "Bedrift",
    )
    _summary = mo.Html(
        f"""
        <div style="
            margin: 8px auto 0;
            max-width: 820px;
            padding: 18px 26px;
            border: 1px solid #0b2b66;
            border-radius: 28px;
            background: #dcefd2;
            color: #000;
            font-size: 1.05rem;
            line-height: 1.45;
            text-align: center;
        ">
            <div style="margin: 0 0 12px; font-size: 1.2rem; font-weight: 700;">{_period_text}</div>
            {_segment_text("Lyse Tele (Ice)")}<br>
            {_segment_text("Telenor")}<br>
            {_segment_text("Telia")}<br>
            {_segment_text("Øvrige")}
        </div>
        """
    )

    mo.vstack(
        [
            mo.hstack(
                [
                    mo.vstack(
                        [
                            mo.Html(
                                '<div style="font-size: 1.25rem; font-weight: 700; margin-bottom: 8px;">Privat</div>'
                            ),
                            _private_export,
                            _private_fig,
                        ],
                        gap=0.5,
                    ),
                    mo.vstack(
                        [
                            mo.Html(
                                '<div style="font-size: 1.25rem; font-weight: 700; margin-bottom: 8px;">Bedrift</div>'
                            ),
                            _business_export,
                            _business_fig,
                        ],
                        gap=0.5,
                    ),
                ],
                justify="center",
                gap=2,
            ),
            _summary,
        ],
        gap=2,
    )
    return


if __name__ == "__main__":
    app.run()
