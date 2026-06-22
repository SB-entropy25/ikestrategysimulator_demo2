import streamlit as st
import os
import random
import plotly.graph_objects as go
from src.simulation_engine import SimulationEngine
from src.storage import StorageHandler

# --- Setup ---
st.set_page_config(page_title="F1 WAR ROOM", layout="wide", initial_sidebar_state="collapsed")

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
engine = SimulationEngine(DATA_DIR)
storage = StorageHandler(DATA_DIR)

# Load CSS
css_path = os.path.join(os.path.dirname(__file__), 'assets', 'style.css')
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- Session State Initialization ---
if 'phase' not in st.session_state:
    st.session_state.phase = 1

if 'team_info' not in st.session_state:
    st.session_state.team_info = {}

if 'driver_profile' not in st.session_state:
    st.session_state.driver_profile = {}

if 'upgrades' not in st.session_state:
    st.session_state.upgrades = []

if 'credits' not in st.session_state:
    st.session_state.credits = 100

if 'race_state' not in st.session_state:
    st.session_state.race_state = {
        "lap": 1,
        "position": random.randint(5, 15),
        "tire_health": 100,
        "tire_compound": "Medium",
        "tire_age": 0,
        "track_dampness": 0,
        "fuel_load": 110.0,
        "ers_percent": 100,
        "gap_ahead": random.uniform(1.0, 5.0),
        "gap_behind": random.uniform(1.0, 5.0),
        "reliability": 100,
        "driver_confidence": 100,
        "pit_stops": 0,
        "risk_efficiency": 50,
        "resource_management": 50,
        "prediction_accuracy": 50,
        "strategy_bonus": 0
    }

if 'decision_history' not in st.session_state:
    st.session_state.decision_history = []

if 'current_event' not in st.session_state:
    st.session_state.current_event = None

def create_gauge(value, title, max_val=100, color="green"):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title, 'font': {'size': 24, 'color': 'white', 'family': 'Teko'}},
        gauge = {
            'axis': {'range': [None, max_val], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_val*0.3], 'color': 'rgba(255,0,0,0.3)'},
                {'range': [max_val*0.3, max_val*0.7], 'color': 'rgba(255,255,0,0.3)'},
                {'range': [max_val*0.7, max_val], 'color': 'rgba(0,255,0,0.3)'}],
        }
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white", 'family': "Share Tech Mono"}, height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# --- Phase 1: Registration ---
def phase_1_registration():
    st.title("F1 WAR ROOM")
    st.subheader("The Strategist's Challenge")
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        with st.container(border=True):
            st.markdown("### 🖥️ Launch Control")
            st.markdown("Authenticate your telemetry connection to initialize operations.")
            principal_name = st.text_input("Team Principal Name:", placeholder="e.g., Christian Horner")
            team_name = st.text_input("Team Name:", placeholder="e.g., Red Bull Racing")
            
            if st.button("Initialize Operations", use_container_width=True):
                if principal_name and team_name:
                    st.session_state.team_info = {
                        "team_id": f"TID-{random.randint(1000,9999)}",
                        "principal_name": principal_name,
                        "team_name": team_name
                    }
                    st.session_state.phase = 2
                    st.rerun()
                else:
                    st.error("Authentication failed. Provide valid credentials.")
                    
            st.markdown("---")
            if storage.gsheets_enabled:
                st.success(f"🟢 **Database:** {storage.status_message}")
            else:
                st.warning(f"⚠️ **Database:** {storage.status_message}")
                with st.expander("Show Connection Diagnostics"):
                    st.write("**Error Details:**")
                    st.code(storage.error_details)
                    
    with col2:
        with st.container(border=True):
            st.markdown("### 📋 Operations Briefing & Rules")
            
            tabs = st.tabs(["🎮 Objective & Flow", "🏁 Key Rules & Strategy", "📊 Scoring & Telemetry"])
            
            with tabs[0]:
                st.markdown("""
                **Welcome to the Pit Wall.** You are the Team Principal and Chief Strategist. 
                Your mission is to guide your driver through a dynamic **60-lap Grand Prix** under shifting weather and track conditions.
                
                **Simulation Flow:**
                1. **Onboarding**: Set up your team credentials.
                2. **Driver Assessment**: Profiles your driver's traits (Aggression, Tyre Management, Adaptability).
                3. **R&D Upgrades**: Invest your 100 Credits budget in performance enhancements.
                4. **Live Race Operations**: Make critical decisions every few laps (Push, Defend, Save, Pit).
                5. **Debrief**: Analyze your timeline, strategy, and leaderboard ranking.
                """)
                
            with tabs[1]:
                st.markdown("""
                **Race Regulations & Strategy:**
                
                * **The Tire Cliff**: Below **30% Tire Health**, tires hit the cliff. Lap times drop off exponentially and puncture risks increase drastically.
                * **Track Dampness**: 
                  * Slicks (Soft/Medium/Hard) lose all grip above **30% dampness** (massive time loss & spin risks).
                  * Wets/Intermediates degrade **3x faster** on a dry track (below 20% dampness).
                * **R&D Upgrades**:
                  * *Elite Pit Crew (30 cr)*: Cuts pit time loss from 23s to 18.5s.
                  * *Weather Center (40 cr)*: Unlocks advanced precision weather forecasts.
                  * *AI Strategy Assistant (50 cr)*: Displays real-time pit wall recommendations.
                  * *Reliability Package (35 cr)*: Halves subsystem wear/degradation.
                  * *Tire Engineers (45 cr)*: Reduces tire wear rate by 20%.
                """)
                
            with tabs[2]:
                st.markdown("""
                **Pit Wall Telemetry & Scoring:**
                
                * **Dashboard**: Monitor live gauges for Tyre Health, ERS deployment, Fuel reserves, and Car Reliability.
                * **Scoring Breakdown (Max 1000 pts):**
                  * **Race Result (300 pts)**: Higher finishes yield more points (P1 = 300 pts).
                  * **Strategy Accuracy (250 pts)**: Evaluates decision optimization.
                  * **Risk & Resource (250 pts)**: Rewards efficient fuel, ERS, and safety margin management.
                  * **Driver & Innovation (200 pts)**: Scoring based on driver confidence and smart tactical plays.
                """)

