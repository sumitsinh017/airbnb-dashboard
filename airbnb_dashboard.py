# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "altair",
#     "marimo",
#     "numpy",
#     "openpyxl",
#     "pandas",
#     "pingouin",
# ]
# ///
import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import altair as alt
    import numpy as np
    import pingouin as pg

    return alt, mo, np, pd, pg


@app.cell
def _(pd):
    base_url = "https://docs.google.com/spreadsheets/d/"
    doc_id = "1ecopK6oyyb4d_7-QLrCr8YlgFrCetHU7-VQfnYej7JY/"
    format_doc = "export/format=excel"

    url = base_url + doc_id + format_doc

    excel_file = pd.ExcelFile(url)
    return (excel_file,)


@app.cell
def _(excel_file, pd):
    dfs = []

    for sheet in excel_file.sheet_names:
        _df = excel_file.parse(sheet)
        _df["city"] = sheet.split("_")[0]
        _df["type_of_day"] = sheet.split("_")[1]
        dfs.append(_df)

    df = pd.concat(dfs, ignore_index=True)
    return (df,)


@app.cell
def _():
    return


@app.cell
def _(df, np, pd):
    ### written entirely by AI
    # Prepare a copy of the data: log price and categorical versions of the variables
    df_model = df.copy()
    df_model["log_price"] = np.log(df_model["realSum"])
    df_model["city"] = df_model["city"].str.title()
    df_model["type_of_day"] = (
        df_model["type_of_day"].str.title().str.rstrip("s")
    )  # weekdays -> Weekday
    df_model["superhost"] = df_model["host_is_superhost"].map(
        {True: "Superhost", False: "Not superhost"}
    )
    df_model["capacity"] = df_model["person_capacity"].astype(str) + " guests"
    df_model["dist_band"] = pd.cut(
        df_model["dist"],
        bins=[0, 1, 3, 6, np.inf],
        labels=["< 1 km", "1–3 km", "3–6 km", "> 6 km"],
        right=False,
    ).astype(str)

    factor_labels = {
        "city": "City",
        "room_type": "Room type",
        "capacity": "Guest capacity",
        "dist_band": "Distance to centre",
        "superhost": "Superhost status",
        "type_of_day": "Weekday vs weekend",
    }
    # natural order for ordered variables (others are sorted by median price)
    factor_orders = {
        "capacity": [f"{i} guests" for i in range(2, 7)],
        "dist_band": ["< 1 km", "1–3 km", "3–6 km", "> 6 km"],
    }
    return df_model, factor_labels, factor_orders


@app.cell
def _(np):
    ### written entirely by AI
    def size_label(x):
        # rough guide from the README: 0.01 small, 0.06 medium, 0.14 large
        if x is None or np.isnan(x):
            return "n/a"
        if x < 0.01:
            return "negligible"
        if x < 0.06:
            return "small"
        if x < 0.14:
            return "medium"
        return "large"

    def fmt_p(p):
        return "< 0.001" if p < 0.001 else f"{p:.3f}"

    def pcol(t):
        # newer pingouin versions call the column "p_unc", older ones "p-unc"
        return "p_unc" if "p_unc" in t.columns else "p-unc"

    return fmt_p, pcol, size_label


@app.cell
def _(mo):
    ### written entirely by AI
    mo.md(
        """
    # Group 6 · What drives Airbnb prices in Europe?

    **Members:** Shreenath Shreepathi Hebbar, Sumitsinh Dharmendrasinh Rahevar

    Henrik asked which variables explain the variation in Airbnb prices across ten
    European cities. This dashboard has four short sections: the data, boxplots you
    can explore, ANOVA to rank the variables, and a two-way ANOVA to test interactions.

    **Variables chosen and why**

    - **City**: Henrik's main question; ten very different markets.
    - **Room type**: entire home vs. private vs. shared room, a very visible price driver.
    - **Guest capacity**: a simple proxy for the size of the listing.
    - **Distance to centre**: location, put into four distance bands (ANOVA needs groups).
    - **Superhost status**: a quality signal of the host.
    - **Weekday vs. weekend**: whether the offer is for a weekday or a weekend.

    Left out: ratings and the attraction/restaurant indices (continuous, and they
    overlap with distance and city) and the number of bedrooms (overlaps with capacity).
    """
    )
    return


