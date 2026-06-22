import pandas as pd
import numpy as np
import random
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def generate_drivers(num_drivers=20):
    drivers = []
    for i in range(1, num_drivers + 1):
        driver_id = f"DRV-{i:02d}"
        drivers.append({
            "driver_id": driver_id,
            "aggression": random.randint(50, 99),
            "race_pace": random.randint(70, 99),
            "wet_pace": random.randint(60, 99),
            "overtaking": random.randint(50, 99),
            "tire_management": random.randint(50, 99),
            "consistency": random.randint(60, 99),
            "reliability": random.randint(70, 99)
        })
    df = pd.DataFrame(drivers)
    df.to_csv(os.path.join(DATA_DIR, 'drivers.csv'), index=False)
    print(f"Generated {len(drivers)} drivers.")

def generate_teams(num_teams=10):
    teams = []
    for i in range(1, num_teams + 1):
        team_id = f"TEAM-{i:02d}"
        teams.append({
            "team_id": team_id,
            "pitstop_speed": round(random.uniform(2.0, 3.5), 2),
            "base_pace": random.randint(75, 99),
            "reliability": random.randint(70, 99),
            "strategy_rating": random.randint(60, 99),
            "upgrade_slots": 5
        })
    df = pd.DataFrame(teams)
    df.to_csv(os.path.join(DATA_DIR, 'teams.csv'), index=False)
    print(f"Generated {len(teams)} teams.")