# --- Phase 2: Driver Quiz ---
def phase_2_quiz():
    st.title("Driver Profiling")
    st.markdown("Assess your newly signed driver's mentality.")
    
    with st.container(border=True):
        st.markdown("### 🧠 Psychological & Decision-Making Assessment")
        q1 = st.radio("1. When trailing by 0.5s entering a high-speed corner, your driver should:", 
                      ("Lift and preserve tires", "Wait for DRS zone", "Attempt an aggressive late-brake dive", "Follow telemetry strictly"), index=None)
        q2 = st.radio("2. Weather radar shows 40% chance of rain in 5 laps. Your driver:",
                      ("Pits immediately for Inters", "Waits for engineer instruction", "Complains about grip but stays out", "Pushes hard to build a gap before rain"), index=None)
        q3 = st.radio("3. Engineer reports engine temps are critical. Your driver:",
                      ("Ignores and keeps pushing", "Lifts and coasts slightly", "Demands a new engine map", "Pits to clear sidepods"), index=None)
        q4 = st.radio("4. How does your driver treat the Pirelli tires?",
                      ("Burns them up in 10 laps", "Uses them exactly as simulated", "Can miraculously extend a stint by 15 laps", "Complains they are dead after lap 1"), index=None)
        q5 = st.radio("5. A Safety Car is deployed. Your driver is:",
                      ("Furious because he lost his 10s lead", "Relieved because he can save fuel", "Already analyzing the restart strategy", "Asking about other drivers' pit stops"), index=None)
                      
        if st.button("Generate Driver Profile", use_container_width=True):
            if all([q1, q2, q3, q4, q5]):
                answers = [
                    ["Lift and preserve tires", "Wait for DRS zone", "Follow telemetry strictly", "Attempt an aggressive late-brake dive"].index(q1) + 1,
                    ["Waits for engineer instruction", "Complains about grip but stays out", "Pushes hard to build a gap before rain", "Pits immediately for Inters"].index(q2) + 1,
                    ["Pits to clear sidepods", "Lifts and coasts slightly", "Demands a new engine map", "Ignores and keeps pushing"].index(q3) + 1,
                    ["Can miraculously extend a stint by 15 laps", "Uses them exactly as simulated", "Complains they are dead after lap 1", "Burns them up in 10 laps"].index(q4) + 1,
                    ["Relieved because he can save fuel", "Asking about other drivers' pit stops", "Already analyzing the restart strategy", "Furious because he lost his 10s lead"].index(q5) + 1
                ]
                st.session_state.driver_profile = engine.evaluate_quiz(answers)
                st.toast("Driver profile generated successfully!", icon="✅")
                st.session_state.phase = 3
                st.rerun()
            else:
                st.error("All assessments must be completed.")

