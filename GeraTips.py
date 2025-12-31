import pandas as pd
import os
import glob
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# =========================
# CONFIGURAÇÃO DE DIRETÓRIOS (PORTÁVEL)
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DATA = os.path.join(BASE_DIR, "base")
os.makedirs(BASE_DATA, exist_ok=True)

# =========================
# TELEGRAM (VIA SECRETS)
# =========================
def enviar_telegram(mensagem):
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if not TOKEN or not CHAT_ID:
        print("⚠️ Token ou Chat ID não configurado")
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

    return [(inicio - i, inicio - i + 1) for i in range(qtd)]


def calcular_media(df, time, condicao, col_gm, col_gs):
    jogos = df[condicao].copy().sort_values(by=['Data', 'Hora'], ascending=False).head(10)
    if jogos.empty:
        return None
    gols = jogos[col_gm].sum() + jogos[col_gs].sum()
    return gols / len(jogos)


def calcular_gm10(time):
    return calcular_media(
        temporadas,
        time,
        (temporadas['Mandante'] == time) | (temporadas['Visitante'] == time),
        'GM',
        'GS'
    )


def calcular_gs10(time):
    return calcular_media(
        temporadas,
        time,
        (temporadas['Mandante'] == time) | (temporadas['Visitante'] == time),
        'GS',
        'GM'
    )


def calcular_gmht(time):
    return calcular_media(
        temporadas,
        time,
        (temporadas['Mandante'] == time) | (temporadas['Visitante'] == time),
        'GM1T',
        'GS1T'
    )


def calcular_gsht(time):
    return calcular_media(
        temporadas,
        time,
        (temporadas['Mandante'] == time) | (temporadas['Visitante'] == time),
        'GS1T',
        'GM1T'
    )


def calcular_gmc(time):
    return calcular_media(
        temporadas,
        time,
        temporadas['Mandante'] == time,
        'GM',
        'GM'
    )


def calcular_gmhtc(time):
    return calcular_media(
        temporadas,
        time,
        temporadas['Mandante'] == time,
        'GM1T',
        'GM1T'
    )


def calcular_gsf(time):
    return calcular_media(
        temporadas,
        time,
        temporadas['Visitante'] == time,
        'GM',
        'GM'
    )


def calcular_gshtf(time):
    return calcular_media(
        temporadas,
        time,
        temporadas['Visitante'] == time,
        'GS1T',
        'GS1T'
    )


# =========================
# DOWNLOAD DE DADOS
# =========================
BASE_PAGE = "https://www.football-data.co.uk/matches_new_leagues.php"
BASE_SITE = "https://www.football-data.co.uk/"


def baixar_jogos_extra(destino):
    print("🔄 Acessando página de fixtures...")
    soup = BeautifulSoup(requests.get(BASE_PAGE).text, "html.parser")
    link = soup.find("a", href=lambda x: x and "new_league_fixtures" in x)

    if not link:
        raise Exception("Link de fixtures não encontrado")

    url_download = link["href"]
    if not url_download.startswith("http"):
        url_download = BASE_SITE + url_download

    print("⬇️ Baixando:", url_download)
    arquivo = requests.get(url_download)

    pasta = os.path.dirname(destino)
    if pasta:
        os.makedirs(pasta, exist_ok=True)

    with open(destino, "wb") as f:
        f.write(arquivo.content)

    df = pd.read_excel(destino)
    df = df[['Country', 'Date', 'Time', 'Home', 'Away']]
    df.columns = ['Div', 'Data', 'Hora', 'Mandante', 'Visitante']
    df.to_excel(destino, index=False)


def baixar_temp_extra():
    page = requests.get("https://www.football-data.co.uk/all_new_data.php").text
    soup = BeautifulSoup(page, "html.parser")
    link = soup.find("a", href=lambda x: x and "new_leagues_data.xlsx" in x)

    url = BASE_SITE + link["href"]
    destino = os.path.join(BASE_DATA, "TempExtra.xlsx")

    with open(destino, "wb") as f:
        f.write(requests.get(url).content)


def baixar_temp_main(qtd):
    soup = BeautifulSoup(
        requests.get("https://www.football-data.co.uk/downloadm.php").text,
        "html.parser"
    )

    for ini, fim in temporadas_recentes(qtd):
        nome = f"all-euro-data-{ini}-{fim}.xlsx"
        link = soup.find("a", href=lambda x: x and nome in x)
        if not link:
            continue

        url = BASE_SITE + link["href"]
        destino = os.path.join(BASE_DATA, f"Temp{ini}{fim}.xlsx")

        with open(destino, "wb") as f:
            f.write(requests.get(url).content)


# =========================
# MAIN
# =========================
baixar_jogos_extra(os.path.join(BASE_DATA, "JogosExtra.xlsx"))
baixar_temp_extra()
baixar_temp_main(3)

arquivos = glob.glob(os.path.join(BASE_DATA, "*.xlsx"))

dfs = []
for arq in arquivos:
    if "Jogos" in arq:
        df = pd.read_excel(arq)
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        df['Hora'] = df['Hora'].astype(str).str[:5]
        dfs.append(df)

jogos = pd.concat(dfs).sort_values(by=['Data', 'Hora'])

temporadas = []
for arq in glob.glob(os.path.join(BASE_DATA, "Temp*.xlsx")):
    abas = pd.read_excel(arq, sheet_name=None)
    for _, df in abas.items():
        if 'Country' in df.columns:
            df['HTHG'] = np.nan
            df['HTAG'] = np.nan

        df = df[['Div', 'Date', 'Time', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'HTHG', 'HTAG']]
        df.columns = ['Div', 'Data', 'Hora', 'Mandante', 'Visitante', 'GM', 'GS', 'GM1T', 'GS1T']
        temporadas.append(df)

temporadas = pd.concat(temporadas)

clubs = pd.unique(pd.concat([temporadas['Mandante'], temporadas['Visitante']]))
Clubs = pd.DataFrame({'Time': clubs})

Clubs['GM10'] = Clubs['Time'].apply(calcular_gm10)
Clubs['GS10'] = Clubs['Time'].apply(calcular_gs10)
Clubs['GMHT10'] = Clubs['Time'].apply(calcular_gmht)
Clubs['GSHT10'] = Clubs['Time'].apply(calcular_gsht)
Clubs['GMC'] = Clubs['Time'].apply(calcular_gmc)
Clubs['GMHTC'] = Clubs['Time'].apply(calcular_gmhtc)
Clubs['GSF'] = Clubs['Time'].apply(calcular_gsf)
Clubs['GSHTF'] = Clubs['Time'].apply(calcular_gshtf)

jogos.to_excel(os.path.join(BASE_DATA, "TIPS.xlsx"), index=False)
Clubs.to_excel(os.path.join(BASE_DATA, "Times.xlsx"), index=False)

for _, linha in jogos.iterrows():
    if linha.get('Gols_HT_AJ', 0) and linha['Gols_HT_AJ'] >= 0.6:
        enviar_telegram(f"{linha['Mandante']} x {linha['Visitante']} – Gols HT")