def generate_events(num_events=250):
    event_templates = {
        "Safety Car": {
            "Low": "Debris reported at Turn 4 from a minor lockup. Marshall flags are yellow, Safety Car standing by.",
            "Medium": "Minor collision between Haas and Williams at the hairpin. Recovery vehicle on track, Safety Car preparing to deploy.",
            "High": "Safety Car deployed! Esteban Ocon has spun off into the gravel barrier at Turn 7, leaving heavy carbon fiber debris on the racing line.",
            "Critical": "Safety Car deployed! Multi-car incident at the start/finish straight. Heavy barrier damage. Strategic window is wide open!"
        },
        "Virtual Safety Car": {
            "Low": "Minor telemetry anomaly. Virtual Safety Car monitoring delta times.",
            "Medium": "Stalled car in Sector 3 run-off area. VSC deployed to safely retrieve the vehicle.",
            "High": "VSC deployed! Magnussen stopped at Turn 10 with engine issues. Keep the target delta positive.",
            "Critical": "VSC deployed! Sudden debris on track in Sector 1. Great opportunity to save fuel or execute a cheap pitstop!"
        },
        "Red Flag": {
            "Low": "Track warning: High winds. Red flag standby.",
            "Medium": "Heavy rain forecast. Race director warning of a potential Red Flag if conditions worsen.",
            "High": "Red Flag! Barrier damage at Turn 3 requires immediate repairs. All cars returning to the pit lane.",
            "Critical": "Red Flag deployed! Massive incident at the main straight has halted the session. Complete race restart protocols active!"
        },
        "Rain Starts": {
            "Low": "Light spots of rain reported in Sector 2. Slicks still holding up, but grip is dropping.",
            "Medium": "Rain intensity increasing. Track dampness rising towards 20%. Strategic crossover point approaching.",
            "High": "Rain is coming down hard now. Track dampness is at 45% and climbing. Intermediate tires required!",
            "Critical": "Torrential downpour! Heavy standing water on the straight. Track dampness exceeded 70%. Wet tires mandatory!"
        },
        "Rain Stops": {
            "Low": "Rain has stopped, but the track remains wet. Watch for dry line evolution.",
            "Medium": "Track is drying out quickly. Dampness dropping below 30%. Slicks might be faster soon.",
            "High": "Dry line visible on track. Dampness is under 15%. Intermediate tires are starting to overheat.",
            "Critical": "Track is completely dry! The dampness is 0%. Wet/Intermediate tires will disintegrate within a few laps!"
        },
        "Brake Failure Warning": {
            "Low": "Brake temps climbing slightly. Watch your brake wear telemetry.",
            "Medium": "Brake duct temperatures are critical. Driver complaining of spongy brake pedal feel.",
            "High": "Brake fluid pressure dropping! Reliability impacted. Lift and coast required to cool the system.",
            "Critical": "Major Brake Wear Warning! High risk of failure. Driver must manage temperature immediately or retire!"
        },
        "Hydraulic Warning": {
            "Low": "Hydraulic pressure sensor fluctuation detected. Status monitored.",
            "Medium": "Hydraulic warning on the dashboard. Gear changes starting to feel sluggish.",
            "High": "Pressure drop in the hydraulic loop! Steering weight has increased. Reliability is critical.",
            "Critical": "Critical hydraulic leak! Gearbox shifts failing. Shift to safe mode immediately!"
        },
        "Driver Complaint": {
            "Low": "Driver: 'Seat feels a bit loose, but I can manage.'",
            "Medium": "Driver: 'These tires are vibrating like crazy, check the balance!'",
            "High": "Driver: 'The wind is pushing me all over the track, I have no rear stability!'",
            "Critical": "Driver: 'No grip! The rear is sliding everywhere, I'm skating on ice here!'"
        },
        "Pit Lane Congestion": {
            "Low": "Heavy traffic reported in the pit lane. Pit window tight.",
            "Medium": "Double-stack risk: Sister car approaching the pit box. Strategic spacing needed.",
            "High": "Pit lane bottleneck! Stalled car at the entry. Expect significant pit stop delays.",
            "Critical": "Pit entry blocked! Pitting now will result in massive stationary delays. Abort box call!"
        },
        "Undercut Threat": {
            "Low": "Rival car behind is close to pit window. Keep alert.",
            "Medium": "Car behind has pitted for fresh Softs. They will attempt the undercut. Push hard to defend!",
            "High": "Undercut threat active! Rival is putting green sectors on fresh rubber. You must react next lap!",
            "Critical": "Undercut successful! Rival has jumped us by pitting early. We must extend stint or change tactic."
        },
        "Overcut Opportunity": {
            "Low": "Car ahead is showing signs of tire degradation. Watch the gap.",
            "Medium": "Car ahead is pitting. We have clean air. Push now to execute the overcut!",
            "High": "Leader has pitted into traffic. You have 2 laps of maximum ERS push to leapfrog them!",
            "Critical": "Overcut opportunity! Rival's out-lap is slow on cold tires. Give it everything to stay ahead!"
        },
        "Tire Blistering": {
            "Low": "Minor blistering detected on the front-right tire. Temperature stable.",
            "Medium": "Tire blistering is worsening. Driver complains of understeer in fast corners.",
            "High": "Severe blistering on the rear tires. Thermal degradation is critical. Core grip has collapsed.",
            "Critical": "Tires are completely blistered and worn to the carcass! High risk of immediate puncture!"
        },
        "Track Evolution": {
            "Low": "Track rubbering in. Grip levels increasing slightly.",
            "Medium": "Clean racing line established. Corner speeds climbing. Lap times improving.",
            "High": "High track evolution! Rapid track drying and high rubber deposit. Grip levels are peak.",
            "Critical": "Grip levels are at their maximum. DRS zones are highly effective. Pace is flying!"
        },
        "Yellow Flag": {
            "Low": "Yellow flag in Sector 2. Driver went off track but rejoined.",
            "Medium": "Yellow flag in Sector 1. Spun car blocking the run-off. Watch the micro-sector deltas.",
            "High": "Yellow flag! Debris at the exit of Turn 4. No overtaking permitted in this zone.",
            "Critical": "Double wave yellow flags! Marshals on track recovering a car. Pushing now will incur penalties!"
        },
        "Front Wing Damage": {
            "Low": "Minor endplate damage from light curb contact. Telemetry shows 2% downforce loss.",
            "Medium": "Front wing damage! Collision debris has damaged the main plane. Understeer increasing.",
            "High": "Wing endplate has detached. Front grip is severely compromised. Pit stop box call needed for replacement.",
            "Critical": "Structural wing collapse! Debris under the floor. Driver has lost steering control. Box immediately!"
        },
        "Gearbox Alert": {
            "Low": "Gearbox temperature warning. Sensor anomaly suspected.",
            "Medium": "Sluggish shifts reported by driver. Gearbox oil temperature is high.",
            "High": "Gearbox wear active! Sluggish shifting and loss of 6th gear. Reliability dropping.",
            "Critical": "Gearbox failure warning! Driver must short-shift and avoid redline to finish the race!"
        },
        "DRS Train": {
            "Low": "DRS is enabled. Gap to car ahead is 0.9s.",
            "Medium": "Trapped in a DRS train! Overtaking is extremely difficult. We need to save fuel and manage tires.",
            "High": "DRS train bottleneck. Leader is holding up the field. Strategic pit stop is the only exit.",
            "Critical": "DRS train active! Pushing now will only burn fuel and cook tires in dirty air. Conserve and wait!"
        },
        "Fuel Concern": {
            "Low": "Fuel consumption is slightly above delta. Monitor usage.",
            "Medium": "Fuel flow warning. Current projection shows us finishing -0.5 laps under fuel margin. Save mode active.",
            "High": "Critical fuel delta! We are -1.5 laps under target. Driver must execute lift and coast immediately.",
            "Critical": "Extreme fuel warning! Car will not finish the race on current engine map. Switch to Mix 1 now!"
        },
        "Overheating Issue": {
            "Low": "Coolant temps climbing in traffic. Monitor air intakes.",
            "Medium": "Power unit overheating! Intakes blocked by debris. Divert out of dirty air.",
            "High": "Engine temperatures critical! Reliability is decaying rapidly. Drop engine mode to save unit.",
            "Critical": "Engine thermal warning active! Emergency cooling mode required. Back off from the cars ahead!"
        },
        "Engine Mode Restriction": {
            "Low": "Engine map limited to save lifecycle. Pace slightly reduced.",
            "Medium": "MGU-K deployment restriction. Hybrid assist reduced. Overtaking power drops.",
            "High": "ICE power loss. Cylinder misfire detected. ERS must be used strategically to defend.",
            "Critical": "Power Unit in recovery mode! ICE producing 80% power. Reliability is severely hit."
        }
    }
    
    event_types = list(event_templates.keys())
    severities = ["Low", "Medium", "High", "Critical"]
    actions = ["Ignore", "Pit", "Push", "Save Tires", "Lift and Coast", "Change Engine Mode", "Defend"]
    
    events = []
    for i in range(1, num_events + 1):
        e_type = random.choice(event_types)
        severity = random.choice(severities)
        description = event_templates[e_type][severity]
        
        events.append({
            "event_id": f"EVT-{i:03d}",
            "event_type": e_type,
            "lap_range": f"{random.randint(1, 20)}-{random.randint(21, 50)}",
            "probability": round(random.uniform(0.01, 0.40), 2),
            "severity": severity,
            "description": description,
            "possible_actions": "|".join(random.sample(actions, k=random.randint(2, 4))),
            "expected_consequences": "Varies based on action and team attributes"
        })
    df = pd.DataFrame(events)
    df.to_csv(os.path.join(DATA_DIR, 'events.csv'), index=False)
    print(f"Generated {len(events)} events.")

