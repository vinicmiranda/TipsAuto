import pandas as pd
import os
import glob
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from io import BytesIO

# =========================
# BASE DIR (multiplataforma)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DATA = os.path.join(BASE_DIR, "base")
os.makedirs(BASE_DATA, exist_ok=True)

BASE_PAGE = "https://www.football-data.co.uk/matches_new_leagues.php"
BASE_SITE = "https://www.football-data.co.uk/"

# =========================
# TELEGRAM
# =========================
def enviar_telegram(mensagem):
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if not TOKEN or not CHAT_ID:
        print("⚠️ Telegram não configurado")
        return False

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }

    r = requests.post(url, json=payload)
    return r.status_code == 200

# =========================
# FUNÇÕES AUXILIARES
# =========================
def temporadas_recentes(qtd):
    hoje = datetime.today()
    ano = hoje.year
    mes = hoje.month
    inicio = ano - 1 if mes < 8 else ano

    temporadas = []
    for i in range(qtd):
        a1 = inicio - i
        a2 = a1 + 1
        temporadas.append((a1, a2))

    return temporadas

# =========================
# DOWNLOAD FIXTURES EXTRA
# =========================
def baixar_jogos_extra(destino):
    print("🔄 Acessando página de fixtures...")
    response = requests.get(BASE_PAGE)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    link = soup.find("a", href=lambda x: x and "new_league_fixtures" in x)

    if not link:
        raise Exception("Link de fixtures não encontrado")

    url = link["href"]
    url = url if url.startswith("http") else BASE_SITE + url
    print("⬇️ Baixando:", url)

    arquivo = requests.get(url)
    arquivo.raise_for_status()

    pasta = os.path.dirname(destino)
    if pasta:
        os.makedirs(pasta, exist_ok=True)

    with open(destino, "wb") as f:
        f.write(arquivo.content)

    df = pd.read_excel(destino, engine="openpyxl")
    df = df[['Country', 'Date', 'Time', 'Home', 'Away']]
    df = df.rename(columns={
        'Country': 'Div',
        'Date': 'Data',
        'Time': 'Hora',
        'Home': 'Mandante',
        'Away': 'Visitante'
    })

    df.to_excel(destino, index=False)
    print("✅ Fixtures extra salvos")

# =========================
# DOWNLOAD FIXTURES MAIN
# =========================
def baixar_jogos_main(destino):
    page_url = "https://www.football-data.co.uk/matches.php"
    response = requests.get(page_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    link = soup.find("a", href=lambda x: x and x.strip() == "fixtures.xlsx")

    if not link:
        raise Exception("fixtures.xlsx não encontrado")

    url = BASE_SITE + link["href"]
    arquivo = requests.get(url)
    arquivo.raise_for_status()

    df = pd.read_excel(BytesIO(arquivo.content), engine="openpyxl")
    df = df[['Div', 'Date', 'Time', 'HomeTeam', 'AwayTeam']]
    df = df.rename(columns={
        'Date': 'Data',
        'Time': 'Hora',
        'HomeTeam': 'Mandante',
        'AwayTeam': 'Visitante'
    })

    df.to_excel(destino, index=False)

# =========================
# DOWNLOAD TEMPORADAS
# =========================
def baixar_temp_extra(destino_base):
    page_url = "https://www.football-data.co.uk/all_new_data.php"
    response = requests.get(page_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    link = soup.find("a", href=lambda x: x and "new_leagues_data.xlsx" in x)

    if not link:
        raise Exception("new_leagues_data.xlsx não encontrado")

    url = BASE_SITE + link["href"]
    arquivo = requests.get(url)
    arquivo.raise_for_status()

    with open(os.path.join(destino_base, "TempExtra.xlsx"), "wb") as f:
        f.write(arquivo.content)

def baixar_temp_main(destino_base, qtd):
    page_url = "https://www.football-data.co.uk/downloadm.php"
    response = requests.get(page_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    temporadas = temporadas_recentes(qtd)

    for ini, fim in temporadas:
        nome = f"all-euro-data-{ini}-{fim}.xlsx"
        link = soup.find("a", href=lambda x: x and nome in x)

        if not link:
            continue

        url = BASE_SITE + link["href"]
        arquivo = requests.get(url)
        arquivo.raise_for_status()

        destino = os.path.join(destino_base, f"Temp{ini}{fim}.xlsx")
        with open(destino, "wb") as f:
            f.write(arquivo.content)

# =========================
# MAIN
# =========================
destino_extra = os.path.join(BASE_DATA, "JogosExtra.xlsx")
destino_main = os.path.join(BASE_DATA, "JogosMain.xlsx")

baixar_jogos_extra(destino_extra)
baixar_jogos_main(destino_main)
baixar_temp_extra(BASE_DATA)
baixar_temp_main(BASE_DATA, 3)

print("✅ Downloads finalizados")
