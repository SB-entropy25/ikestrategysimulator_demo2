import pandas as pd
import os

class StorageHandler:
    def __init__(self, data_dir):
        self.participants_file = os.path.join(data_dir, 'participants.csv')
        self.excel_file = os.path.join(data_dir, 'results.xlsx')
        
        # Local fallback initialization
        if not os.path.exists(self.participants_file):
            df = pd.DataFrame(columns=[
                "team_id", "principal_name", "team_name", "driver_profile", 
                "upgrades", "race_position", "strategy_score", "total_score"
            ])
            df.to_csv(self.participants_file, index=False)
            
        # Try to initialize Google Sheets connection
        self.gsheets_enabled = False
        self.client = None
        self.sheet = None
        self.status_message = "Initializing..."
        self.error_details = None
        self.init_gsheets()

    def init_gsheets(self):
        try:
            # Try to load environment variables from a .env file
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                pass
                
            import gspread
            from google.oauth2.service_account import Credentials
            import json
            
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            creds = None
            
            # 1. Check environment variable GOOGLE_SERVICE_ACCOUNT_JSON
            env_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            if env_creds:
                try:
                    info = json.loads(env_creds)
                    creds = Credentials.from_service_account_info(info, scopes=scopes)
                except Exception as e:
                    print(f"[StorageHandler] Failed to parse GOOGLE_SERVICE_ACCOUNT_JSON env: {e}")
                    
            # 2. Check credentials.json file in root
            if not creds:
                root_cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
                if os.path.exists(root_cred_path):
                    creds = Credentials.from_service_account_file(root_cred_path, scopes=scopes)
                    
            # 3. Check Streamlit secrets
            if not creds:
                try:
                    import streamlit as st
                    sec_key = None
                    if "gcp_service_account" in st.secrets:
                        sec_key = "gcp_service_account"
                    elif "GOOGLE_SERVICE_ACCOUNT_JSON" in st.secrets:
                        sec_key = "GOOGLE_SERVICE_ACCOUNT_JSON"
                        
                    if sec_key:
                        secret_val = st.secrets[sec_key]
                        if isinstance(secret_val, str):
                            # It's a raw JSON string
                            info = json.loads(secret_val)
                        else:
                            # It's a TOML table / dict
                            info = dict(secret_val)
                        creds = Credentials.from_service_account_info(
                            info,
                            scopes=scopes
                        )
                except Exception as e:
                    print(f"[StorageHandler] Secrets load error: {e}")
                    self.error_details = f"Secrets load error ({type(e).__name__}): {str(e)}"
            
            if not creds:
                print("[StorageHandler] No Google credentials found. Using local storage fallback.")
                self.status_message = "Offline Mode (Local backup active)"
                self.error_details = "No Google Cloud credentials found in environment variables (GOOGLE_SERVICE_ACCOUNT_JSON), local credentials.json file, or Streamlit secrets."
                return
                
            self.client = gspread.authorize(creds)
            
            # Get spreadsheet ID/name from env or st.secrets
            spreadsheet_id = os.getenv("GSHEETS_SPREADSHEET_ID")
            spreadsheet_name = os.getenv("GSHEETS_SPREADSHEET_NAME")
            
            # Check streamlit secrets if env variables are empty
            if not spreadsheet_id or not spreadsheet_name:
                try:
                    import streamlit as st
                    spreadsheet_id = spreadsheet_id or st.secrets.get("GSHEETS_SPREADSHEET_ID")
                    spreadsheet_name = spreadsheet_name or st.secrets.get("GSHEETS_SPREADSHEET_NAME")
                except Exception:
                    pass
            
            # Default fallback name
            if not spreadsheet_id and not spreadsheet_name:
                spreadsheet_name = "F1 War Room Leaderboard"
                
            if spreadsheet_id:
                # Auto-extract ID if the user provided a full Google Sheet URL
                if "docs.google.com/spreadsheets" in spreadsheet_id or spreadsheet_id.startswith("http"):
                    import re
                    match = re.search(r"/d/([a-zA-Z0-9-_]+)", spreadsheet_id)
                    if match:
                        spreadsheet_id = match.group(1)
                        
                self.spreadsheet = self.client.open_by_key(spreadsheet_id)
            else:
                self.spreadsheet = self.client.open(spreadsheet_name)
                
            self.sheet = self.spreadsheet.get_worksheet(0)
            self.gsheets_enabled = True
            self.status_message = f"Connected to Google Sheets: {self.spreadsheet.title}"
            self.error_details = None
            print(f"[StorageHandler] Google Sheets connected successfully to: {self.spreadsheet.title}")
            
            # Ensure headers exist on the sheet
            headers = [
                "team_id", "principal_name", "team_name", "driver_profile", 
                "upgrades", "race_position", "strategy_score", "total_score"
            ]
            
            existing_headers = self.sheet.row_values(1)
            if not existing_headers:
                self.sheet.insert_row(headers, 1)
                
        except Exception as e:
            print(f"[StorageHandler] Error initializing Google Sheets: {e}. Falling back to local storage.")
            self.gsheets_enabled = False
            self.status_message = "Connection Error (Local backup active)"
            self.error_details = f"{type(e).__name__}: {str(e)}"

    def save_participant(self, p_data):
        # Always save locally as a backup
        self.save_local(p_data)
        
        # Save to Google Sheets if enabled
        if self.gsheets_enabled and self.sheet:
            try:
                # Find if team_id already exists in sheet
                col_team_ids = self.sheet.col_values(1)  # team_id is in column 1
                
                row_data = [
                    p_data["team_id"],
                    p_data["principal_name"],
                    p_data["team_name"],
                    str(p_data["driver_profile"]),
                    str(p_data["upgrades"]),
                    int(p_data["race_position"]),
                    int(p_data["strategy_score"]),
                    int(p_data["total_score"])
                ]
                
                if p_data["team_id"] in col_team_ids:
                    row_idx = col_team_ids.index(p_data["team_id"]) + 1  # 1-indexed
                    self.sheet.update(range_name=f"A{row_idx}:H{row_idx}", values=[row_data])
                    print(f"[StorageHandler] Updated Google Sheets row {row_idx} for team {p_data['team_id']}")
                else:
                    self.sheet.append_row(row_data)
                    print(f"[StorageHandler] Appended new row to Google Sheets for team {p_data['team_id']}")
            except Exception as e:
                print(f"[StorageHandler] Error saving to Google Sheets: {e}")

    def save_local(self, p_data):
        df = pd.read_csv(self.participants_file)
        
        # Check if team_id already exists to update or append
        if p_data["team_id"] in df["team_id"].values:
            idx = df.index[df['team_id'] == p_data["team_id"]].tolist()[0]
            for key, val in p_data.items():
                df.at[idx, key] = val
        else:
            new_row = pd.DataFrame([p_data])
            df = pd.concat([df, new_row], ignore_index=True)
            
        df.to_csv(self.participants_file, index=False)
        self.export_to_excel()
        
    def export_to_excel(self):
        df = pd.read_csv(self.participants_file)
        if df.empty:
            return
            
        df = df.sort_values(by="total_score", ascending=False).reset_index(drop=True)
        df.insert(0, "Rank", df.index + 1)
        df.to_excel(self.excel_file, index=False)
        
    def get_leaderboard(self, top_n=10):
        if self.gsheets_enabled and self.sheet:
            try:
                records = self.sheet.get_all_records()
                if records:
                    df = pd.DataFrame(records)
                    
                    df["total_score"] = pd.to_numeric(df["total_score"], errors='coerce')
                    df["race_position"] = pd.to_numeric(df["race_position"], errors='coerce')
                    df["strategy_score"] = pd.to_numeric(df["strategy_score"], errors='coerce')
                    
                    df = df.sort_values(by="total_score", ascending=False).reset_index(drop=True)
                    df.insert(0, "Rank", df.index + 1)
                    return df.head(top_n)
            except Exception as e:
                print(f"[StorageHandler] Error reading leaderboard from Google Sheets: {e}. Using local fallback.")
                
        # Local fallback
        df = pd.read_csv(self.participants_file)
        if df.empty:
            return pd.DataFrame()
            
        df = df.sort_values(by="total_score", ascending=False).reset_index(drop=True)
        df.insert(0, "Rank", df.index + 1)
        return df.head(top_n)
