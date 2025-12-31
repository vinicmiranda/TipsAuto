import pandas as pd
import os
import glob
import numpy as np
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def enviar_telegram(mensagem):
    TOKEN = "8573618362:AAE_NLqF21FTkk31Afb8YcCDKB3IBXN_7RI"
    ##CHAT_ID = "5968711732"
    CHAT_ID = "-5187415368"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }

    r = requests.post(url, json=payload)
    return r.status_code == 200

def temporadas_recentes(qtd):

    hoje = datetime.today()
    ano = hoje.year
    mes = hoje.month

    if mes < 8:
        inicio = ano - 1
    else:
        inicio = ano

    temporadas = []
    for i in range(qtd):
        a1 = inicio - i
        a2 = a1 + 1
        temporadas.append((a1, a2))

    return temporadas

def calcular_gm10(time):
    jogos_time = temporadas[
        (temporadas['Mandante'] == time) |
        (temporadas['Visitante'] == time)
    ].copy()

    jogos_time = jogos_time.sort_values(
        by=['Data', 'Hora'], ascending=[False, False]
    ).head(10)

    total_jogos = len(jogos_time)

    if total_jogos == 0:
        return None

    gols = (
        jogos_time.loc[jogos_time['Mandante'] == time, 'GM'].sum() +
        jogos_time.loc[jogos_time['Visitante'] == time, 'GS'].sum()
    )

    return gols / total_jogos

    jogos_time = ExtraHist[
        (ExtraHist['Mandante'] == time) |
        (ExtraHist['Visitante'] == time)
    ].copy()

    jogos_time = jogos_time.sort_values(
        by=['Data', 'Hora'], ascending=[False, False]
    ).head(10)

    total_jogos = len(jogos_time)

    if total_jogos == 0:
        return None

    gols = (
        jogos_time.loc[jogos_time['Mandante'] == time, 'GM'].sum() +
        jogos_time.loc[jogos_time['Visitante'] == time, 'GS'].sum()
    )

    return gols / total_jogos

def calcular_gs10(time):
    jogos_time = temporadas[
        (temporadas['Mandante'] == time) |
        (temporadas['Visitante'] == time)
    ].copy()

    jogos_time = jogos_time.sort_values(
        by=['Data', 'Hora'], ascending=[False, False]
    ).head(10)

    total_jogos = len(jogos_time)

    if total_jogos == 0:
        return None

    gols_sofridos = (
        jogos_time.loc[jogos_time['Mandante'] == time, 'GS'].sum() +
        jogos_time.loc[jogos_time['Visitante'] == time, 'GM'].sum()
    )

    return gols_sofridos / total_jogos

    jogos_time = ExtraHist[
        (ExtraHist['Mandante'] == time) |
        (ExtraHist['Visitante'] == time)
    ].copy()

    jogos_time = jogos_time.sort_values(
        by=['Data', 'Hora'], ascending=[False, False]
    ).head(10)

    total_jogos = len(jogos_time)

    if total_jogos == 0:
        return None

    gols_sofridos = (
        jogos_time.loc[jogos_time['Mandante'] == time, 'GS'].sum() +
        jogos_time.loc[jogos_time['Visitante'] == time, 'GM'].sum()
    )

    return gols_sofridos / total_jogos

def calcular_gmht(time):
    jogos_time = temporadas[
        (temporadas['Mandante'] == time) |
        (temporadas['Visitante'] == time)
    ].copy()

    jogos_time = jogos_time.sort_values(
        by=['Data', 'Hora'], ascending=[False, False]
    ).head(10)

    total_jogos = len(jogos_time)

    if total_jogos == 0:
        return None

    gols_1t = (
        jogos_time.loc[jogos_time['Mandante'] == time, 'GM1T'].sum() +
        jogos_time.loc[jogos_time['Visitante'] == time, 'GS1T'].sum()
    )

    return gols_1t / total_jogos

def calcular_gsht(time):
    jogos_time = temporadas[
        (temporadas['Mandante'] == time) |
        (temporadas['Visitante'] == time)
    ].copy()

    jogos_time = jogos_time.sort_values(
        by=['Data', 'Hora'], ascending=[False, False]
    ).head(10)

    total_jogos = len(jogos_time)

    if total_jogos == 0:
        return None

    gols_sofridos_1t = (
        jogos_time.loc[jogos_time['Mandante'] == time, 'GS1T'].sum() +
        jogos_time.loc[jogos_time['Visitante'] == time, 'GM1T'].sum()
    )

    return gols_sofridos_1t / total_jogos