# --- Phase 3: Upgrades ---
def phase_3_upgrades():
    st.title("Team Development")
    st.subheader(f"Credits Available: {st.session_state.credits} cr")
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### 📊 Driver Profile Generated")
            st.markdown(f"**Driver Archetype ID:** `{st.session_state.driver_profile['driver_id']}`")
            for stat, val in st.session_state.driver_profile.items():
                if stat != "driver_id":
                    st.progress(val/100.0, text=f"{stat.replace('_', ' ').title()}: {val}%")
        
    with col2:
        with st.container(border=True):
            st.markdown("### 🛠️ Select Upgrades")
            upgrades = {
                "Elite Pit Crew (30 cr)": 30,
                "Weather Center (40 cr)": 40,
                "AI Strategy Assistant (50 cr)": 50,
                "Reliability Package (35 cr)": 35,
                "Tire Engineers (45 cr)": 45
            }
            
            selected = []
            for upg, cost in upgrades.items():
                if st.checkbox(upg):
                    selected.append((upg, cost))
                    
            total_cost = sum([c for _, c in selected])
            st.metric("Total Cost", f"{total_cost} cr")
    
    st.divider()
    if st.button("Confirm Development & Head to Grid", use_container_width=True):
        if total_cost <= 100:
            st.session_state.upgrades = [u for u, _ in selected]
            st.session_state.credits -= total_cost
            st.toast("Upgrades applied. Heading to grid...", icon="🏎️")
            st.session_state.phase = 4
            st.rerun()
        else:
            st.error("Insufficient credits for selected upgrades.")

# --- Phase 4: Race Loop ---
def phase_4_race():
    st.title("LIVE: GRAND PRIX")
    rs = st.session_state.race_state
    
    # Dynamic styling class (applied to container)
    alert_class = ""
    if rs['tire_health'] < 30 or rs['reliability'] < 40:
        alert_class = "pulse-alert"
    
    # Header telemetry
    with st.container(border=True):
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("LAP", f"{rs['lap']} / 60")
        c2.metric("POSITION", f"P{rs['position']}")
        c3.metric("GAP AHEAD", f"+{rs['gap_ahead']:.1f}s")
        c4.metric("GAP BEHIND", f"-{rs['gap_behind']:.1f}s")
        c5.metric("COMPOUND", f"{rs['tire_compound']}")
        c6.metric("DAMPNESS", f"{rs['track_dampness']}%")
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        with st.container(border=True):
            # Generate random event if none
            if st.session_state.current_event is None:
                st.session_state.current_event = engine.events.sample(1).iloc[0]
                st.session_state.radio_msg = engine.generate_radio_message(rs)
            
            evt = st.session_state.current_event
            
            st.markdown(f"### Current Situation: {evt['event_type']}")
            
            # Apply alert logic using custom warning block
            if alert_class:
                st.markdown(f'<div class="pulse-alert" style="padding: 10px; margin-bottom: 15px; border-radius: 4px; background-color: rgba(255,0,0,0.15); border-left: 5px solid red; font-weight: bold; color: #ff3333;">🚨 SYSTEM ALERT: Subsystems or Tires at Critical Threshold!</div>', unsafe_allow_html=True)
                
            st.warning(f"Severity: {evt['severity']}")
            st.markdown(f"<div class='radio-box'><span class='radio-driver'>DRIVER RADIO:</span> {st.session_state.radio_msg}</div>", unsafe_allow_html=True)
            
            # Actions
            actions = evt['possible_actions'].split('|')
            for a in ["Push", "Save Tires", "Pit", "Defend"]:
                if a not in actions:
                    actions.append(a)
                    
            decision = st.radio("STRATEGY DECISION:", actions, key=f"decision_{rs['lap']}", horizontal=True)
            
            # Pit stop compound selection
            pit_compound = rs['tire_compound']
            if decision == "Pit":
                pit_compound = st.selectbox("Select New Tire Compound:", ["Soft", "Medium", "Hard", "Intermediate", "Wet"])
                
            # AI Strategy Assistant Upgrade
            if "AI Strategy Assistant" in str(st.session_state.upgrades):
                st.info("💡 **AI Strategy Recommendation:** " + 
                        ("Pit immediately for new tires! Your current set is critical." if rs['tire_health'] < 40 else
                         "Pit for Intermediates/Wets to match the incoming rain." if rs['track_dampness'] > 30 and rs['tire_compound'] in ["Soft", "Medium", "Hard"] else
                         "Maintain current strategy. Push if gap ahead is small, save tires to extend stint."))

            if st.button("Execute Decision", use_container_width=True):
                if decision == "Pit":
                    rs['tire_compound'] = pit_compound
                    st.toast(f"Pitting for {pit_compound}s...", icon="🔧")
                else:
                    st.toast(f"Executing: {decision}", icon="⚡")
                    
                new_state = engine.process_decision(
                    rs, decision, st.session_state.driver_profile, st.session_state.upgrades
                )
                st.session_state.race_state = new_state
                st.session_state.decision_history.append({"lap": rs['lap'], "event": evt['event_type'], "decision": decision})
                st.session_state.current_event = None
                
                # End race if lap count is reached or the car has DNF'd/DSQ'd (reliability reaches 0)
                if new_state['lap'] >= 60 or new_state['reliability'] <= 0:
                    st.session_state.phase = 5
                
                st.rerun()

    with col2:
        with st.container(border=True):
            tab1, tab2, tab3 = st.tabs(["Dashboard", "Weather & Comms", "Car Health"])
            
            with tab1:
                # Plotly Gauges
                fig_tire = create_gauge(rs['tire_health'], "TIRE HEALTH %", color="#ff1801" if rs['tire_health']<30 else "#00ff00")
                st.plotly_chart(fig_tire, use_container_width=True, config={'displayModeBar': False})
                
                st.progress(rs['fuel_load']/110.0, text=f"Fuel Load: {rs['fuel_load']:.1f}kg")
                
            with tab2:
                st.markdown("### Weather Radar")
                weather = engine.weather.sample(1).iloc[0]
                st.info(f"Condition: {weather['condition']}")
                if "Weather Center" in str(st.session_state.upgrades):
                    st.success("🌦️ **Advanced Radar:** Highly accurate precipitation tracking active.")
                    
                if st.session_state.decision_history:
                    last_dec = st.session_state.decision_history[-1]
                    st.markdown("### Pit Wall Comms")
                    st.markdown(f"***Engineer:** {engine.generate_commentary(rs, last_dec['decision'])}*")
                    
            with tab3:
                st.markdown("### Subsystems")
                st.progress(rs['reliability']/100.0, text=f"Car Reliability: {rs['reliability']}%")
                st.progress(rs['driver_confidence']/100.0, text=f"Driver Confidence: {rs['driver_confidence']}%")
                st.progress(rs['ers_percent']/100.0, text=f"ERS Deployment: {rs['ers_percent']}%")

