from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv("VT_HOST"))
print(os.getenv("UNKOWN_VAR"))