def calcular_gmc(time):
    jogos_time = temporadas[
        temporadas['Mandante'] == time
    ].copy()

    jogos_time = jogos_time.sort_values(
        by=['Data', 'Hora'], ascending=[False, False]
    ).head(10)

    total_jogos = len(jogos_time)
    if total_jogos == 0:
        return None

    gols = jogos_time['GM'].sum()

    return gols / total_jogos

    jogos_time = ExtraHist[
        ExtraHist['Mandante'] == time
    ].copy()

    jogos_time = jogos_time.sort_values(
        by=['Data', 'Hora'], ascending=[False, False]
    ).head(10)

    total_jogos = len(jogos_time)
    if total_jogos == 0:
        return None

    gols = jogos_time['GM'].sum()

    return gols / total_jogos

def calcular_gmhtc(time):
    jogos_time = temporadas[
        temporadas['Mandante'] == time
    ].copy()

    jogos_time = jogos_time.sort_values(
        by=['Data', 'Hora'], ascending=[False, False]
    ).head(10)

    total_jogos = len(jogos_time)
    if total_jogos == 0:
        return None

    gols_1t = jogos_time['GM1T'].sum()

    return gols_1t / total_jogos

def calcular_gshtf(time):
    jogos_time = temporadas[
        temporadas['Visitante'] == time
    ].copy()

    jogos_time = jogos_time.sort_values(
        by=['Data', 'Hora'], ascending=[False, False]
    ).head(10)

    total_jogos = len(jogos_time)
    if total_jogos == 0:
        return None

    gols_1t = jogos_time['GS1T'].sum()

    return gols_1t / total_jogos

def calcular_gsf(time):
    jogos_time = temporadas[
        temporadas['Visitante'] == time
    ].copy()

    jogos_time = jogos_time.sort_values(
        by=['Data', 'Hora'], ascending=[False, False]
    ).head(10)

    total_jogos = len(jogos_time)
    if total_jogos == 0:
        return None

    gols_sofridos = jogos_time['GM'].sum()

    return gols_sofridos / total_jogos

def dadosfixtures(jogos, TeamsFinal):

    # =========================
    # JOIN MANDANTE
    # =========================
    fixtures = jogos.merge(
        TeamsFinal,
        left_on='Mandante',
        right_on='Time',
        how='left'
    )

    fixtures = fixtures.rename(columns={
        'GM10': 'GM10_H',
        'GS10': 'GS10_H',
        'GMHT10': 'GMHT10_H',
        'GMC': 'GMC_H',
        'GMHTC': 'GMHTC_H',
        'GSF': 'GSF_H',
        'GSHTF': 'GSHTF_H'
    }).drop(columns=['Time'])

    # =========================
    # JOIN VISITANTE
    # =========================
    fixtures = fixtures.merge(
        TeamsFinal[['Time', 'GM10', 'GS10', 'GMC', 'GSF', 'GSHTF']],
        left_on='Visitante',
        right_on='Time',
        how='left'
    )

    fixtures = fixtures.rename(columns={
        'GM10': 'GM10_A',
        'GS10': 'GS10_A',
        'GMC': 'GMC_A',
        'GSF': 'GSF_A',
        'GSHTF': 'GSHTF_A'
    }).drop(columns=['Time'])

    # =========================
    # FULL_FIX
    # =========================
    fixtures['full_fix'] = fixtures['Mandante'] + ' x ' + fixtures['Visitante']

    # =========================
    # SELEÇÃO FINAL
    # =========================
    fixtures = fixtures[
        [
            'Data',
            'Hora',
            'full_fix',

            'Mandante',
            'GM10_H',
            'GS10_H',
            'GMHT10_H',
            'GMC_H',
            'GMHTC_H',

            'Visitante',
            'GM10_A',
            'GS10_A',
            'GMC_A',
            'GSF_A',
            'GSHTF_A'
        ]
    ]

    return fixtures

