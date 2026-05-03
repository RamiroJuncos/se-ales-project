from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import time
import iqoptionapi.stable_api as iq

app = FastAPI()

# CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Guardo las sesiones en memoria
sesiones = {}

class LoginData(BaseModel):
    usuario: str
    clave: str
    cuenta_demo: bool

# Aca puedo ver que la API esta funcionando
@app.get("/")
def root():
    return {"status": "API funcionando"}    

@app.post("/login")
def login(data: LoginData):
    try:
        api = iq.IQ_Option(data.usuario, data.clave)
        ok, msg = api.connect()

        if not ok:
            return {"error": msg}

        api.change_balance("PRACTICE" if data.cuenta_demo else "REAL")

        sesiones[data.usuario] = api

        return {"status": "conectado"}

    except Exception as e:
        return {"error": str(e)}

@app.get("/senal")
def obtener_senal(usuario: str):
    if usuario not in sesiones:
        return {"error": "No conectado"}

    api = sesiones[usuario]

    try:
        velas = api.get_candles('EURUSD', 60, 10, time.time())
        closes = [v['close'] for v in velas]

        ema3 = sum(closes[-3:]) / 3
        ema8 = sum(closes[-8:]) / 8
        precio = closes[-1]
        momento = precio - closes[-2]

        if ema3 > ema8 and momento > 0:
            señal = "🟢 ARRIBA"
        elif ema3 < ema8 and momento < 0:
            señal = "🔴 ABAJO"
        else:
            señal = "🔘 ESPERAR"

        return {
           "senal": "🟢 ARRIBA",
            "precio": 1.2345,
            "hora": "12:00:00"
        }

    except Exception as e:
        return {"error": str(e)}