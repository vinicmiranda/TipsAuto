import pandas as pd
import os
import glob
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime

###################################
# CONFIGURAÇÕES GERAIS
###################################

BASE_SITE = "https://www.football-data.co.uk/"
BASE_PAGE = "https://www.football-data.co.uk/matches_new_leagues.php"

BASE_DIR = os.path.join(os.getcwd(), "base")
os.makedirs(BASE_DIR, exist_ok=True)

###################################
# TELEGRAM
###################################

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

###################################
# FUNÇÕES AUXILIARES
###################################

def temporadas_recentes(qtd):
    hoje = datetime.today()
    inicio = hoje.year - 1 if hoje.month < 8 else hoje.year
    return [(inicio - i, inicio - i + 1) for i in range(qtd)]

###################################
# MÉTRICAS
###################################

def calcular_gm10(time):
    jogos = temporadas[
        (temporadas['Mandante'] == time) |
        (temporadas['Visitante'] == time)
    ].sort_values(['Data','Hora'], ascending=False).head(10)

    if jogos.empty:
        return None

    gols = (
        jogos.loc[jogos['Mandante'] == time, 'GM'].sum() +
        jogos.loc[jogos['Visitante'] == time, 'GS'].sum()
    )
    return gols / len(jogos)

def calcular_gs10(time):
    jogos = temporadas[
        (temporadas['Mandante'] == time) |
        (temporadas['Visitante'] == time)
    ].sort_values(['Data','Hora'], ascending=False).head(10)

    if jogos.empty:
        return None

    gols = (
        jogos.loc[jogos['Mandante'] == time, 'GS'].sum() +
        jogos.loc[jogos['Visitante'] == time, 'GM'].sum()
    )
    return gols / len(jogos)

def calcular_gmht(time):
    jogos = temporadas[
        (temporadas['Mandante'] == time) |
        (temporadas['Visitante'] == time)
    ].sort_values(['Data','Hora'], ascending=False).head(10)

    if jogos.empty:
        return None

    gols = (
        jogos.loc[jogos['Mandante'] == time, 'GM1T'].sum() +
        jogos.loc[jogos['Visitante'] == time, 'GS1T'].sum()
    )
    return gols / len(jogos)

def calcular_gsht(time):
    jogos = temporadas[
        (temporadas['Mandante'] == time) |
        (temporadas['Visitante'] == time)
    ].sort_values(['Data','Hora'], ascending=False).head(10)

    if jogos.empty:
        return None

    gols = (
        jogos.loc[jogos['Mandante'] == time, 'GS1T'].sum() +
        jogos.loc[jogos['Visitante'] == time, 'GM1T'].sum()
    )
    return gols / len(jogos)

def calcular_gmc(time):
    jogos = temporadas[
        temporadas['Mandante'] == time
    ].sort_values(['Data','Hora'], ascending=False).head(10)

    if jogos.empty:
        return None

    return jogos['GM'].sum() / len(jogos)

def calcular_gmhtc(time):
    jogos = temporadas[
        temporadas['Mandante'] == time
    ].sort_values(['Data','Hora'], ascending=False).head(10)

    if jogos.empty:
        return None

    return jogos['GM1T'].sum() / len(jogos)

def calcular_gsf(time):
    jogos = temporadas[
        temporadas['Visitante'] == time
    ].sort_values(['Data','Hora'], ascending=False).head(10)

    if jogos.empty:
        return None

    return jogos['GM'].sum() / len(jogos)

def calcular_gshtf(time):
    jogos = temporadas[
        temporadas['Visitante'] == time
    ].sort_values(['Data','Hora'], ascending=False).head(10)

    if jogos.empty:
        return None

    return jogos['GS1T'].sum() / len(jogos)

###################################
# DOWNLOADS
###################################

def baixar_jogos_extra(destino):
    print("🔄 Acessando página de fixtures...")
    soup = BeautifulSoup(requests.get(BASE_PAGE).text, "html.parser")
    link = soup.find("a", href=lambda x: x and "new_league_fixtures" in x)

    url = link["href"]
    if not url.startswith("http"):
        url = BASE_SITE + url

    arq = requests.get(url)

    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "wb") as f:
        f.write(arq.content)

    df = pd.read_excel(destino)
    df = df[['Country','Date','Time','Home','Away']]
    df.columns = ['Div','Data','Hora','Mandante','Visitante']
    df.to_excel(destino, index=False)

def baixar_jogos_main(destino):
    soup = BeautifulSoup(
        requests.get("https://www.football-data.co.uk/matches.php").text,
        "html.parser"
    )
    link = soup.find("a", href=lambda x: x and "fixtures.xlsx" in x)
    url = BASE_SITE + link["href"]

    df = pd.read_excel(requests.get(url).content)
    df = df[['Div','Date','Time','HomeTeam','AwayTeam']]
    df.columns = ['Div','Data','Hora','Mandante','Visitante']
    df.to_excel(destino, index=False)