def baixar_jogos_main(destino_main):
    """
    Baixa os fixtures principais e retorna um DataFrame
    apenas com as colunas:
    Div, Data, Hora, Mandante, Visitante
    """

    page_url = "https://www.football-data.co.uk/matches.php"
    response = requests.get(page_url)

    if response.status_code != 200:
        raise Exception("Erro ao acessar página de Jogos Main")

    soup = BeautifulSoup(response.text, "html.parser")

    # Link correto conforme você validou no HTML
    link = soup.find("a", href=lambda x: x and x.strip() == "fixtures.xlsx")
    if not link:
        raise Exception("Link fixtures.xlsx não encontrado")

    url_download = BASE_SITE + link["href"]

    arquivo = requests.get(url_download)
    if arquivo.status_code != 200:
        raise Exception("Erro ao baixar fixtures.xlsx")

    df = pd.read_excel(arquivo.content)

    df = df[
        ['Div', 'Date', 'Time', 'HomeTeam', 'AwayTeam']
    ].rename(columns={
        'Date': 'Data',
        'Time': 'Hora',
        'HomeTeam': 'Mandante',
        'AwayTeam': 'Visitante'
    })

    df.to_excel(destino_main, index=False)

def baixar_jogos_extra(destino):
    print("🔄 Acessando página de fixtures...")

    response = requests.get(BASE_PAGE)
    if response.status_code != 200:
        print("❌ Erro ao acessar página")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Procura o link correto
    link = soup.find("a", href=lambda x: x and "new_league_fixtures" in x)

    if not link:
        print("❌ Link de fixtures não encontrado")
        return

    href = link["href"]

    # Monta URL completa
    if not href.startswith("http"):
        url_download = BASE_SITE + href
    else:
        url_download = href

    print("⬇️ Baixando:", url_download)

    arquivo = requests.get(url_download)
    if arquivo.status_code != 200:
        print("❌ Erro ao baixar arquivo")
        return

    # Garante diretório
    os.makedirs(os.path.dirname(destino), exist_ok=True)

    # Salva arquivo
    with open(destino, "wb") as f:
        f.write(arquivo.content)

    print("✅ Arquivo baixado com sucesso")

    # Lê e ajusta colunas
    df = pd.read_excel(destino)

    df = df[['Country', 'Date','Time','Home', 'Away']].copy()
    df = df.rename(columns={
        'Country': 'Div',
        'Date':'Data',
        'Time':'Hora',
        'Home': 'Mandante',
        'Away': 'Visitante'
    })

    df.to_excel(destino, index=False)
    print("📊 Arquivo tratado e salvo:", destino)

def baixar_temp_extra(destino_extra):
    """
    Baixa o arquivo All New Data (Extra)
    Salva como TempExtra.xlsx
    """

    page_url = "https://www.football-data.co.uk/all_new_data.php"
    response = requests.get(page_url)

    if response.status_code != 200:
        raise Exception("Erro ao acessar página All New Data")

    soup = BeautifulSoup(response.text, "html.parser")

    link = soup.find("a", href=lambda x: x and "new_leagues_data.xlsx" in x)
    if not link:
        raise Exception("Link new_leagues_data.xlsx não encontrado")

    url_download = BASE_SITE + link["href"]

    arquivo = requests.get(url_download)
    if arquivo.status_code != 200:
        raise Exception("Erro ao baixar new_leagues_data.xlsx")

    destino = os.path.join(destino_extra, "TempExtra.xlsx")

    with open(destino, "wb") as f:
        f.write(arquivo.content)

def baixar_temp_main(destino_jogos_main, qtd_temporadas):
    """
    Baixa os arquivos Main das N temporadas mais recentes
    Salva como TempYYYYYYYY.xlsx
    """

    page_url = "https://www.football-data.co.uk/downloadm.php"
    response = requests.get(page_url)

    if response.status_code != 200:
        raise Exception("Erro ao acessar página downloadm")

    soup = BeautifulSoup(response.text, "html.parser")

    temporadas = temporadas_recentes(qtd_temporadas)

    for ano_ini, ano_fim in temporadas:
        nome_arquivo = f"all-euro-data-{ano_ini}-{ano_fim}.xlsx"

        link = soup.find("a", href=lambda x: x and nome_arquivo in x)
        if not link:
            print(f"Arquivo não encontrado: {nome_arquivo}")
            continue

        url_download = BASE_SITE + link["href"]

        arquivo = requests.get(url_download)
        if arquivo.status_code != 200:
            print(f"Erro ao baixar {nome_arquivo}")
            continue

        nome_saida = f"Temp{ano_ini}{ano_fim}.xlsx"
        destino = os.path.join(destino_jogos_main, nome_saida)

        with open(destino, "wb") as f:
            f.write(arquivo.content)

        print(f"✔ Baixado: {nome_saida}")


