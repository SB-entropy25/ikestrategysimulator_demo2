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
    event_types = [
        "Safety Car", "Virtual Safety Car", "Red Flag", "Rain Starts", "Rain Stops",
        "Brake Failure Warning", "Hydraulic Warning", "Driver Complaint",
        "Pit Lane Congestion", "Undercut Threat", "Overcut Opportunity",
        "Tire Blistering", "Track Evolution", "Yellow Flag", "Front Wing Damage",
        "Gearbox Alert", "DRS Train", "Fuel Concern", "Overheating Issue",
        "Engine Mode Restriction"
    ]
    
    severities = ["Low", "Medium", "High", "Critical"]
    actions = ["Ignore", "Pit", "Push", "Save Tires", "Lift and Coast", "Change Engine Mode", "Defend"]
    
    events = []
    for i in range(1, num_events + 1):
        e_type = random.choice(event_types)
        severity = random.choice(severities)
        
        events.append({
            "event_id": f"EVT-{i:03d}",
            "event_type": e_type,
            "lap_range": f"{random.randint(1, 20)}-{random.randint(21, 50)}",
            "probability": round(random.uniform(0.01, 0.40), 2),
            "severity": severity,
            "description": f"Detected {e_type} with {severity} severity.",
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
