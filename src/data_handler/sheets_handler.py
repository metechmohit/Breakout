import os
import pandas as pd
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import GOOGLE_SCOPES

class GoogleSheetsHandler:
    """Handles Google Sheets integration"""
    
    def __init__(self):
        self.SCOPES = GOOGLE_SCOPES
        
    def authenticate(self):
        """Authenticate with Google Sheets API"""
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds
        
    def read_sheet(self, sheet_id: str, range_name: str) -> pd.DataFrame:
        """Read data from Google Sheet"""
        try:
            creds = self.authenticate()
            service = build('sheets', 'v4', credentials=creds)
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
            values = result.get('values', [])
            if not values:
                return pd.DataFrame()
            return pd.DataFrame(values[1:], columns=values[0])
        except Exception as e:
            st.error(f"Error reading Google Sheet: {str(e)}")
            return pd.DataFrame()
            
    def write_results(self, sheet_id: str, range_name: str, data: pd.DataFrame):
        """Write results back to Google Sheet"""
        try:
            creds = self.authenticate()
            service = build('sheets', 'v4', credentials=creds)
            values = [data.columns.tolist()] + data.values.tolist()
            body = {'values': values}
            service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            st.success("Results written to Google Sheet successfully!")
        except Exception as e:
            st.error(f"Error writing to Google Sheet: {str(e)}")