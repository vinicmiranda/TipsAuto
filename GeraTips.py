import pandas as pd
import os
import glob
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

###################################
# CONFIGURAÇÕES GERAIS
###################################

BASE_SITE = "https://www.football-data.co.uk/"
BASE_PAGE = "https://www.football-data.co.uk/matches_new_leagues.php"
ARQUIVO_JOGOS_GERADOS = os.path.join(os.getcwd(), "JogosGerados.xlsx")

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

def arredondar_gols(valor):
    if pd.isna(valor):
        return None
    inteiro = int(valor)
    return inteiro + 1 if valor - inteiro >= 0.7 else inteiro

###################################
# DOWNLOADS
###################################

def baixar_jogos_extra(destino):
    soup = BeautifulSoup(requests.get(BASE_PAGE).text, "html.parser")
    link = soup.find("a", href=lambda x: x and "new_league_fixtures" in x)

    url = link["href"]
    if not url.startswith("http"):
        url = BASE_SITE + url

    with open(destino, "wb") as f:
        f.write(requests.get(url).content)

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

###################################
# MAIN – DOWNLOAD
###################################

baixar_jogos_extra(os.path.join(BASE_DIR, "JogosExtra.xlsx"))
baixar_jogos_main(os.path.join(BASE_DIR, "JogosMain.xlsx"))

###################################
# CONSOLIDA JOGOS
###################################

lista = []
for arq in glob.glob(os.path.join(BASE_DIR, "Jogos*.xlsx")):
    df = pd.read_excel(arq)

    if 'Div' not in df.columns:
        df['Div'] = 'Desconhecido'

    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
    df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M', errors='coerce')
    df = df.dropna(subset=['Data','Hora'])
    lista.append(df)

if not lista:
    print("❌ Nenhum jogo carregado")
    exit()

jogos = pd.concat(lista, ignore_index=True)

jogos['Data/Hora'] = (
    jogos['Data'] +
    pd.to_timedelta(jogos['Hora'].dt.hour, unit='h') +
    pd.to_timedelta(jogos['Hora'].dt.minute, unit='m')
) - pd.Timedelta(hours=3)

###################################
# FILTRO DE HORÁRIO
###################################

agora = pd.Timestamp.now()

jogos = jogos[
    (jogos['Data/Hora'] >= agora - pd.Timedelta(hours=3)) &
    (jogos['Data/Hora'] <= agora + pd.Timedelta(hours=12))
]

print(f"Jogos após filtro de horário: {len(jogos)}")

###################################
# ALERTAS
###################################

jogos_alertados = []

for _, linha in jogos.iterrows():
    msgs = ["*Mais de 1.5 gols no jogo*"]

    msg = (
        f"⚽ *{linha['Div']}*\n"
        f"🗓️ {linha['Data/Hora'].strftime('%d/%m')}\n"
        f"🕒 {linha['Data/Hora'].strftime('%H:%M')}\n"
        f"{linha['Mandante']} x {linha['Visitante']}\n\n"
        + "\n".join(msgs)
    )

    enviado = enviar_telegram(msg)
    time.sleep(1)

    jogos_alertados.append({
        "Data": linha["Data/Hora"].date(),
        "Hora": linha["Data/Hora"].strftime("%H:%M"),
        "Divisão": linha["Div"],
        "Mandante": linha["Mandante"],
        "Visitante": linha["Visitante"],
        "Linha_Gols_FT": 1.5,
        "Telegram_Enviado": enviado,
        "Data_Execucao": pd.Timestamp.now()
    })

print(f"Total de jogos alertados: {len(jogos_alertados)}")

###################################
# SALVAMENTO NO EXCEL (BLINDADO)
###################################

if jogos_alertados:
    df_novos = pd.DataFrame(jogos_alertados)

    if os.path.exists(ARQUIVO_JOGOS_GERADOS):
        try:
            df_antigo = pd.read_excel(ARQUIVO_JOGOS_GERADOS)
            df_final = pd.concat([df_antigo, df_novos], ignore_index=True)
        except Exception:
            df_final = df_novos
    else:
        df_final = df_novos

    df_final = df_final.drop_duplicates(
        subset=["Data","Hora","Mandante","Visitante","Linha_Gols_FT"],
        keep="last"
    )

    df_final.to_excel(ARQUIVO_JOGOS_GERADOS, index=False)
    print("📊 Excel atualizado com sucesso")

else:
    print("ℹ️ Nenhum jogo para salvar")

print("✅ Script finalizado")
