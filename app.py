from supabase import create_client
from dotenv import load_dotenv
import os

# Carica il file .env
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase= create_client(url, key)

response = supabase.table("user").select("*").execute()
data = response.data

name = data[0].get("name")
email = data[0].get("email")
psw = data[0].get("password")
print(name, email, psw)