@app.cell
def _(alt, df_model, mo, np, pd):
    ### written entirely by AI
    _raw, _e1 = np.histogram(df_model["realSum"].clip(upper=1000), bins=40)
    _log, _e2 = np.histogram(df_model["log_price"], bins=40)
    _h1 = pd.DataFrame({"left": _e1[:-1], "right": _e1[1:], "count": _raw})
    _h2 = pd.DataFrame({"left": _e2[:-1], "right": _e2[1:], "count": _log})

    _c1 = (
        alt.Chart(_h1)
        .mark_bar()
        .encode(
            alt.X("left:Q", title="Price per night (€, capped at 1000)"),
            alt.X2("right:Q"),
            alt.Y("count:Q", title="Listings"),
        )
        .properties(width=330, height=220, title="Price: strongly right-skewed")
    )
    _c2 = (
        alt.Chart(_h2)
        .mark_bar()
        .encode(
            alt.X("left:Q", title="log(price)"),
            alt.X2("right:Q"),
            alt.Y("count:Q", title="Listings"),
        )
        .properties(width=330, height=220, title="log(price): roughly symmetric")
    )

    _skew_raw = df_model["realSum"].skew()
    _skew_log = df_model["log_price"].skew()

    mo.vstack(
        [
            mo.md(
                f"""
    ## 1 · The data

    The dataset has **{len(df_model):,} listings** from 10 cities (weekday and weekend offers).
    Prices are very skewed (skewness {_skew_raw:.1f}), so all tests below use
    **log(price)** (skewness {_skew_log:.1f}). Boxplots show the original price in €.
    """
            ),
            mo.hstack([_c1, _c2], justify="start", wrap=True),
        ]
    )
    return


@app.cell
def _(factor_labels, mo):
    ### written entirely by AI
    factor_ui = mo.ui.dropdown(
        options={v: k for k, v in factor_labels.items()},
        value="City",
        label="Group prices by",
    )
    return (factor_ui,)


@app.cell
def _(df_model, mo):
    ### written entirely by AI
    _cities = sorted(df_model["city"].unique())
    city_ui = mo.ui.multiselect(options=_cities, value=_cities, label="Cities")
    scale_ui = mo.ui.radio(
        options=["Log scale", "Linear scale"], value="Log scale", label="Price axis"
    )
    return city_ui, scale_ui


