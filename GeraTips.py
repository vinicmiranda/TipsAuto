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

def calcular_gsc10(time):
    jogos = temporadas[
        temporadas['Mandante'] == time
    ].sort_values(['Data','Hora'], ascending=False).head(10)

    if jogos.empty:
        return None

    return jogos['GS'].sum() / len(jogos)


def calcular_gmf10(time):
    jogos = temporadas[
        temporadas['Visitante'] == time
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

def arredondar_gols(valor):
    if pd.isna(valor):
        return None

    inteiro = int(valor)
    decimal = valor - inteiro

    return inteiro + 1 if decimal >= 0.7 else inteiro

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
    print("📄 Jogos EXTRA baixados:")
    print(df[['Data','Hora','Mandante','Visitante']])

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
    print("📄 Jogos MAIN baixados:")
    print(df[['Data','Hora','Mandante','Visitante']])

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

arquivo_extra = os.path.join(BASE_DIR, "JogosAdicionais.xlsx")
if os.path.exists(arquivo_extra):
    arquivos.append(arquivo_extra)


lista = []

for arq in arquivos:
    df = pd.read_excel(arq)
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
    df['Hora'] = df['Hora'].astype(str).str[:5]
    lista.append(df)
    nome_arq = os.path.basename(arq)
    print(f"📄 Jogos carregados do arquivo {nome_arq}:")
    print(df[['Data','Hora','Mandante','Visitante']])

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
Clubs['GSC10'] = Clubs['Time'].apply(calcular_gsc10)
Clubs['GMF10'] = Clubs['Time'].apply(calcular_gmf10)

###################################
# FIXTURES + ALERTAS
###################################


agora = pd.Timestamp.now()
limite = agora + pd.Timedelta(minutes=60)

jogos['Hora'] = pd.to_datetime(jogos['Hora'], format='%H:%M', errors='coerce').dt.time
jogos['Data/Hora'] = jogos.apply(
    lambda x: pd.Timestamp.combine(x['Data'].date(), x['Hora']), axis=1
) - pd.Timedelta(hours=3)

hoje = pd.Timestamp.now().normalize()

jogos = jogos[
    jogos['Data/Hora'].dt.normalize() == hoje
]


clubs = Clubs.set_index('Time')

jogos['Gols_HT_AJ'] = (
    clubs.loc[jogos['Mandante'], 'GMHTC'].values +
    clubs.loc[jogos['Visitante'], 'GSHTF'].values
) / 2

jogos['Gols_FT_AJ'] = (
    (
        clubs.loc[jogos['Mandante'], 'GMC'].values +
        clubs.loc[jogos['Visitante'], 'GSF'].values
    ) / 2
    +
    (
        clubs.loc[jogos['Visitante'], 'GMF10'].values +
        clubs.loc[jogos['Mandante'], 'GSC10'].values
    ) / 2
)

jogos['Gols_FT_AJ_AR'] = jogos['Gols_FT_AJ'].apply(arredondar_gols)


for _, linha in jogos.iterrows():

    msgs = []

    # -------- PRIMEIRO TEMPO --------
    gols_ht = linha['Gols_HT_AJ']
    if not pd.isna(gols_ht) and gols_ht >= 0.60:
        if gols_ht >= 0.90:
            msgs.append("Mais de *1* gol no **Primeiro tempo**")
        else:
            msgs.append("Mais de *0.5* gol no **Primeiro tempo**")

    # -------- JOGO TODO --------
    gols_ft = linha['Gols_FT_AJ_AR']
    if not pd.isna(gols_ft) and gols_ft >= 1:
        msgs.append(f"Mais de {gols_ft - 0.5} gols no jogo")

    if not msgs:
        continue

    hora = linha['Data/Hora'].strftime('%H:%M')
    dia = linha['Data/Hora'].strftime('%d/%m')

    msg = f"""
⚽ *Próximo jogo*
🗓️ {dia}
🕒 {hora}
{linha['Mandante']} x {linha['Visitante']}

""" + "\n".join(msgs)

    enviar_telegram(msg)


print("✅ Script finalizado com sucesso")