####################################### MAIN #######################################

BASE_PAGE = "https://www.football-data.co.uk/matches_new_leagues.php"
BASE_SITE = "https://www.football-data.co.uk/"

destino = r"C:\Users\vinicius.miranda\Desktop\Tips\base\JogosExtra.xlsx"
baixar_jogos_extra(destino)

destino_main = r"C:\Users\vinicius.miranda\Desktop\Tips\base\JogosMain.xlsx"
baixar_jogos_main(destino_main)

destino_jogos_extra = r"C:\Users\vinicius.miranda\Desktop\Tips\base"
baixar_temp_extra(destino_jogos_extra)

destino_jogos_main = r"C:\Users\vinicius.miranda\Desktop\Tips\base"
qtd_temporadas = 3
baixar_temp_main(destino_jogos_main, qtd_temporadas)


################# CRIA DATAFRAME COM OS PROXIMOS JOGOS #################


diretorio = r'C:\Users\vinicius.miranda\Desktop\Tips\base'

arquivos_jogos = glob.glob(os.path.join(diretorio, 'Jogos*.xlsx'))

lista_jogos = []
for arquivo in arquivos_jogos:
    df = pd.read_excel(arquivo)

    df = df[['Div', 'Data', 'Hora', 'Mandante', 'Visitante']]

    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')

    df['Hora'] = (
        df['Hora']
        .astype(str)
        .str.strip()
        .str[:5]
        .replace({'nan': np.nan})
    )

    lista_jogos.append(df)

jogos = pd.concat(lista_jogos, ignore_index=True)
jogos = jogos.sort_values(by=['Data', 'Hora'])


print("Próximos jogos unificados em uma base")



################# CRIA DATAFRAME COM AS TEMPORADAS #################

arquivos_temporadas = glob.glob(os.path.join(diretorio, 'Temp*.xlsx'))


lista_dfs = []

for arquivo in arquivos_temporadas:

    abas = pd.read_excel(arquivo, sheet_name=None)

    for nome_aba, df in abas.items():

        # =========================
        # CASO TEMP EXTRA
        # =========================
        if 'TempExtra' in os.path.basename(arquivo):

            df = df.rename(columns={
                'Country': 'Div',
                'Home': 'HomeTeam',
                'Away': 'AwayTeam',
                'HG': 'FTHG',
                'AG': 'FTAG'
            })

            # Cria colunas inexistentes no Extra
            df['HTHG'] = np.nan
            df['HTAG'] = np.nan

        # =========================
        # SELEÇÃO FINAL PADRÃO
        # =========================
        df = df[
            [
                'Div',
                'Date',
                'Time',
                'HomeTeam',
                'AwayTeam',
                'FTHG',
                'FTAG',
                'HTHG',
                'HTAG'
            ]
        ]

        lista_dfs.append(df)


temporadas = pd.concat(lista_dfs, ignore_index=True)

temporadas = temporadas.rename(columns={
    'Date': 'Data',
    'Time': 'Hora',
    'HomeTeam': 'Mandante',
    'AwayTeam': 'Visitante',
    'FTHG': 'GM',
    'FTAG': 'GS',
    'HTHG': 'GM1T',
    'HTAG': 'GS1T'
})

print("Temporadas unificadas em uma base")


Clubs = pd.concat([
    temporadas['Mandante'],
    temporadas['Visitante']
], ignore_index=True).drop_duplicates().reset_index(drop=True)
Clubs = pd.DataFrame(Clubs, columns=['Time'])