def generate_weather():
    conditions = ["Sunny", "Cloudy", "Light Rain", "Heavy Rain", "Mixed Conditions"]
    weather_data = []
    for i, cond in enumerate(conditions):
        weather_data.append({
            "weather_id": f"WTH-{i+1}",
            "condition": cond,
            "track_temp_modifier": random.randint(-10, 10),
            "grip_modifier": round(random.uniform(0.5, 1.2), 2),
            "tire_wear_modifier": round(random.uniform(0.8, 1.5), 2)
        })
    df = pd.DataFrame(weather_data)
    df.to_csv(os.path.join(DATA_DIR, 'weather.csv'), index=False)
    print("Generated weather profiles.")

def generate_race_scenarios(num_scenarios=500):
    weather_conds = ["Sunny", "Cloudy", "Light Rain", "Heavy Rain", "Mixed Conditions"]
    tire_compounds = ["Soft", "Medium", "Hard", "Intermediate", "Wet"]
    driver_conds = ["Focused", "Frustrated", "Tired", "Confident"]
    
    scenarios = []
    for i in range(1, num_scenarios + 1):
        lap = random.randint(1, 60)
        pos = random.randint(1, 20)
        scenarios.append({
            "scenario_id": f"SCN-{i:04d}",
            "lap": lap,
            "position": pos,
            "gap_ahead": round(random.uniform(0.1, 15.0), 2),
            "gap_behind": round(random.uniform(0.1, 15.0), 2),
            "tire_age": random.randint(1, 30),
            "tire_compound": random.choice(tire_compounds),
            "weather": random.choice(weather_conds),
            "track_temp": random.randint(20, 50),
            "driver_condition": random.choice(driver_conds),
            "fuel_status": round(random.uniform(10.0, 100.0), 2),
            "event_trigger": f"EVT-{random.randint(1, 250):03d}" if random.random() > 0.7 else "None",
            "decision_options": "Box|Push|Save|Defend"
        })
    df = pd.DataFrame(scenarios)
    df.to_csv(os.path.join(DATA_DIR, 'race_scenarios.csv'), index=False)
    print(f"Generated {len(scenarios)} race scenarios.")

if __name__ == "__main__":
    generate_drivers()
    generate_teams()
    generate_events()
    generate_weather()
    generate_race_scenarios()
    print("All datasets generated successfully in 'data/' directory.")
