
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="WattWise AI",
    page_icon="⚡",
    layout="wide"
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background: #0b1120;
    color: #f8fafc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    padding: 35px;
    border-radius: 20px;
    background: linear-gradient(135deg, #111827, #172554);
    border: 1px solid #334155;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 48px;
    margin-bottom: 5px;
}

.hero p {
    font-size: 18px;
    color: #cbd5e1;
}

.section-title {
    font-size: 25px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 15px;
}

.kpi {
    background: #111827;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 22px;
    min-height: 145px;
}

.kpi-title {
    color: #94a3b8;
    font-size: 14px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 700;
    margin-top: 10px;
}

.kpi-desc {
    color: #64748b;
    font-size: 12px;
    margin-top: 5px;
}

.info-box {
    background: #111827;
    border-left: 4px solid #38bdf8;
    padding: 18px;
    border-radius: 10px;
    margin: 15px 0;
}

.warning-box {
    background: #271b08;
    border-left: 4px solid #f59e0b;
    padding: 18px;
    border-radius: 10px;
    margin: 15px 0;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv("wattwise_hostel_energy_data.csv")

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


df = load_data()


# ============================================================
# ML ANOMALY DETECTION
# ============================================================

features = [
    "temperature_c",
    "occupancy",
    "ac_status",
    "light_status",
    "scheduled",
    "power_kw"
]

model = IsolationForest(
    n_estimators=200,
    contamination=0.02,
    random_state=42
)

model.fit(df[features])

df["ml_anomaly"] = model.predict(df[features])

df["ml_anomaly_label"] = df["ml_anomaly"].map({
    1: "NORMAL",
    -1: "ANOMALY"
})


# ============================================================
# WATTWISE CONTEXT ENGINE
# ============================================================

def wattwise_context_detector(row):

    if row["ac_status"] == 1 and row["occupancy"] == 0:
        return "AC_WASTE"

    if row["occupancy"] == 0 and row["power_kw"] > 0.5:
        return "STANDBY_WASTE"

    if row["ml_anomaly"] == -1:
        return "ANOMALY_REQUIRES_REVIEW"

    return "NORMAL"


df["wattwise_status"] = df.apply(
    wattwise_context_detector,
    axis=1
)


# ============================================================
# EXPLANATION ENGINE
# ============================================================

def wattwise_explanation(row):

    status = row["wattwise_status"]

    if status == "AC_WASTE":

        return (
            f"AC is running in {row['room_id']} while the room "
            f"has no occupants. Power consumption is "
            f"{row['power_kw']:.3f} kW."
        )

    elif status == "STANDBY_WASTE":

        return (
            f"{row['room_id']} has no occupants but is consuming "
            f"{row['power_kw']:.3f} kW. This may indicate "
            f"unnecessary standby consumption."
        )

    elif status == "ANOMALY_REQUIRES_REVIEW":

        return (
            f"Energy consumption of {row['power_kw']:.3f} kW "
            f"is unusual compared with learned patterns. "
            f"Further contextual review is recommended."
        )

    return "Energy usage appears normal."


df["wattwise_explanation"] = df.apply(
    wattwise_explanation,
    axis=1
)


# ============================================================
# RECOMMENDATION ENGINE
# ============================================================

def generate_recommendation(row):

    status = row["wattwise_status"]

    if status == "AC_WASTE":

        return (
            "Check whether the AC can be switched off when the "
            "room is unoccupied. Consider occupancy-based or "
            "scheduled AC control."
        )

    elif status == "STANDBY_WASTE":

        return (
            "Check connected devices and standby loads. Switch "
            "off unnecessary equipment when the room is unused."
        )

    elif status == "ANOMALY_REQUIRES_REVIEW":

        return (
            "Review this reading against room activity, device "
            "status and operating schedule before taking action."
        )

    return "No immediate action required."


df["recommendation"] = df.apply(
    generate_recommendation,
    axis=1
)


# ============================================================
# ENERGY AND COST CALCULATIONS
# ============================================================

tariff_per_kwh = 8.0

df["estimated_cost"] = (
    df["energy_kwh"] * tariff_per_kwh
)

df["avoidable_energy_kwh"] = np.where(
    df["wattwise_status"].isin(
        ["AC_WASTE", "STANDBY_WASTE"]
    ),
    df["energy_kwh"],
    0
)

df["avoidable_cost"] = (
    df["avoidable_energy_kwh"] * tariff_per_kwh
)


total_energy = df["energy_kwh"].sum()

avoidable_energy = df["avoidable_energy_kwh"].sum()

avoidable_cost = df["avoidable_cost"].sum()

avoidable_percentage = (
    avoidable_energy / total_energy
) * 100


# ============================================================
# WATTWISE SCORE
# ============================================================

wattwise_score = 100 - (
    avoidable_percentage * 5
)

wattwise_score = max(
    0,
    min(100, wattwise_score)
)


# ============================================================
# WHAT-IF SIMULATION
# ============================================================

prevention_rate = 0.80

simulated_saving_energy = (
    avoidable_energy * prevention_rate
)

simulated_saving_cost = (
    simulated_saving_energy * tariff_per_kwh
)

simulated_new_energy = (
    total_energy - simulated_saving_energy
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚡ WattWise AI")

st.sidebar.caption(
    "Explainable Energy Waste Copilot"
)

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Dashboard",
        "🚨 Energy Events",
        "🔮 What-If Simulator",
        "🏢 Room Analysis"
    ]
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Prototype uses simulated smart-meter data. "
    "It does not represent real measured hostel electricity data."
)