def baixar_temp_extra(destino_dir):
    soup = BeautifulSoup(
        requests.get("https://www.football-data.co.uk/all_new_data.php").text,
        "html.parser"
    )
    link = soup.find("a", href=lambda x: x and "new_leagues_data.xlsx" in x)
    url = BASE_SITE + link["href"]

    with open(os.path.join(destino_dir, "TempExtra.xlsx"), "wb") as f:
        f.write(requests.get(url).content)

def baixar_temp_main(destino_dir, qtd):
    soup = BeautifulSoup(
        requests.get("https://www.football-data.co.uk/downloadm.php").text,
        "html.parser"
    )

    for a1, a2 in temporadas_recentes(qtd):
        nome = f"all-euro-data-{a1}-{a2}.xlsx"
        link = soup.find("a", href=lambda x: x and nome in x)
        if not link:
            continue

        url = BASE_SITE + link["href"]
        with open(os.path.join(destino_dir, f"Temp{a1}{a2}.xlsx"), "wb") as f:
            f.write(requests.get(url).content)

###################################
# MAIN – DOWNLOAD
###################################

baixar_jogos_extra(os.path.join(BASE_DIR, "JogosExtra.xlsx"))
baixar_jogos_main(os.path.join(BASE_DIR, "JogosMain.xlsx"))
baixar_temp_extra(BASE_DIR)
baixar_temp_main(BASE_DIR, 3)

###################################
# CONSOLIDA JOGOS
###################################

arquivos = glob.glob(os.path.join(BASE_DIR, "Jogos*.xlsx"))
lista = []

for arq in arquivos:
    df = pd.read_excel(arq)
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
    df['Hora'] = df['Hora'].astype(str).str[:5]
    lista.append(df)

jogos = pd.concat(lista).sort_values(['Data','Hora'])

###################################
# CONSOLIDA TEMPORADAS
###################################

dfs = []
for arq in glob.glob(os.path.join(BASE_DIR, "Temp*.xlsx")):
    abas = pd.read_excel(arq, sheet_name=None)

    for _, df in abas.items():
        if "TempExtra" in arq:
            df = df.rename(columns={
                'Country':'Div','Home':'HomeTeam','Away':'AwayTeam',
                'HG':'FTHG','AG':'FTAG'
            })
            df['HTHG'] = np.nan
            df['HTAG'] = np.nan

        df = df[['Div','Date','Time','HomeTeam','AwayTeam','FTHG','FTAG','HTHG','HTAG']]
        dfs.append(df)

temporadas = pd.concat(dfs)
temporadas.columns = ['Div','Data','Hora','Mandante','Visitante','GM','GS','GM1T','GS1T']

###################################
# MÉTRICAS
###################################

Clubs = pd.concat([temporadas['Mandante'], temporadas['Visitante']]).drop_duplicates()
Clubs = pd.DataFrame({'Time':Clubs})

Clubs['GM10'] = Clubs['Time'].apply(calcular_gm10)
Clubs['GS10'] = Clubs['Time'].apply(calcular_gs10)
Clubs['GMHT10'] = Clubs['Time'].apply(calcular_gmht)
Clubs['GSHT10'] = Clubs['Time'].apply(calcular_gsht)
Clubs['GMC'] = Clubs['Time'].apply(calcular_gmc)
Clubs['GMHTC'] = Clubs['Time'].apply(calcular_gmhtc)
Clubs['GSF'] = Clubs['Time'].apply(calcular_gsf)
Clubs['GSHTF'] = Clubs['Time'].apply(calcular_gshtf)

###################################
# FIXTURES + ALERTAS
###################################

jogos['Hora'] = pd.to_datetime(jogos['Hora'], format='%H:%M', errors='coerce').dt.time
jogos['Data/Hora'] = jogos.apply(
    lambda x: pd.Timestamp.combine(x['Data'].date(), x['Hora']), axis=1
) - pd.Timedelta(hours=3)

clubs = Clubs.set_index('Time')

jogos['Gols_HT_AJ'] = (
    clubs.loc[jogos['Mandante'], 'GMHTC'].values +
    clubs.loc[jogos['Visitante'], 'GSHTF'].values
) / 2

agora = pd.Timestamp.now()
jogos = jogos[jogos['Data/Hora'] > agora]

for _, linha in jogos.iterrows():
    gols = linha['Gols_HT_AJ']
    if pd.isna(gols) or gols < 0.60:
        continue

    hora = linha['Data/Hora'].strftime('%H:%M')
    dia = linha['Data/Hora'].strftime('%d/%m')

    msg = f"""
⚽ *Próximo jogo*
🗓️ {dia}
🕒 {hora}
{linha['Mandante']} x {linha['Visitante']}
Gols HT: {'Acima de 1' if gols >= 0.90 else 'Acima de 0.5'}
"""
    print("DEBUG TOKEN:", "OK" if os.getenv("TELEGRAM_TOKEN") else "NÃO")
    print("DEBUG CHAT_ID:", "OK" if os.getenv("TELEGRAM_CHAT_ID") else "NÃO")
    enviar_telegram(msg)

print("✅ Script finalizado com sucesso")