@app.cell
def _(alt, city_ui, df_model, factor_labels, factor_orders, factor_ui, mo, scale_ui):
    ### written entirely by AI
    _col = factor_ui.value
    _data = df_model[df_model["city"].isin(city_ui.value)]
    _controls = mo.hstack([factor_ui, scale_ui, city_ui], justify="start", wrap=True)

    if _data.empty:
        box_out = mo.vstack(
            [
                _controls,
                mo.callout(
                    "No listings match this selection. Please select at least one city.",
                    kind="warn",
                ),
            ]
        )
    else:
        # pre-computed box statistics keep the chart small (no 50k rows in the browser)
        _st = _data.groupby(_col)["realSum"].agg(
            q1=lambda x: x.quantile(0.25),
            median="median",
            q3=lambda x: x.quantile(0.75),
        ).reset_index()
        _st["iqr"] = _st["q3"] - _st["q1"]
        _m = _data[[_col, "realSum"]].merge(_st, on=_col)
        _inside = (_m["realSum"] >= _m["q1"] - 1.5 * _m["iqr"]) & (
            _m["realSum"] <= _m["q3"] + 1.5 * _m["iqr"]
        )
        _wh = (
            _m[_inside].groupby(_col)["realSum"].agg(low="min", high="max").reset_index()
        )
        _st = _st.merge(_wh, on=_col)
        # outliers: show at most 150 random ones per group
        _out = (
            _m[~_inside][[_col, "realSum"]]
            .sample(frac=1, random_state=0)
            .groupby(_col)
            .head(150)
        )
        _order = factor_orders.get(_col) or _st.sort_values("median")[_col].tolist()
        _scale = alt.Scale(type="log" if scale_ui.value == "Log scale" else "linear")
        _x = alt.X(f"{_col}:N", title=factor_labels[_col], sort=_order)
        _ytitle = "Price per night (€)"
        _base = alt.Chart(_st).encode(x=_x)
        _whisk = _base.mark_rule().encode(
            y=alt.Y("low:Q", scale=_scale, title=_ytitle), y2="high:Q"
        )
        _box = _base.mark_bar(size=40).encode(
            y=alt.Y("q1:Q", scale=_scale), y2="q3:Q",
            color=alt.Color(f"{_col}:N", legend=None),
        )
        _med = _base.mark_tick(color="white", size=40, thickness=2).encode(
            y=alt.Y("median:Q", scale=_scale)
        )
        _pts = (
            alt.Chart(_out)
            .mark_circle(size=12, opacity=0.4, color="gray")
            .encode(x=_x, y=alt.Y("realSum:Q", scale=_scale))
        )
        _chart = (_whisk + _box + _med + _pts).properties(width=650, height=380)
        box_out = mo.vstack(
            [
                _controls,
                _chart,
                mo.md(
                    f"Boxes show the middle 50 % of prices, the line is the median, "
                    f"dots are a sample of outliers. {len(_data):,} listings used."
                ),
            ]
        )

    mo.vstack([mo.md("## 2 · Explore prices with boxplots"), box_out])
    return (box_out,)


@app.cell
def _(df_model, factor_labels, pcol, pd, pg):
    ### written entirely by AI
    # one-way ANOVA for every chosen variable; Welch ANOVA if variances are unequal
    _rows = []
    for _f, _label in factor_labels.items():
        _lev = pg.homoscedasticity(
            data=df_model, dv="log_price", group=_f, method="levene"
        )
        _p_lev = float(_lev["pval"].iloc[0])
        if _p_lev < 0.05:
            _t = pg.welch_anova(data=df_model, dv="log_price", between=_f)
            _test = "Welch ANOVA"
        else:
            _t = pg.anova(data=df_model, dv="log_price", between=_f, detailed=True)
            _test = "One-way ANOVA"
        _r = _t.iloc[0]
        _rows.append(
            {
                "key": _f,
                "label": _label,
                "test": _test,
                "p_lev": _p_lev,
                "F": float(_r["F"]),
                "p": float(_t[pcol(_t)].iloc[0]),
                "np2": float(_r["np2"]),
            }
        )
    oneway = (
        pd.DataFrame(_rows).sort_values("np2", ascending=False).reset_index(drop=True)
    )
    return (oneway,)