# ============================================================
# HERO
# ============================================================

st.markdown("""
<div class="hero">

<h1>⚡ WattWise AI</h1>

<p>
An Explainable Energy Waste Copilot for Hostels & Small Offices
</p>

<p>
Detect waste • Explain why • Simulate fixes • Verify savings
</p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="section-title">🧠 WattWise AI Summary</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-box">
    <b>What makes WattWise AI different?</b><br>
    Instead of only showing electricity consumption,
    WattWise combines energy, occupancy, device status
    and learned patterns to identify potentially wasteful
    behaviour and explain the reason behind it.
    </div>
    """, unsafe_allow_html=True)

    # KPI ROW

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.markdown(f"""
        <div class="kpi">

        <div class="kpi-title">
        TOTAL ENERGY
        </div>

        <div class="kpi-value">
        {total_energy:,.2f} kWh
        </div>

        <div class="kpi-desc">
        Simulated 30-day dataset
        </div>

        </div>
        """, unsafe_allow_html=True)

    with c2:

        st.markdown(f"""
        <div class="kpi">

        <div class="kpi-title">
        Potentially Avoidable Cost
        </div>

        <div class="kpi-value">
        ₹{avoidable_cost:,.2f}
        </div>

        <div class="kpi-desc">
        Potentially avoidable usage
        </div>

        </div>
        """, unsafe_allow_html=True)

    with c3:

        st.markdown(f"""
        <div class="kpi">

        <div class="kpi-title">
        AVOIDABLE ENERGY
        </div>

        <div class="kpi-value">
        {avoidable_energy:,.2f} kWh
        </div>

        <div class="kpi-desc">
        {avoidable_percentage:.2f}% of total usage
        </div>

        </div>
        """, unsafe_allow_html=True)

    with c4:

        st.markdown(f"""
        <div class="kpi">

        <div class="kpi-title">
        WATTWISE SCORE
        </div>

        <div class="kpi-value">
        {wattwise_score:.1f}/100
        </div>

        <div class="kpi-desc">
        Prototype efficiency score
        </div>

        </div>
        """, unsafe_allow_html=True)


    # --------------------------------------------------------
    # ENERGY TREND
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">📈 Energy Consumption Trend</div>',
        unsafe_allow_html=True
    )

    daily_energy = (
        df.groupby(
            df["timestamp"].dt.date
        )["energy_kwh"]
        .sum()
        .reset_index()
    )

    daily_energy.columns = [
        "date",
        "energy_kwh"
    ]

    fig = px.line(
        daily_energy,
        x="date",
        y="energy_kwh",
        markers=True,
        title="Daily Energy Consumption"
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Energy (kWh)"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


    # --------------------------------------------------------
    # WASTE BREAKDOWN
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            '<div class="section-title">🚨 Energy Events</div>',
            unsafe_allow_html=True
        )

        waste_counts = df[
            df["wattwise_status"] != "NORMAL"
        ]["wattwise_status"].value_counts()

        if len(waste_counts) > 0:

            fig_waste = px.bar(
                x=waste_counts.index,
                y=waste_counts.values,
                labels={
                    "x": "Detection Type",
                    "y": "Events"
                },
                title="Detected Events"
            )

            fig_waste.update_layout(
                template="plotly_dark"
            )

            st.plotly_chart(
                fig_waste,
                width="stretch"
            )

        else:

            st.success(
                "No waste events detected."
            )


    # --------------------------------------------------------
    # SCORE GAUGE
    # --------------------------------------------------------

    with col2:

        st.markdown(
            '<div class="section-title">🎯 WattWise Score</div>',
            unsafe_allow_html=True
        )

        gauge = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=wattwise_score,
                title={
                    "text": "Energy Efficiency Score"
                },
                gauge={
                    "axis": {
                        "range": [0, 100]
                    }
                }
            )
        )

        gauge.update_layout(
            template="plotly_dark"
        )

        st.plotly_chart(
            gauge,
            width="stretch"
        )


    # --------------------------------------------------------
    # PROTOTYPE NOTE
    # --------------------------------------------------------

    st.markdown("""
    <div class="warning-box">

    ⚠️ <b>Prototype Data Notice</b><br>

    The current dataset is simulated for demonstration.
    The savings estimate and WattWise Score are prototype
    calculations, not verified real-world savings.

    </div>
    """, unsafe_allow_html=True)