Clubs['GM10'] = Clubs['Time'].apply(calcular_gm10)
Clubs['GS10'] = Clubs['Time'].apply(calcular_gs10)
Clubs['GMHT10'] = Clubs['Time'].apply(calcular_gmht)
Clubs['GSHT10'] = Clubs['Time'].apply(calcular_gsht)
Clubs['GMC'] = Clubs['Time'].apply(calcular_gmc)
Clubs['GMHTC'] = Clubs['Time'].apply(calcular_gmhtc)
Clubs['GSF'] = Clubs['Time'].apply(calcular_gsf)
Clubs['GSHTF'] = Clubs['Time'].apply(calcular_gshtf)


print("Métricas dos clubes calculadas")

# Garante tipos corretos
jogos['Data'] = pd.to_datetime(jogos['Data'])
jogos['Hora'] = pd.to_datetime(jogos['Hora'], format='%H:%M').dt.time

# Cria coluna Data/Hora
jogos['Data/Hora'] = jogos.apply(
    lambda x: pd.Timestamp.combine(x['Data'].date(), x['Hora']),
    axis=1
)


# Reordena colocando Data/Hora como primeira coluna (opcional, mas recomendado)
colunas = ['Data/Hora'] + [c for c in jogos.columns if c != 'Data/Hora']
jogos = jogos[colunas]
jogos['Data/Hora'] = pd.to_datetime(jogos['Data/Hora']) - pd.Timedelta(hours=3)

# Ordena ascendente por Data/Hora
jogos = jogos.sort_values(by='Data/Hora', ascending=True).reset_index(drop=True)

# Remove coluna Div
jogos = jogos.drop(columns=['Div'])
jogos = jogos.drop(columns=['Data'])
jogos = jogos.drop(columns=['Hora'])

clubs = Clubs.set_index('Time')

jogos['Gols'] = (
    clubs.loc[jogos['Mandante'], ['GM10', 'GS10']].sum(axis=1).values +
    clubs.loc[jogos['Visitante'], ['GM10', 'GS10']].sum(axis=1).values
) / 4

jogos['Gols_Aj'] = (
    clubs.loc[jogos['Mandante'], 'GMC'].values +
    clubs.loc[jogos['Visitante'], 'GSF'].values
) / 2

jogos['Gols_HT'] = (
    clubs.loc[jogos['Mandante'], ['GMHT10', 'GSHT10']].sum(axis=1).values +
    clubs.loc[jogos['Visitante'], ['GMHT10', 'GSHT10']].sum(axis=1).values
) / 4

jogos['Gols_HT_AJ'] = (
    clubs.loc[jogos['Mandante'], 'GMHTC'].values +
    clubs.loc[jogos['Visitante'], 'GSHTF'].values
) / 2

agora = pd.Timestamp.now()

jogos = jogos[jogos['Data/Hora'] > agora]


jogos.to_excel(
    r'C:\Users\vinicius.miranda\Desktop\Tips\base\TIPS.xlsx',
    index=False
)

Clubs.to_excel(
    r'C:\Users\vinicius.miranda\Desktop\Tips\base\Times.xlsx',
    index=False
)

print("Arquivo TIPS.xlsx criado com sucesso!")


for _, linha in jogos.iterrows():

    gols_ht = linha['Gols_HT_AJ']

    # Ignora nulos
    if pd.isna(gols_ht):
        continue

    # Só envia se >= 0.60
    if gols_ht < 0.60:
        continue

    # Formata hora hh:mm
    hora_formatada = pd.to_datetime(linha['Data/Hora']).strftime('%H:%M')
    dia_formatado = pd.to_datetime(linha['Data/Hora']).strftime('%d/%m')

    # =========================
    # DEFINE MENSAGEM
    # =========================
    if 0.60 <= gols_ht < 0.90:
        msg = f"""
⚽ *Próximo jogo*

🗓️{dia_formatado}
🕒{hora_formatada}

{linha['Mandante']} x {linha['Visitante']}
Gols HT: Acima de 0.5
"""

    elif gols_ht >= 0.90:
        msg = f"""
⚽ *Próximo jogo*

🗓️{dia_formatado}
🕒{hora_formatada}
{linha['Mandante']} x {linha['Visitante']}
Gols HT: Acima de 1 (Handicap Asiático)
"""

    else:
        continue

    # =========================
    # ENVIA TELEGRAM
    # =========================
    enviar_telegram(msg)