@app.cell
def _(alt, df_model, fmt_p, mo, np, oneway, pd, size_label):
    ### written entirely by AI
    _show = pd.DataFrame(
        {
            "Variable": oneway["label"],
            "Test used": oneway["test"],
            "Levene p": oneway["p_lev"].map(fmt_p),
            "F": oneway["F"].round(1),
            "p": oneway["p"].map(fmt_p),
            "np2": oneway["np2"].round(3),
            "Effect size": oneway["np2"].map(size_label),
        }
    )

    _bar = (
        alt.Chart(oneway)
        .mark_bar()
        .encode(
            x=alt.X("np2:Q", title="Partial eta squared (np2): share of explained variation"),
            y=alt.Y("label:N", sort="-x", title=None),
            tooltip=["label", alt.Tooltip("np2:Q", format=".3f")],
        )
        .properties(width=500, height=200)
    )

    _top = oneway.iloc[0]
    _second = oneway.iloc[1]
    _gm = np.exp(df_model.groupby(_top["key"])["log_price"].mean()).sort_values()
    _n_welch = int((oneway["test"] == "Welch ANOVA").sum())

    _interp = f"""
    **In plain words:** **{_top['label']}** matters most. It explains about
    **{_top['np2']:.0%}** of the price variation ({size_label(_top['np2'])} effect,
    np2 = {_top['np2']:.3f}), followed by **{_second['label']}**
    (np2 = {_second['np2']:.3f}, {size_label(_second['np2'])}). Typical prices
    (geometric mean) are highest for **{_gm.index[-1]}** (about {_gm.iloc[-1]:.0f} €) and
    lowest for **{_gm.index[0]}** (about {_gm.iloc[0]:.0f} €). Variables with a tiny
    np2 are statistically significant in many cases only because there are so many listings.

    **Which test?** Levene's test for equal variances was significant (p < 0.05) for
    {_n_welch} of {len(oneway)} variables, so **Welch ANOVA** was used there because it does not
    assume equal variances; the normal one-way ANOVA was used for the others.
    """

    mo.vstack(
        [
            mo.md(
                """
    ## 3 · One-way ANOVA: which variables matter?

    **H0 (for every variable):** the mean log price is the same in all groups of that variable
    (for example, in all cities). The larger np2, the more price variation the variable explains.
    """
            ),
            mo.ui.table(_show, selection=None, page_size=10),
            _bar,
            mo.md(_interp),
        ]
    )
    return


@app.cell
def _(factor_labels, mo):
    ### written entirely by AI
    assump_ui = mo.ui.dropdown(
        options={v: k for k, v in factor_labels.items()},
        value="City",
        label="Check assumptions for",
    )
    return (assump_ui,)


@app.cell
def _(assump_ui, df_model, fmt_p, mo, np, pcol, pd, pg):
    ### written entirely by AI
    _f = assump_ui.value

    _sizes = (
        df_model.groupby(_f)["log_price"]
        .agg(n="size", skew="skew")
        .reset_index()
        .rename(columns={_f: "group"})
    )
    _norm = (
        pg.normality(df_model, dv="log_price", group=_f, method="normaltest")
        .rename_axis("group")
        .reset_index()[["group", "pval"]]
        .rename(columns={"pval": "normality p"})
    )
    _tab = _sizes.merge(_norm, on="group")

    _lev = pg.homoscedasticity(data=df_model, dv="log_price", group=_f, method="levene")
    _p_lev = float(_lev["pval"].iloc[0])
    _kw = pg.kruskal(data=df_model, dv="log_price", between=_f)
    _h = float(_kw["H"].iloc[0])
    _p_kw = float(_kw[pcol(_kw)].iloc[0])

    _ratio = _tab["n"].max() / _tab["n"].min()
    _max_skew = _tab["skew"].abs().max()

    _show = pd.DataFrame(
        {
            "Group": _tab["group"],
            "Listings (n)": _tab["n"],
            "Skewness of log price": _tab["skew"].round(2),
            "Normality p": _tab["normality p"].map(fmt_p),
        }
    )

    _size_txt = (
        f"The largest group is **{_ratio:.0f} times** bigger than the smallest, so the ANOVA "
        "is quite sensitive to unequal variances here."
        if _ratio > 3
        else f"Group sizes are similar (largest/smallest = {_ratio:.1f})."
    )
    _norm_txt = (
        f"With thousands of listings the normality test almost always rejects, so we look at "
        f"the skewness: the largest absolute value is {_max_skew:.2f}, "
        + (
            "so log price is roughly symmetric within groups."
            if _max_skew < 1
            else "so some groups are still clearly skewed; read those results with care."
        )
    )
    _var_txt = (
        f"Levene's test: p = {fmt_p(_p_lev)} → variances are **not equal**, so we use "
        "**Welch ANOVA** instead of the normal ANOVA."
        if _p_lev < 0.05
        else f"Levene's test: p = {fmt_p(_p_lev)} → variances are similar, so the normal "
        "one-way ANOVA is fine."
    )

    mo.vstack(
        [
            mo.md(
                """
    ## 4 · Can we trust the ANOVA? Assumption checks

    - **Independence:** each listing is one observation; we assume listings do not depend on each other.
      Weekday and weekend offers cannot be paired (no listing ID), so they are treated as independent groups.
    - **Normality, equal variances, group sizes:** pick a variable to check.
    """
            ),
            assump_ui,
            mo.ui.table(_show, selection=None, page_size=12),
            mo.md(
                f"""
    - **Normality:** {_norm_txt}
    - **Equal variances (H0: all group variances are equal):** {_var_txt}
    - **Group sizes:** {_size_txt}
    - **Robustness check:** the rank-based Kruskal-Wallis test (H0: the groups have the same
      price distribution) gives H = {_h:.0f}, p = {fmt_p(_p_kw)}, which
      {"agrees with" if _p_kw < 0.05 else "differs from"} the Welch/ANOVA conclusion.
    """
            ),
        ]
    )
    return


