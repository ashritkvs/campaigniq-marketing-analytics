"""
CampaignIQ — Streamlit marketing analytics dashboard.
Loads marketing_data.csv (same schema as analysis notebook).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Brand palette (consistent with notebook)
PALETTE = ["#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51"]
DATA_PATH = Path(__file__).resolve().parent / "marketing_data.csv"


def _clean_currency(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace(r"[$,]", "", regex=True)
        .replace({"nan": np.nan})
        .astype(float)
    )


@st.cache_data(show_spinner=False)
def load_marketing_data(path: str | Path = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Spend"] = _clean_currency(df["Acquisition_Cost"])
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    # ROI column is treated as percentage return: Revenue = Spend * (1 + ROI/100)
    df["Revenue"] = df["Spend"] * (1 + df["ROI"] / 100.0)
    df["Conversions"] = (df["Conversion_Rate"] * df["Clicks"]).clip(lower=0)
    df["AOV"] = np.where(df["Conversions"] > 0, df["Revenue"] / df["Conversions"], np.nan)
    return df


def channel_metrics(d: pd.DataFrame) -> pd.DataFrame:
    g = d.groupby("Channel_Used", as_index=False).agg(
        Spend=("Spend", "sum"),
        Revenue=("Revenue", "sum"),
        Conversions=("Conversions", "sum"),
        Clicks=("Clicks", "sum"),
    )
    g["ROI_pct"] = np.where(g["Spend"] > 0, (g["Revenue"] - g["Spend"]) / g["Spend"] * 100, np.nan)
    g["Conv_rate"] = np.where(g["Clicks"] > 0, g["Conversions"] / g["Clicks"], np.nan)
    return g


def budget_recommendation(d: pd.DataFrame) -> tuple[pd.DataFrame, float, float, float]:
    """Return channel-level current vs recommended budget % and projected revenue lift."""
    cm = channel_metrics(d)
    total_spend = float(cm["Spend"].sum())
    total_revenue = float(cm["Revenue"].sum())
    if total_spend <= 0 or cm.empty:
        return cm.assign(current_pct=np.nan, recommended_pct=np.nan), total_revenue, total_revenue, 0.0

    cm = cm.copy()
    cm["efficiency"] = np.where(cm["Spend"] > 0, cm["Revenue"] / cm["Spend"], 0.0)
    eff = cm["efficiency"].clip(lower=1e-9)
    raw = eff / eff.sum()
    cm["recommended_pct"] = raw
    cm["current_pct"] = cm["Spend"] / total_spend
    projected = float((total_spend * cm["recommended_pct"] * cm["efficiency"]).sum())
    lift_pct = (projected - total_revenue) / total_revenue * 100 if total_revenue > 0 else 0.0
    return cm, total_revenue, projected, lift_pct


def main() -> None:
    st.set_page_config(
        page_title="CampaignIQ — Marketing Analytics",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if not DATA_PATH.exists():
        st.error(f"Data file not found: {DATA_PATH}")
        st.stop()

    df = load_marketing_data()

    st.title("CampaignIQ — Marketing Analytics Dashboard")
    st.caption("Marketing campaign attribution, ROI, and budget optimization")

    # Sidebar filters
    with st.sidebar:
        st.header("Filters")
        min_d, max_d = df["Date"].min(), df["Date"].max()
        dr = st.date_input(
            "Date range",
            value=(min_d.date(), max_d.date()),
            min_value=min_d.date(),
            max_value=max_d.date(),
        )
        if isinstance(dr, tuple) and len(dr) == 2:
            d0, d1 = pd.Timestamp(dr[0]), pd.Timestamp(dr[1])
        elif hasattr(dr, "year"):  # single date selected
            d0 = d1 = pd.Timestamp(dr)
        else:
            d0, d1 = min_d, max_d

        ctype = st.multiselect(
            "Campaign type",
            options=sorted(df["Campaign_Type"].dropna().unique()),
            default=sorted(df["Campaign_Type"].dropna().unique()),
        )
        channels = st.multiselect(
            "Channels",
            options=sorted(df["Channel_Used"].dropna().unique()),
            default=sorted(df["Channel_Used"].dropna().unique()),
        )
        segments = st.multiselect(
            "Audience segment",
            options=sorted(df["Customer_Segment"].dropna().unique()),
            default=sorted(df["Customer_Segment"].dropna().unique()),
        )

    filt = df[
        (df["Date"] >= d0)
        & (df["Date"] <= d1)
        & (df["Campaign_Type"].isin(ctype))
        & (df["Channel_Used"].isin(channels))
        & (df["Customer_Segment"].isin(segments))
    ]

    if filt.empty:
        st.warning("No rows match the selected filters.")
        st.stop()

    total_spend = float(filt["Spend"].sum())
    total_revenue = float(filt["Revenue"].sum())
    overall_roi = (total_revenue - total_spend) / total_spend * 100 if total_spend > 0 else 0.0
    cm = channel_metrics(filt)
    best_channel = (
        cm.sort_values("ROI_pct", ascending=False).iloc[0]["Channel_Used"]
        if not cm.empty
        else "—"
    )

    # Row 1 — KPI cards
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    r1c1.metric("Total Spend", f"${total_spend:,.0f}")
    r1c2.metric("Total Revenue", f"${total_revenue:,.0f}")
    r1c3.metric("Overall ROI %", f"{overall_roi:.1f}%")
    r1c4.metric("Best Channel (ROI)", best_channel)

    cm_sorted = cm.sort_values("ROI_pct", ascending=True)
    scatter = px.scatter(
        filt,
        x="Spend",
        y="Revenue",
        size="Conversions",
        color="Channel_Used",
        hover_data=["Campaign_Type", "Customer_Segment"],
        color_discrete_sequence=PALETTE,
        title="Spend vs Revenue (bubble size = conversions)",
    )
    scatter.update_layout(height=420, legend_title_text="Channel")

    roi_bar = px.bar(
        cm_sorted,
        x="ROI_pct",
        y="Channel_Used",
        orientation="h",
        color="ROI_pct",
        color_continuous_scale=PALETTE,
        title="Channel ROI % (Revenue − Spend) / Spend × 100",
        labels={"ROI_pct": "ROI %", "Channel_Used": "Channel"},
    )
    roi_bar.update_layout(height=420, showlegend=False)

    # Row 2
    c21, c22 = st.columns(2)
    with c21:
        st.plotly_chart(roi_bar, use_container_width=True)
    with c22:
        st.plotly_chart(scatter, use_container_width=True)

    # Monthly trends
    m = filt.assign(month=filt["Date"].dt.to_period("M").dt.to_timestamp())
    monthly = m.groupby("month", as_index=False).agg(Spend=("Spend", "sum"), Revenue=("Revenue", "sum"))
    trend = go.Figure()
    trend.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=monthly["Spend"],
            name="Spend",
            line=dict(color=PALETTE[0], width=2),
            yaxis="y1",
        )
    )
    trend.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=monthly["Revenue"],
            name="Revenue",
            line=dict(color=PALETTE[1], width=2),
            yaxis="y2",
        )
    )
    trend.update_layout(
        title="Monthly spend vs revenue",
        height=420,
        yaxis=dict(title="Spend ($)", side="left", showgrid=False),
        yaxis2=dict(title="Revenue ($)", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    heat = (
        filt.groupby(["Customer_Segment", "Channel_Used"], as_index=False)
        .agg(roi=("ROI", "mean"))
        .pivot(index="Customer_Segment", columns="Channel_Used", values="roi")
    )
    heatmap = px.imshow(
        heat,
        aspect="auto",
        color_continuous_scale=PALETTE,
        title="Average campaign ROI index by segment × channel",
        labels=dict(x="Channel", y="Segment", color="Avg ROI"),
    )
    heatmap.update_layout(height=420)

    c31, c32 = st.columns(2)
    with c31:
        st.plotly_chart(trend, use_container_width=True)
    with c32:
        st.plotly_chart(heatmap, use_container_width=True)

    # Budget optimization + top campaigns
    bud, _, projected, lift = budget_recommendation(filt)
    bud_plot = go.Figure()
    bud_plot.add_trace(
        go.Bar(
            name="Current %",
            x=bud["Channel_Used"],
            y=bud["current_pct"] * 100,
            marker_color=PALETTE[2],
        )
    )
    bud_plot.add_trace(
        go.Bar(
            name="Recommended %",
            x=bud["Channel_Used"],
            y=bud["recommended_pct"] * 100,
            marker_color=PALETTE[3],
        )
    )
    bud_plot.update_layout(
        barmode="group",
        title="Budget mix: current vs efficiency-weighted recommendation",
        yaxis_title="Share of spend (%)",
        xaxis_title="Channel",
        height=420,
        legend=dict(orientation="h", y=1.05),
    )

    top_camps = (
        filt.groupby(["Campaign_ID", "Campaign_Type", "Channel_Used"], as_index=False)
        .agg(Revenue=("Revenue", "sum"), Spend=("Spend", "sum"), ROI=("ROI", "mean"))
        .sort_values("Revenue", ascending=False)
        .head(15)
    )

    c41, c42 = st.columns(2)
    with c41:
        st.plotly_chart(bud_plot, use_container_width=True)
        st.caption(f"Projected revenue under reallocation (same total spend): **${projected:,.0f}** (~**{lift:+.1f}%** vs filtered actual).")
    with c42:
        st.subheader("Top campaigns by revenue")
        st.dataframe(top_camps, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