# --- Phase 5: End Race Report ---
def phase_5_report():
    st.title("RACE DEBRIEF")
    
    score_breakdown = engine.calculate_final_score(st.session_state.race_state)
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            rs = st.session_state.race_state
            if rs.get("reliability", 100) <= 0:
                if rs.get("fuel_load", 10.0) <= 0.0:
                    st.markdown("## Final Status: DSQ (Disqualified - Out of Fuel)")
                elif rs.get("tire_health", 100) < 10:
                    st.markdown("## Final Status: DNF (Retired - Tire Blowout)")
                elif rs.get("track_dampness", 0) > 35 and rs.get("tire_compound") in ["Soft", "Medium", "Hard"]:
                    st.markdown("## Final Status: DNF (Retired - Crash in Wet)")
                else:
                    st.markdown("## Final Status: DNF (Retired - Engine Failure)")
            else:
                st.markdown(f"## Final Position: P{rs.get('position', 10)}")
                
            st.markdown(f"### Total Score: {score_breakdown['total_score']} / 1000")
            
            # Display score dynamically
            for key, val in score_breakdown.items():
                if key != "total_score":
                    st.metric(key.replace('_', ' ').title(), val)
        
    with col2:
        with st.container(border=True):
            st.markdown("### Strategy Timeline")
            with st.expander("View Full Race Timeline", expanded=True):
                for d in st.session_state.decision_history:
                    st.markdown(f"**Lap {d['lap']}:** {d['event']} ➔ `{d['decision']}`")
            
    if st.button("Save & View Leaderboard", use_container_width=True):
        p_data = {
            "team_id": st.session_state.team_info["team_id"],
            "principal_name": st.session_state.team_info["principal_name"],
            "team_name": st.session_state.team_info["team_name"],
            "driver_profile": str(st.session_state.driver_profile),
            "upgrades": str(st.session_state.upgrades),
            "race_position": st.session_state.race_state.get('position', 20),
            "strategy_score": score_breakdown['strategy_accuracy'],
            "total_score": score_breakdown['total_score']
        }
        storage.save_participant(p_data)
        st.balloons()
        st.success("Results saved and exported to Excel.")
        
        st.markdown("### Leaderboard")
        st.dataframe(storage.get_leaderboard())
        
        if storage.gsheets_enabled:
            st.success(f"🟢 **Data Synchronized:** {storage.status_message}")
        else:
            st.warning(f"⚠️ **Offline Mode:** {storage.status_message}")

# --- Router ---
if st.session_state.phase == 1:
    phase_1_registration()
elif st.session_state.phase == 2:
    phase_2_quiz()
elif st.session_state.phase == 3:
    phase_3_upgrades()
elif st.session_state.phase == 4:
    phase_4_race()
elif st.session_state.phase == 5:
    phase_5_report()