@app.cell
def _(factor_labels, mo):
    ### written entirely by AI
    _opts = {v: k for k, v in factor_labels.items()}
    factor_a_ui = mo.ui.dropdown(options=_opts, value="City", label="Factor A")
    factor_b_ui = mo.ui.dropdown(options=_opts, value="Room type", label="Factor B")
    return factor_a_ui, factor_b_ui


@app.cell
def _(
    alt,
    df_model,
    factor_a_ui,
    factor_b_ui,
    factor_labels,
    factor_orders,
    fmt_p,
    mo,
    np,
    pcol,
    pd,
    pg,
    size_label,
):
    ### written entirely by AI
    _a = factor_a_ui.value
    _b = factor_b_ui.value
    _la = factor_labels[_a]
    _lb = factor_labels[_b]
    _controls = mo.hstack([factor_a_ui, factor_b_ui], justify="start")
    _head = mo.md("## 5 · Two-way ANOVA: do the effects depend on each other?")

    _tab = None
    if _a != _b:
        try:
            _tab = pg.anova(data=df_model, dv="log_price", between=[_a, _b], detailed=True)
        except Exception:
            _tab = None

    if _a == _b:
        twoway_out = mo.vstack(
            [
                _head,
                _controls,
                mo.callout("Please choose two different variables.", kind="warn"),
            ]
        )
    elif _tab is None:
        twoway_out = mo.vstack(
            [
                _head,
                _controls,
                mo.callout(
                    "The two-way ANOVA could not be computed for this combination "
                    "(some groups are empty). Please choose another combination.",
                    kind="warn",
                ),
            ]
        )
    else:
        # table
        _names = {
            _a: _la,
            _b: _lb,
            "Residual": "Residual (unexplained)",
        }
        _show = pd.DataFrame(
            {
                "Source": [
                    f"{_la} × {_lb} (interaction)" if "*" in str(s) else _names.get(s, s)
                    for s in _tab["Source"]
                ],
                "SS": _tab["SS"].round(1),
                "DF": _tab["DF"],
                "F": _tab["F"].round(1).astype(object).where(_tab["F"].notna(), ""),
                "p": [("" if np.isnan(p) else fmt_p(p)) for p in _tab[pcol(_tab)]],
                "np2": _tab["np2"].round(3).astype(object).where(_tab["np2"].notna(), ""),
            }
        )

        # interpretation
        _lines = []
        _mains = []
        for _, _r in _tab.iterrows():
            _src = str(_r["Source"])
            if _src == "Residual":
                continue
            _np2 = float(_r["np2"])
            _p = float(_r[pcol(_tab)])
            if "*" in _src:
                if _p < 0.05:
                    _lines.append(
                        f"- **Interaction:** the price differences between {_la.lower()} groups "
                        f"are not the same for every {_lb.lower()} group (np2 = {_np2:.3f}, "
                        f"{size_label(_np2)}). We reject H0 of no interaction."
                    )
                else:
                    _lines.append(
                        f"- **Interaction:** no clear sign that the effect of {_la.lower()} "
                        f"depends on {_lb.lower()} (p = {fmt_p(_p)}). We cannot reject H0."
                    )
            else:
                _lab = factor_labels.get(_src, _src)
                _mains.append((_lab, _np2))
                if _p < 0.05:
                    _lines.append(
                        f"- **{_lab}:** matters. It explains about {_np2:.0%} of the price variation "
                        f"that stays after the other factors are taken into account "
                        f"(np2 = {_np2:.3f}, {size_label(_np2)}). We reject H0."
                    )
                else:
                    _lines.append(
                        f"- **{_lab}:** no clear effect (p = {fmt_p(_p)}). We cannot reject H0."
                    )
        _stronger = max(_mains, key=lambda m: m[1])[0]

        # assumptions
        _d = df_model[[_a, _b, "log_price"]].copy()
        _d["cell"] = _d[_a] + " | " + _d[_b]
        _p_lev = float(
            pg.homoscedasticity(data=_d, dv="log_price", group="cell", method="levene")[
                "pval"
            ].iloc[0]
        )
        _n = _d.groupby("cell").size()
        _ratio = _n.max() / _n.min()
        _lev_txt = (
            f"Levene's test across all {len(_n)} combinations: p = {fmt_p(_p_lev)} → variances "
            + (
                "are **not equal**. pingouin has no two-way Welch test, so we keep the two-way ANOVA "
                "but read the np2 values as a rough guide and rely on the one-way Welch results above "
                "for the main conclusions."
                if _p_lev < 0.05
                else "are similar, so the two-way ANOVA is appropriate."
            )
        )
        _size_txt = (
            f"Combinations differ a lot in size (from {_n.min()} to {_n.max()} listings), "
            "so the test is more sensitive to unequal variances; combinations with few listings "
            "should be read with care."
            if _ratio > 3
            else f"Combination sizes are similar ({_n.min()} to {_n.max()} listings)."
        )

        # interaction plot (typical price = geometric mean)
        _g = (
            _d.groupby([_a, _b])["log_price"]
            .mean()
            .apply(np.exp)
            .rename("price")
            .reset_index()
        )
        _order = factor_orders.get(_a)
        if not _order:
            _order = (
                _g.groupby(_a)["price"]
                .mean()
                .sort_values(ascending=False)
                .index.tolist()
            )
        _chart = (
            alt.Chart(_g)
            .mark_line(point=True)
            .encode(
                x=alt.X(f"{_a}:N", title=_la, sort=_order),
                y=alt.Y("price:Q", title="Typical price (€, geometric mean)"),
                color=alt.Color(f"{_b}:N", title=_lb),
                tooltip=[_a, _b, alt.Tooltip("price:Q", format=".0f")],
            )
            .properties(width=620, height=340)
        )

        twoway_out = mo.vstack(
            [
                _head,
                mo.md(
                    f"""
    Choose two variables. **H0 (one per row of the table):** no effect of **{_la}**;
    no effect of **{_lb}**; and **no interaction** (the effect of {_la.lower()} does not depend on
    {_lb.lower()}).
    """
                ),
                _controls,
                mo.ui.table(_show, selection=None),
                mo.md("**In plain words:**\n\n" + "\n".join(_lines)
                      + f"\n\nOf the two factors, **{_stronger}** explains more of the price variation."),
                _chart,
                mo.md(
                    "Lines that are not parallel mean an interaction: the price gap between groups "
                    "of one variable changes across the other."
                ),
                mo.md(
                    f"""
    **Assumptions:** listings are treated as independent observations. {_lev_txt} {_size_txt}
    """
                ),
            ]
        )
    twoway_out
    return (twoway_out,)


if __name__ == "__main__":
    app.run()