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

BASE_DIR = os.path.join(os.getcwd(), "base")
os.makedirs(BASE_DIR, exist_ok=True)

MAPA_DIV = {
    # INGLATERRA
    'E0': 'Premier League',
    'E1': 'Championship',
    'E2': 'League One',
    'E3': 'League Two',
    'EC': 'National League',

    # ESCÓCIA
    'SC0': 'Scottish Premiership',
    'SC1': 'Scottish Championship',
    'SC2': 'Scottish League One',
    'SC3': 'Scottish League Two',

    # ALEMANHA
    'D1': 'Bundesliga',
    'D2': '2. Bundesliga',

    # ITÁLIA
    'I1': 'Serie A',
    'I2': 'Serie B',

    # ESPANHA
    'SP1': 'La Liga',
    'SP2': 'La Liga 2',

    # FRANÇA
    'F1': 'Ligue 1',
    'F2': 'Ligue 2',

    # PORTUGAL
    'P1': 'Primeira Liga',

    # HOLANDA
    'N1': 'Eredivisie',

    # BÉLGICA
    'B1': 'Jupiler Pro League',

    # TURQUIA
    'T1': 'Süper Lig',

    # GRÉCIA
    'G1': 'Super League Greece',
    
    # ARGENTINA
    'Argentina': 'Campeonato Argentino',

    # AUSTRIA
    'Austria': 'Campeonato Austríaco',

    # BRASIL
    'Brazil': 'Campeonato Brasileiro',

    # CHINA
    'China': 'Campeonato Chinês',

    # DINAMARCA
    'Denmark': 'Campeonato Dinamarquês',

    # FINLÂNDIA
    'Finland': 'Campeonato Finlandês',

    # IRLANDA
    'Ireland': 'Campeonato Irlandês',

    # JAPÃO
    'Japan': 'Campeonato Japonês',

    # MÉXICO
    'Mexico': 'Campeonato Mexicano',

    # NORUEGA
    'Norway': 'Campeonato Norueguês',

    # POLÔNIA
    'Poland': 'Campeonato Polonês',

    # ROMÊNIA
    'Romania': 'Campeonato Romeno',

    # RÚSSIA
    'Russia': 'Campeonato Russo',

    # SUÉCIA
    'Sweden': 'Campeonato Sueco',

    # SUÍÇA
    'Switzerland': 'Campeonato Suíço',

    # ESTADOS UNIDOS
    'USA': 'Campeonato Norte-Americano'
    
}


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
        "text": mensagem
        ,"parse_mode": "Markdown"
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


def baixar_jogos_main(destino):
    soup = BeautifulSoup(
        requests.get("https://www.football-data.co.uk/matches.php").text,
        "html.parser"
    )

    link = soup.find("a", href=lambda x: x and "fixtures.xlsx" in x)
    if not link:
        print("❌ Link de fixtures não encontrado")
        return

    url = BASE_SITE + link["href"]

    response = requests.get(url)

    with open(destino, "wb") as f:
        f.write(response.content)

    df = pd.read_excel(destino)
    df = df[['Div','Date','Time','HomeTeam','AwayTeam']]
    df.columns = ['Div','Data','Hora','Mandante','Visitante']
    df.to_excel(destino, index=False)

    print("📄 Jogos MAIN baixados:")



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

def dividir_em_blocos(lista, tamanho=10):
    for i in range(0, len(lista), tamanho):
        yield lista[i:i + tamanho]

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

#arquivo_extra = os.path.join(BASE_DIR, "JogosAdicionais.xlsx")
#if os.path.exists(arquivo_extra):
#    arquivos.append(arquivo_extra)


lista = []

for arq in arquivos:
    df = pd.read_excel(arq)
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
    df['Hora'] = df['Hora'].astype(str).str[:5]
    lista.append(df)
    nome_arq = os.path.basename(arq)

jogos = pd.concat(lista).sort_values(['Data','Hora'])

jogos['Div'] = jogos['Div'].map(MAPA_DIV).fillna(jogos['Div'])


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



jogos['Hora'] = pd.to_datetime(jogos['Hora'], format='%H:%M', errors='coerce').dt.time
jogos['Data/Hora'] = jogos.apply(
    lambda x: pd.Timestamp.combine(x['Data'].date(), x['Hora']), axis=1
) - pd.Timedelta(hours=3)

agora = pd.Timestamp.now()
limite_up = agora + pd.Timedelta(hours=12)
limite_down = agora - pd.Timedelta(hours=3)

jogos = jogos[
    (jogos['Data/Hora'] >= limite_down) &
    (jogos['Data/Hora'] <= limite_up)
]