# ============================================================
# Energy Events PAGE
# ============================================================

elif page == "🚨 Energy Events":

    st.markdown(
        '<div class="section-title">🚨 Explainable Energy Events</div>',
        unsafe_allow_html=True
    )

    st.write(
        "WattWise combines contextual rules with machine-learning "
        "anomaly detection."
    )

    detection_filter = st.selectbox(
        "Select detection type",
        [
            "All",
            "AC_WASTE",
            "STANDBY_WASTE",
            "ANOMALY_REQUIRES_REVIEW"
        ]
    )

    if detection_filter == "All":

        display_df = df[
            df["wattwise_status"] != "NORMAL"
        ]

    else:

        display_df = df[
            df["wattwise_status"] == detection_filter
        ]

    st.write(
        f"Detected events: **{len(display_df)}**"
    )

    display_columns = [
        "timestamp",
        "room_id",
        "temperature_c",
        "occupancy",
        "power_kw",
        "wattwise_status",
        "wattwise_explanation",
        "recommendation"
    ]

    st.dataframe(
        display_df[display_columns].head(100),
        width="stretch",
        hide_index=True
    )


# ============================================================
# WHAT-IF SIMULATOR
# ============================================================

elif page == "🔮 What-If Simulator":

    st.markdown(
        '<div class="section-title">🔮 What-If Energy Simulator</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-box">

    Change the prevention rate to simulate how much energy
    and money could potentially be saved if detected waste
    were reduced.

    </div>
    """, unsafe_allow_html=True)

    prevention_rate = st.slider(
        "Waste prevention rate",
        min_value=0,
        max_value=100,
        value=80,
        step=5
    )

    rate = prevention_rate / 100

    saving_energy = (
        avoidable_energy * rate
    )

    saving_cost = (
        saving_energy * tariff_per_kwh
    )

    new_energy = (
        total_energy - saving_energy
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Current Energy",
            f"{total_energy:,.2f} kWh"
        )

    with c2:

        st.metric(
            "Potential Energy Saved",
            f"{saving_energy:,.2f} kWh"
        )

    with c3:

        st.metric(
            "Potential Cost Saved",
            f"₹{saving_cost:,.2f}"
        )

    st.markdown(
        '<div class="section-title">📊 Simulation Result</div>',
        unsafe_allow_html=True
    )

    comparison = pd.DataFrame({
        "Scenario": [
            "Current",
            "After simulated prevention"
        ],
        "Energy (kWh)": [
            total_energy,
            new_energy
        ]
    })

    fig = px.bar(
        comparison,
        x="Scenario",
        y="Energy (kWh)",
        title="Current vs Simulated Energy Consumption"
    )

    fig.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.warning(
        "The prevention rate is a prototype assumption. "
        "It is not a guaranteed real-world saving."
    )


# ============================================================
# ROOM ANALYSIS
# ============================================================

elif page == "🏢 Room Analysis":

    st.markdown(
        '<div class="section-title">🏢 Room-Level Energy Analysis</div>',
        unsafe_allow_html=True
    )

    selected_room = st.selectbox(
        "Select Room",
        sorted(df["room_id"].unique())
    )

    room_df = df[
        df["room_id"] == selected_room
    ]

    room_energy = room_df["energy_kwh"].sum()

    room_avoidable = (
        room_df["avoidable_energy_kwh"].sum()
    )

    room_cost = (
        room_avoidable * tariff_per_kwh
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Room Energy",
            f"{room_energy:,.2f} kWh"
        )

    with c2:

        st.metric(
            "Potentially Avoidable",
            f"{room_avoidable:,.2f} kWh"
        )

    with c3:

        st.metric(
            "Potential Cost",
            f"₹{room_cost:,.2f}"
        )


    st.markdown(
        '<div class="section-title">📈 Room Energy Trend</div>',
        unsafe_allow_html=True
    )

    fig_room = px.line(
        room_df,
        x="timestamp",
        y="power_kw",
        title=f"Power Consumption — {selected_room}"
    )

    fig_room.update_layout(
        template="plotly_dark",
        xaxis_title="Time",
        yaxis_title="Power (kW)"
    )

    st.plotly_chart(
        fig_room,
        width="stretch"
    )


    st.markdown(
        '<div class="section-title">🚨 Room Events</div>',
        unsafe_allow_html=True
    )

    room_events = room_df[
        room_df["wattwise_status"] != "NORMAL"
    ]

    if len(room_events) > 0:

        st.dataframe(
            room_events[
                [
                    "timestamp",
                    "power_kw",
                    "wattwise_status",
                    "wattwise_explanation",
                    "recommendation"
                ]
            ],
            width="stretch",
            hide_index=True
        )

    else:

        st.success(
            "No waste or anomaly events detected for this room."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "⚡ WattWise AI | HackNowa Global Hackathon 2026 | "
    "Smart & Sustainable Future"
)

st.caption(
    "Prototype demonstration using simulated energy data."
)