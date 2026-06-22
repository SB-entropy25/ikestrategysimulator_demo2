import pandas as pd
import random
import os

class SimulationEngine:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.drivers = pd.read_csv(os.path.join(data_dir, 'drivers.csv'))
        self.teams = pd.read_csv(os.path.join(data_dir, 'teams.csv'))
        self.events = pd.read_csv(os.path.join(data_dir, 'events.csv'))
        self.weather = pd.read_csv(os.path.join(data_dir, 'weather.csv'))
        self.scenarios = pd.read_csv(os.path.join(data_dir, 'race_scenarios.csv'))

    def evaluate_quiz(self, answers):
        # Answers is a list of 5 integers (1-4 scale)
        aggression = 50 + (answers[0] * 12)
        risk_appetite = 50 + (answers[1] * 12)
        data_trust = 50 + ((5 - answers[2]) * 12)
        tire_management = 50 + ((5 - answers[3]) * 12)
        adaptability = 50 + (answers[4] * 12)

        driver_id = f"VX-{random.randint(10, 99)}"
        return {
            "driver_id": driver_id,
            "aggression": min(99, aggression),
            "risk_appetite": min(99, risk_appetite),
            "data_reliance": min(99, data_trust),
            "tire_management": min(99, tire_management),
            "adaptability": min(99, adaptability)
        }

    def process_decision(self, current_state, decision, driver_profile, upgrades):
        new_state = current_state.copy()
        
        # Upgrade Modifiers
        has_pit_crew = "Elite Pit Crew" in str(upgrades)
        has_tire_eng = "Tire Engineers" in str(upgrades)
        has_reliability = "Reliability Package" in str(upgrades)
        
        # Base compound stats
        compound = new_state.get("tire_compound", "Medium")
        wear_rate = 1.0
        pace_offset = 0.0 # Medium base
        
        if compound == "Soft":
            wear_rate = 1.6
            pace_offset = -0.8
        elif compound == "Hard":
            wear_rate = 0.7
            pace_offset = 0.6
        elif compound == "Intermediate":
            wear_rate = 1.2
            pace_offset = 1.5
        elif compound == "Wet":
            wear_rate = 1.0
            pace_offset = 3.0

        # Apply Upgrade / Driver Modifiers
        if has_tire_eng:
            wear_rate *= 0.8
        
        # Driver tire management stat modifies wear
        driver_tire_mod = 1.5 - (driver_profile.get("tire_management", 70) / 100.0)
        wear_rate *= driver_tire_mod

        # Wetter/Dampness matching logic (Simulating F1 track dampness %)
        dampness = new_state.get("track_dampness", 0)  # 0 to 100
        is_slick = compound in ["Soft", "Medium", "Hard"]
        
        wet_penalty = 0.0
        # If wet track and on slicks
        if dampness > 30 and is_slick:
            wet_penalty = (dampness - 30) * 0.15 # Massive time loss, up to 10s+ per lap
            # Risk of spin or crash increases
            new_state["reliability"] = max(0, new_state["reliability"] - random.randint(5, 15))
        # If dry track and on wet tires
        elif dampness < 20 and not is_slick:
            wet_penalty = (20 - dampness) * 0.2
            wear_rate *= 3.0 # Intermediate/Wet tires disintegrate on dry tracks

        # Process Decision Action
        if decision == "Push":
            wear = random.randint(12, 22) * wear_rate
            new_state["tire_health"] = max(0, new_state["tire_health"] - int(wear))
            
            # Overtaking success depends on driver aggression and current confidence
            agg = driver_profile.get("aggression", 70)
            conf = new_state.get("driver_confidence", 70)
            success_chance = (agg + conf) / 2
            
            if random.randint(0, 100) < success_chance:
                new_state["position"] = max(1, new_state["position"] - 1)
                new_state["gap_ahead"] = random.uniform(0.5, 2.0)
            else:
                # Failed attempt might lose time or damage reliability slightly
                new_state["gap_ahead"] += random.uniform(0.5, 1.2)
                
            new_state["fuel_load"] = max(0.0, new_state["fuel_load"] - random.uniform(3.5, 5.0))
            new_state["risk_efficiency"] += 12
            
            # Check for Fastest Lap Bonus: Pushing on low fuel and soft/fresh tires
            if compound == "Soft" and new_state["fuel_load"] < 40 and new_state["tire_health"] > 50:
                new_state["fastest_lap_bonus"] = 50
            
        elif decision == "Save Tires":
            wear = random.randint(3, 7) * wear_rate
            new_state["tire_health"] = max(0, new_state["tire_health"] - int(wear))
            new_state["gap_ahead"] += random.uniform(0.8, 1.8) # Lose some pace
            new_state["fuel_load"] = max(0.0, new_state["fuel_load"] - random.uniform(1.2, 2.0))
            new_state["resource_management"] += 15
            
        elif decision == "Pit":
            new_state["tire_health"] = 100
            # Elite pit crew reduces pit lane loss
            pit_loss = 18.5 if has_pit_crew else 23.0
            new_state["gap_ahead"] += pit_loss
            new_state["pit_stops"] += 1
            new_state["resource_management"] += 10
            # Reset tire age
            new_state["tire_age"] = 0
            
        elif decision == "Defend":
            wear = random.randint(8, 14) * wear_rate
            new_state["tire_health"] = max(0, new_state["tire_health"] - int(wear))
            new_state["gap_behind"] = max(0.5, new_state["gap_behind"] + random.uniform(0.5, 1.5))
            new_state["risk_efficiency"] += 5

        # Tire cliff check
        if new_state["tire_health"] < 30:
            cliff_penalty = (30 - new_state["tire_health"]) * 0.2
            new_state["gap_ahead"] += cliff_penalty # Losing massive time
            # High risk of puncture
            if random.randint(0, 100) < (30 - new_state["tire_health"]):
                new_state["reliability"] = max(0, new_state["reliability"] - 30)
                new_state["driver_confidence"] = max(0, new_state["driver_confidence"] - 20)

        # Check for Critical Telemetry Penalties (Be mindful of actual F1 Tech/Sporting Regs)
        
        # 1. CRITICAL TYRES (<25% health)
        if current_state.get("tire_health", 100) < 25:
            if decision == "Push":
                if random.randint(0, 100) < 60: # 60% chance of tire blowout
                    new_state["reliability"] = 0
                    new_state["driver_confidence"] = 0
                    new_state["position"] = 20 # DNF
                    new_state["strategy_bonus"] = new_state.get("strategy_bonus", 0) - 100
                    print("[F1 PENALTY] Tire blowout! Terminal puncture from pushing on dead tires.")
            elif decision == "Defend":
                if random.randint(0, 100) < 30: # 30% chance of minor puncture
                    new_state["reliability"] = max(0, new_state["reliability"] - 40)
                    new_state["gap_ahead"] += 15.0 # Crawls to pitlane
                    print("[F1 PENALTY] Minor tire puncture under defense.")

        # 2. CRITICAL FUEL (<8.0 kg)
        if current_state.get("fuel_load", 110.0) < 8.0:
            if decision in ["Push", "Defend"]:
                fuel_burn = random.uniform(3.5, 5.0)
                new_state["fuel_load"] = max(0.0, new_state["fuel_load"] - fuel_burn)
                if new_state["fuel_load"] <= 0.0:
                    new_state["position"] = 20 # DSQ / DNF
                    new_state["reliability"] = 0
                    new_state["strategy_bonus"] = new_state.get("strategy_bonus", 0) - 150
                    print("[F1 PENALTY] Disqualified! Car stopped on track with zero fuel (F1 Tech Reg 6.6.2).")

        # 3. CRITICAL RELIABILITY / SUB-SYSTEMS (<25% reliability)
        if current_state.get("reliability", 100) < 25:
            if decision == "Push":
                if random.randint(0, 100) < 70: # 70% chance of PU failure
                    new_state["reliability"] = 0 # Terminal engine blowout
                    new_state["position"] = 20 # DNF
                    new_state["driver_confidence"] = max(0, new_state["driver_confidence"] - 50)
                    new_state["strategy_bonus"] = new_state.get("strategy_bonus", 0) - 120
                    print("[F1 PENALTY] Engine Blowout DNF! Pushing on terminal power unit temperatures.")
            elif decision == "Defend":
                if random.randint(0, 100) < 40:
                    new_state["reliability"] = 0 # Component failure DNF
                    new_state["position"] = 20
                    new_state["strategy_bonus"] = new_state.get("strategy_bonus", 0) - 80

        # 4. WET TRACK ON SLICKS (>35% track dampness on slick tires)
        is_slick = compound in ["Soft", "Medium", "Hard"]
        if dampness > 35 and is_slick:
            if decision in ["Push", "Defend"]:
                if random.randint(0, 100) < 65: # 65% chance of spin/crash into wall
                    new_state["reliability"] = 0 # Crash DNF
                    new_state["position"] = 20
                    new_state["driver_confidence"] = 10
                    new_state["strategy_bonus"] = new_state.get("strategy_bonus", 0) - 130
                    print("[F1 PENALTY] Crash DNF! Spun off into the barriers on slick tires in wet conditions.")

        # Reliability decay
        rel_decay = random.randint(1, 4)
        if has_reliability:
            rel_decay = int(rel_decay * 0.5)
        new_state["reliability"] = max(0, new_state["reliability"] - rel_decay)

        # Weather simulation progression
        if dampness > 0:
            # Randomly fluctuate dampness based on weather condition
            new_state["track_dampness"] = max(0, min(100, dampness + random.randint(-15, 20)))

        new_state["lap"] += random.randint(4, 7)
        new_state["tire_age"] = new_state.get("tire_age", 0) + (new_state["lap"] - current_state["lap"])
        
        return new_state

    def generate_radio_message(self, state):
        # Terminal messages if the car has retired (DNF/DSQ)
        if state.get("reliability", 100) <= 0:
            if state.get("fuel_load", 10.0) <= 0.0:
                return "Engine sputtered out. I'm completely out of fuel. Technical disqualification... stopping on track."
            elif state.get("tire_health", 100) < 10:
                return "The rear tire blew out at high speed! Suspension is damaged, I'm sliding into the barriers. It's over."
            elif state.get("track_dampness", 0) > 35 and state.get("tire_compound") in ["Soft", "Medium", "Hard"]:
                return "I've lost the rear! Aqua-planing... I'm in the barrier at Turn 4. Extensive wing and floor damage. I'm out."
            else:
                return "Smoke in the cockpit! Loss of drive, gearbox is locked. I'm stopping the car next to a marshal post."

        messages = [
            "Tires are holding up fine, let's keep going.",
            "Getting some front-wing vibration, can you check telemetry?",
            "The balance feels off in the mid-speed corners.",
            "Engine temperatures are getting high in dirty air.",
            "Radar reports rain might be heading our way soon."
        ]
        if state.get("tire_health", 100) < 35:
            messages.append("I'm skating on ice here! The tires are completely dead!")
        if state.get("reliability", 100) < 60:
            messages.append("EAP Warning on the dash. I'm losing power on the straight!")
        return random.choice(messages)

    def generate_commentary(self, state, decision):
        if decision == "Pit":
            return "That's the call. Strategists reacting to the telemetry. Standard pitstop duration is around 22 seconds."
        elif decision == "Push":
            return "The engineer is giving the green light. ERS mode active, driving at the limit!"
        elif decision == "Save Tires":
            return "Managing the delta. Strategic lift-and-coast to save rubber and engine lifecycle."
        return "Tactical stand-off. Maintaining position in the DRS train."

    def calculate_final_score(self, state):
        pos = state.get("position", 10)
        
        # F1 Championship points mapping scaled to 500 max points (F1 points * 20)
        f1_points_map = {
            1: 500,  # P1
            2: 360,  # P2
            3: 300,  # P3
            4: 240,  # P4
            5: 200,  # P5
            6: 160,  # P6
            7: 120,  # P7
            8: 80,   # P8
            9: 40,   # P9
            10: 20,  # P10
        }
        race_result_score = f1_points_map.get(pos, 10)
        if pos > 20 or state.get("reliability", 100) <= 0:
            race_result_score = 0  # DNF
            
        # Strategy accuracy based on decisions and upgrades (up to 150 points)
        strategy_score = min(150, 50 + state.get("strategy_bonus", 0) + int(state.get("risk_efficiency", 50) * 0.8))
        
        # Tire preservation (up to 120 points)
        tire_score = min(120, int(state.get("tire_health", 50) * 1.2))
        
        # Fuel & energy efficiency (up to 100 points)
        fuel_ers_score = min(100, int((state.get("fuel_load", 10.0) / 110.0 * 50) + (state.get("ers_percent", 50) / 100.0 * 50)))
        
        # Subsystem reliability preservation (up to 80 points)
        reliability_score = min(80, int(state.get("reliability", 80) * 0.8))
        
        # Driver confidence & synergy (up to 50 points)
        driver_score = min(50, int(state.get("driver_confidence", 50) * 0.5))
        
        # Fastest Lap Bonus (up to 50 points)
        fastest_lap_score = state.get("fastest_lap_bonus", 0)
        
        total = race_result_score + strategy_score + tire_score + fuel_ers_score + reliability_score + driver_score + fastest_lap_score
        
        return {
            "race_result": race_result_score,
            "strategy_accuracy": strategy_score,
            "tire_management": tire_score,
            "fuel_ers_efficiency": fuel_ers_score,
            "car_preservation": reliability_score,
            "driver_confidence": driver_score,
            "fastest_lap_bonus": fastest_lap_score,
            "total_score": total
        }