print("\n🧪 LOG 1 — Jogos após filtro de horário")
for _, j in jogos.iterrows():
    print(f"{j['Mandante']} x {j['Visitante']} | {j['Data/Hora']}")

clubs = Clubs.set_index('Time')

gmhtc_m = clubs.reindex(jogos['Mandante'])['GMHTC'].values
gshtf_v = clubs.reindex(jogos['Visitante'])['GSHTF'].values

jogos['Gols_HT_AJ'] = (gmhtc_m + gshtf_v) / 2

print("\n🧪 LOG 2 — Métricas por clube")
for _, j in jogos.iterrows():
    mand = j['Mandante']
    vis  = j['Visitante']

    print(f"\n{mand} x {vis}")
    print(" Mandante:")
    print(clubs.loc[mand] if mand in clubs.index else "❌ Não encontrado")

    print(" Visitante:")
    print(clubs.loc[vis] if vis in clubs.index else "❌ Não encontrado")

gmc_m = clubs.reindex(jogos['Mandante'])['GMC'].values
gsf_v = clubs.reindex(jogos['Visitante'])['GSF'].values

gmf10_v = clubs.reindex(jogos['Visitante'])['GMF10'].values
gsc10_m = clubs.reindex(jogos['Mandante'])['GSC10'].values

jogos['Gols_FT_AJ'] = (
    (gmc_m + gsf_v) / 2 +
    (gmf10_v + gsc10_m) / 2
)

print("\n🧪 LOG 3 — Cálculo de gols")
for _, j in jogos.iterrows():
    print(
        f"{j['Mandante']} x {j['Visitante']} | "
        f"Gols_FT_AJ: {j['Gols_FT_AJ']}"
    )

jogos['Gols_FT_AJ_AR'] = jogos['Gols_FT_AJ'].apply(arredondar_gols)


print("\n🧪 LOG 4 — Arredondamento")
for _, j in jogos.iterrows():
    print(
        f"{j['Mandante']} x {j['Visitante']} | "
        f"AJ: {j['Gols_FT_AJ']} → AR: {j['Gols_FT_AJ_AR']}"
    )

mensagens_telegram = []

for _, linha in jogos.iterrows():

    print(
        f"\n🧪 LOG 5 — Avaliando jogo: "
        f"{linha['Mandante']} x {linha['Visitante']}"
    )

    msgs = []

    gols_ft = linha['Gols_FT_AJ_AR']
    print(f"   Gols_FT_AJ_AR = {gols_ft}")

    if not pd.isna(gols_ft):
        linha_aposta = gols_ft - 0.5
        print(f"   Linha calculada = {linha_aposta}")

        if linha_aposta == 1.5:
            print("   👉 Condição: Over 1.5")
            msgs.append("*Mais de 1.5 gols no jogo*")

        elif linha_aposta > 1.5:
            protecao = linha_aposta - 1
            print(f"   👉 Condição: Over {linha_aposta}")
            msgs.append(
                f"*Mais de {linha_aposta} gols no jogo*\n"
                f"_(Se mais que {linha_aposta} gols estiver com odd maior ou igual a 1.90, apostar {protecao} gols)_"
            )
    else:
        print("   ❌ Gols_FT_AJ_AR é NaN")

    if not msgs:
        print("   ❌ Nenhuma tip gerada para este jogo")
        continue

    print("   ✅ TIP GERADA:", msgs)

    hora = linha['Data/Hora'].strftime('%H:%M')
    dia = linha['Data/Hora'].strftime('%d/%m')

    msg = (
        f"⚽ {linha['Div']}\n"
        f"🗓️ {dia}\n"
        f"🕒 {hora}\n"
        f"{linha['Mandante']} x {linha['Visitante']}\n\n"
        + "\n".join(msgs)
    )

    mensagens_telegram.append(msg)

# 🔽 FORA do loop
if mensagens_telegram:
    blocos = list(dividir_em_blocos(mensagens_telegram, 10))

    for i, bloco in enumerate(blocos, start=1):
        cabecalho = (
            "📊 *BOLETIM DE TIPS*\n"
            f"🗓️ {datetime.now().strftime('%d/%m')}\n"
            f"📦 Bloco {i}/{len(blocos)}\n\n"
        )

        separador = "\n\n" + "—" * 12 + "\n\n"
        texto = cabecalho + separador.join(bloco)

        enviado = enviar_telegram(texto)

        if enviado:
            print(f"📤 Telegram enviado: bloco {i}")
        else:
            print(f"❌ Falha ao enviar bloco {i}")

        time.sleep(1)  # evita rate limit

print("✅ Script finalizado com sucesso")

