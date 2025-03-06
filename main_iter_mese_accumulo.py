import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly_express as px


st.set_page_config(layout='wide')
st.title('RCCP Lavorazioni Meccaniche')
#st.subheader(':red[Input dati]', divider='red')

mask_non_prod = [
  "Mese",
  "Linea",
  "Modello",
  "Fase",
  "Macchina assegnata",
  "volumi",
  "tempo_ciclo",
  "CI",
  "volumi_pezzi",
  "moving_type",
  "sat_dopo",
  "qty_res [motori]",
  "Stock_fine_periodo",
  "Obiettivo_accumulo_adj"
]


semestre = st.sidebar.radio('Selezionare il semestre', options=['S1','S2'])
if semestre == 'S1':
    mesi = ['GEN','FEB','MAR','APR','MAG','GIU','LUG']
else:
    mesi = ['AGO','SETT','OTT','NOV','DIC']


line = st.sidebar.radio('Selezionare linea', options=['AD','AM'])

path = st.sidebar.file_uploader('Caricare il file')
if not path:
    st.stop()

df = pd.read_excel(path)
df = df[df.columns[0:15]]
df = df.drop(columns=['I°sem','II°sem'])
# eliminazione prima riga
df = df[1:]
to_keep = [df.columns[0]] + mesi
df = df[to_keep]
#df = df[df.columns[0:8]]


flat_path = st.sidebar.file_uploader('Caricare il file statico')
if not flat_path:
    st.stop()
flat = pd.read_excel(flat_path)
calendario = pd.read_excel(flat_path, sheet_name='OEE-calendario')
accumulo = pd.read_excel(flat_path, sheet_name='Accumulo')
contolavoro = pd.read_excel(flat_path, sheet_name='Contolavoro')
contolavoro['Codice'] = [codice.replace(' ','') for codice in contolavoro.Codice]
contolavoro['key'] = contolavoro['Mese']+'-'+contolavoro['Linea']+'-'+contolavoro['Codice']


st.divider()
st.subheader('Contolavoro')
contolavoro

accumulo['Modello'] = [stringa.replace(' ','',) for stringa in accumulo.Modello]
accumulo['linea'] = np.where(accumulo.Tipo == 'Albero', 'AM', 'AD')
accumulo['key'] = accumulo['linea']+'-'+accumulo['Modello']
flat = flat.melt(id_vars=['Mese','Linea','Codice','Fase','Macchina standard','Op'])
flat['Codice'] = [stringa.replace(' ','') for stringa in flat.Codice]
flat_alt = flat[flat['Macchina standard'] != flat['variable']]
flat = flat[flat['Macchina standard'] == flat['variable']]

flat_alt = flat_alt[flat_alt['value'] != 0]
#flat_alt['key'] = flat_alt['Mese']+'-'+flat_alt['Linea']+'-'+flat_alt['Codice']+'-'+flat_alt['Macchina standard']
flat_alt['key'] = flat_alt['Mese']+'-'+flat_alt['Linea']+'-'+flat_alt['Codice']+'-'+flat_alt['Macchina standard']+'-'+flat_alt['Op'].astype(str)

dic_alt = dict(zip(flat_alt.key.unique(), [None for i in range(len(flat_alt.key.unique()))]))
for chiave in dic_alt.keys():
    macchine = list(flat_alt[flat_alt.key == chiave]['variable'])
    tempi = list(flat_alt[flat_alt.key == chiave]['value'])
    alternative = [(macchine[i],tempi[i]) for i in range(len(macchine))]
    dic_alt[chiave]=alternative

bom = pd.read_excel(flat_path, sheet_name='BOM')
bom['Albero'] = [stringa.replace(' ','') for stringa in bom.Albero.astype(str)]
bom['Albero_camme'] = [stringa.replace(' ','') for stringa in bom.Albero_camme.astype(str)]
# CARICAMENTO DATI PERDITE E CADENZE

cad = pd.read_excel(path, sheet_name='PERDITE E CADENZE ')
lista_test = list(cad['Unnamed: 0'].astype(str))
lista_test = [stringa[:3] for stringa in lista_test]
riga_inizio = lista_test.index('Imb') # nel ppp al foglio perdite e cadenze ci deve essere solo una voce Imbiellaggi nella prima colonna

cad = cad[riga_inizio:]
cad = cad[cad.columns[:18]]
cad['Unnamed: 0'] = cad['Unnamed: 0'].ffill()

righe_filtro=[
                "Imbiellaggi MON - MTS - HYM 950 - SS - DSX",
                "Imbiellaggi MSV4 - DVLV4 - PAN7G",
                "Imbiellaggi hym 698",
                "Imbiellaggi Cross",
                "Imbiellaggi Pan V2 + SF V2",
                "Alberi Mts V4 Bra",
                "Alberi Mts 960 +  Mon + DSX",
                "Alberi Dvl + Xdvl Bra",
                "Alberi Pan - Sf V4 Bra",
                "Alberi Scr 800 Bra ",
                "Alberi Hym 698 Bra",
                "Alberi Motore Scr 800  dmh + dmt + Argentina",
                "Alberi Motore 896  dmh + dmt + dafra + VWA",
                "Sc800 DK",
                "Sc800 Icon",
                "SCR Full Throttle 2G",
                "SCR Nightshift 2G",
                "DSX",
                "MTSV2",
                "MTSV2 S",
                "MTS 896",
                "MTS 896 S"
]

cad = cad[[any(key in check for key in righe_filtro) for check in cad['PPP 2025 esp 013'].astype(str)]]
cad = cad.drop(columns = ['Unnamed: 2','1° sem','2°sem','anno'])
cad = cad.rename(columns={'Unnamed: 0': 'Gruppo', 'PPP 2025 esp 013':'Modello'})
cad = cad.fillna(0)
cad = cad[cad.columns[0:9]]

# OEE
oee = pd.read_excel(flat_path, sheet_name='OEE')

df = df[5:] # elimino la parte di pianificazione
df = df[df[df.columns[0]].astype(str) != 'nan']

esclusioni = ['Produz', 'Preserie','Progressivo','gg']
df = df[[all(escluso not in test for escluso in esclusioni) for test in df[df.columns[0]].astype(str)]]
#df = df[[all(escluso not in test for escluso in esclusioni) for test in df['PPP 2025 esp 013'].astype(str)]]
df = df.reset_index(drop=True)
df=df.rename(columns={df.columns[0]:'Modello'})
df = df[:-5]
df.loc[len(df)-1] = df.iloc[-1]
df.iloc[-1] = 0
df.Modello.iloc[-1] = 'Dummy'

df = df.fillna(0)

#filtro per 896 - scr
df = df[['SCR' not in check for check in df.Modello.astype(str)]]
df = df[['896' not in check for check in df.Modello.astype(str)]]

df['Gruppo']='PPP_Veicoli'

df_tot = pd.concat([df, cad])

#rename SETT column to SET

df_tot = df_tot.rename(columns={'SETT':'SET'})

df_tot = df_tot.merge(bom, how='left', left_on='Modello', right_on='Modello')
df_tot = df_tot[df_tot.Nota.astype(str) != 'in phase out, non lo consideriamo']

fabbisogno_aggregato_alberi = df_tot.copy()
fabbisogno_aggregato_camme = df_tot.copy()
fabbisogno_aggregato_calberi = df_tot.copy()

fabbisogno_aggregato_alberi = fabbisogno_aggregato_alberi.drop(columns=['Modello','Gruppo','Nota','Albero_camme','Contralberi','CI [2 | 4]'])
fabbisogno_aggregato_alberi = fabbisogno_aggregato_alberi.groupby(by='Albero', as_index=False).sum()
fabbisogno_aggregato_alberi = fabbisogno_aggregato_alberi.rename(columns={'Albero':'Modello'})
fabbisogno_aggregato_alberi['CI']=1
fabbisogno_aggregato_alberi['Linea']='AM'

fabbisogno_aggregato_camme = fabbisogno_aggregato_camme.drop(columns=['Modello','Gruppo','Nota','Albero','Contralberi'])
fabbisogno_aggregato_camme = fabbisogno_aggregato_camme.groupby(by=['Albero_camme','CI [2 | 4]'], as_index=False).sum()
fabbisogno_aggregato_camme = fabbisogno_aggregato_camme.rename(columns={'CI [2 | 4]':'CI', 'Albero_camme':'Modello'})
fabbisogno_aggregato_camme['Linea']='AD'

fabbisogno_aggregato_calberi = fabbisogno_aggregato_calberi.drop(columns=['Modello','Gruppo','Nota','Albero_camme', 'Albero','CI [2 | 4]'])
fabbisogno_aggregato_calberi = fabbisogno_aggregato_calberi.groupby(by='Contralberi', as_index=False).sum()
fabbisogno_aggregato_calberi = fabbisogno_aggregato_calberi.rename(columns={'Contralberi':'Modello'})
fabbisogno_aggregato_calberi['CI']=2
fabbisogno_aggregato_calberi['Linea']='AD'


fabbisogno = pd.concat([fabbisogno_aggregato_alberi,fabbisogno_aggregato_camme, fabbisogno_aggregato_calberi])
fabbisogno = fabbisogno[fabbisogno.Modello.astype(str) != '0']
fabbisogno = fabbisogno[fabbisogno.Linea == line]

flat['key'] = flat['Mese']+'-' + flat['Linea']+'-'+flat['Codice']
fabbisogno_melt= fabbisogno.melt(id_vars=['Modello','Linea','CI'])

fabbisogno_melt = fabbisogno_melt.rename(columns={'variable':'mese', 'value':'volumi'})
fabbisogno_melt['key']=fabbisogno_melt['mese']+'-'+fabbisogno_melt['Linea']+'-'+fabbisogno_melt['Modello'].astype(str)
fabbisogno_melt = fabbisogno_melt.merge(flat, how='left', left_on='key', right_on='key')

#flat

fabbisogno_melt = fabbisogno_melt[fabbisogno_melt.Codice.astype(str)!='nan']
fabbisogno_melt = fabbisogno_melt.merge(contolavoro[['key','Quantità']], how='left', left_on='key', right_on='key')
fabbisogno_melt['Quantità'] = fabbisogno_melt['Quantità'].fillna(0)
fabbisogno_melt = fabbisogno_melt.rename(columns={'volumi':'volumi_ppp'})
fabbisogno_melt['volumi'] = fabbisogno_melt['volumi_ppp'] - fabbisogno_melt['Quantità']
fabbisogno_melt['volumi_pezzi'] = fabbisogno_melt['volumi'] * fabbisogno_melt['CI']
fabbisogno_melt['wl'] = fabbisogno_melt['volumi_pezzi']*fabbisogno_melt.value / 60

fabbisogno_melt['key_alt'] = fabbisogno_melt['key']+'-'+fabbisogno_melt['Macchina standard']+'-'+fabbisogno_melt['Op']
fabbisogno_melt['alternative']=None


for i in range(len(fabbisogno_melt)):
    key = fabbisogno_melt['key_alt'].iloc[i]
    try:
        fabbisogno_melt['alternative'].iloc[i]=dic_alt[key]
    except:
        fabbisogno_melt['alternative'].iloc[i]=None


fabbisogno_melt = fabbisogno_melt.drop(columns=['Linea_y','variable','mese','Codice'])
fabbisogno_melt = fabbisogno_melt.rename(columns={'Linea_x':'Linea','value':'tempo_ciclo'})
fabbisogno_melt = fabbisogno_melt[['Mese','Linea','Modello','Fase','Macchina standard','volumi','tempo_ciclo','wl','alternative','key','key_alt','CI','volumi_pezzi']]

workload = fabbisogno_melt[['Mese','Fase','Macchina standard','wl']].groupby(by=['Mese','Fase','Macchina standard'], as_index=False).sum()
#workload

#presenti = list(workload['Macchina standard'].unique())
#presenti

workload = workload.merge(oee, how='left', left_on='Macchina standard', right_on='Macchina')

workload['Mese'] = pd.Categorical(workload['Mese'], categories=mesi)

workload = workload.sort_values(by='Mese')

for i in range(1,len(calendario)):
    for mese in mesi:
        lordo = calendario[mese].iloc[0]
        non_pian = calendario[mese].iloc[i]
        calendario[mese].iloc[i] = lordo - non_pian
calendario = calendario[1:]

calendario_melt = calendario.melt(id_vars=['Linea','Macchina','OEE'])
calendario_melt['ore_disp_lorde'] = calendario_melt['value'] * 7.5 * 3 
calendario_melt['ore_disp'] = calendario_melt['ore_disp_lorde'] * calendario_melt['OEE']
calendario_melt['key'] = calendario_melt['Macchina'] + '-'+ calendario_melt['variable']
calendario_melt = calendario_melt[['key','ore_disp']]

workload['key'] = workload['Macchina']+'-'+workload['Mese'].astype(str)
workload = workload.merge(calendario_melt, how='left', left_on='key',right_on='key')
workload['saturazione'] = workload['wl']/workload['ore_disp']
#workload['delta_ore'] = np.where(workload.wl > workload.ore_disp,workload.wl - workload.ore_disp,0 )
workload['delta_ore'] = workload.wl - workload.ore_disp

wl_critiche = workload[['key','delta_ore']]
wl_critiche = wl_critiche.rename(columns={'key':'key_critical'})

fabbisogno_melt['key_critical'] = fabbisogno_melt['Macchina standard']+'-'+fabbisogno_melt['Mese']
fabbisogno_melt = fabbisogno_melt.merge(wl_critiche, how='left', left_on='key_critical', right_on='key_critical')
fabbisogno_melt['delta_volume'] = fabbisogno_melt['delta_ore'] / (fabbisogno_melt['tempo_ciclo']/60)
fabbisogno_melt['moving_type'] = np.where(fabbisogno_melt['delta_volume']>fabbisogno_melt['volumi_pezzi'], 'totale','parziale')
fabbisogno_melt['moving_type'] = np.where(fabbisogno_melt['delta_volume']<0, 'no_moving', fabbisogno_melt['moving_type'])
fabbisogno_melt['delta_volume'] = np.where(fabbisogno_melt['delta_volume']>=0,fabbisogno_melt['delta_volume'],0)

fabbisogno_melt['moving_type'] = np.where(fabbisogno_melt['alternative'].astype(str)=='None', 'no_moving',fabbisogno_melt['moving_type'] )
fabbisogno_melt['delta_volume'] = np.where(fabbisogno_melt.moving_type=='totale',fabbisogno_melt.volumi_pezzi, fabbisogno_melt.delta_volume) #il to_move corisponde a tutti i pezzi

# FINE IMPORTAZIONE DEI DATI ===============================================

if line == 'AD':
    macchine = [
  "1A_AD",
  "1B_AD",
  "STAMA 1",
  "STAMA 2",
  "STAMA 3",
  "STAMA 5",
  "LICON",
  "STAMA 4/4 BIS",
  "Milltap",
  "3A_AD",
  "3B_AD",
  "Jucam",
  "Jucam 2",
  "Proflex 11129",
  "Proflex 11999",
  "Proflex 13426",
  "Proflex 10720"
]
else:
     macchine = [
  "Graziano",
  "Tacchella 1",
  "Tacchella 2",
  "Jucrank 3",
  "Jucrank 1-2",
  "Marus",
  "3B_AM",
  "3A_AM",
  "2B_AM",
  "2A_AM",
  "1_AM",
  "Tacchella 3"
]


presenti = list(workload['Macchina standard'].unique())
non_presenti = list(set(macchine) - set(presenti))

workload_elaborato = workload.copy()


def livella_macchine(workload,mesi):
    lista_assegnati = []
    for mese in mesi:

        workload_graph = workload[workload['Mese']==mese]
        fab_print = fabbisogno_melt[fabbisogno_melt.Mese == mese]
        fab_print = fab_print.drop(columns='alternative')

        # Ottimizzazione

        #lista_assegnati = []
        for fase in fab_print.Fase.unique():

            db_assegnato = fab_print[(fab_print.moving_type == 'no_moving') & (fab_print.Fase == fase)]
            db_assegnato['Macchina assegnata'] = db_assegnato['Macchina standard']
            #st.write(db_assegnato)

            def new_row(df):
                df = df.reset_index(drop=True)
                df.loc[len(df)] = df.iloc[-1]
                return df

            to_split = fabbisogno_melt[fabbisogno_melt.Mese == mese]
            to_split = to_split.drop(columns='alternative')
            #to_split = to_split[(to_split.moving_type == 'parziale') & (to_split.Fase == fase)].reset_index(drop=True)
            to_split = to_split[(to_split.moving_type != 'no_moving') & (to_split.Fase == fase)].reset_index(drop=True)
            #to_split = to_split[to_split.Fase == fase].reset_index(drop=True)

            # dizionario di saturazione di partenza, che viene aggiornato via via che si assegnano volumi
            dic_sat = dict(zip(workload_graph['Macchina standard'], workload_graph['delta_ore']))
            
            #if 'Tacchella 2' not in dic_sat.keys():
                #dic_sat['Tacchella 2']=400
            #st.write(dic_sat)

            for i in range(len(to_split)):
                wl_start = to_split['wl'].iloc[i]
                key_alt = to_split.key_alt.iloc[i]
                try:
                    alternative = dic_alt[key_alt]
                except:
                    alternative = []
                pcs_to_move = to_split.delta_volume.iloc[i]
                modello = to_split.Modello.iloc[i]
                mac_std = to_split['Macchina standard'].iloc[i]
                ci = to_split.CI.iloc[i]
                tot_moved = 0
                #st.write('Modello',modello)
                #st.write('--Pezzi da spostare: ', pcs_to_move)

                for elemento in alternative:
                    #st.write(f'---Sto provando {elemento[0]}')
                    mac_alt = elemento[0]
                    tc_alt = elemento[1]
                    ore_disponibili = - dic_sat[mac_alt]
                    #if (mese=='GEN') & (fase=='rettifica'):
                    #    st.write(f'macchina {mac_alt} ore disp:{ore_disponibili}')

                    if ore_disponibili > 0:
                        max_pcs = ore_disponibili * 60 / tc_alt
                        #st.write(f'----Ore disponibili: {ore_disponibili}')
                        #st.write(f'-----Max pcs: {max_pcs}')
                        if max_pcs < pcs_to_move:
                            #st.write('------Capienza non sufficiente, ne prendo il massimo')
                            moved = max_pcs
                            tot_moved += moved
                            #st.write(f'--------ne ho spostati {moved}')
                            pcs_to_move -= max_pcs
                            motori = moved/ci
                            wl_new = tc_alt * moved / 60
                            dic_sat[mac_alt] = - ore_disponibili + wl_new

                            db_assegnato = new_row(db_assegnato)
                            db_assegnato['Modello'].iloc[-1] = modello
                            db_assegnato['Macchina standard'].iloc[-1] = mac_std
                            db_assegnato['Macchina assegnata'].iloc[-1] = mac_alt
                            db_assegnato['volumi'].iloc[-1] = motori
                            db_assegnato['tempo_ciclo'].iloc[-1] = tc_alt
                            db_assegnato['wl'].iloc[-1] = wl_new
                            db_assegnato['CI'].iloc[-1] = ci
                            db_assegnato['volumi_pezzi'].iloc[-1] = moved
                            db_assegnato['moving_type'].iloc[-1] = 'moved'

                            if(alternative.index(elemento) == len(alternative)-1): #se è l'ultima alternativa poi creo la riga con il residuo sulla macchina di partenza
                                db_assegnato.loc[len(db_assegnato)] = to_split.iloc[i]
                                db_assegnato['volumi_pezzi'].iloc[-1] = db_assegnato['volumi_pezzi'].iloc[-1] - moved# db_assegnato['delta_volume'].iloc[-1]
                                db_assegnato['volumi'].iloc[-1] = db_assegnato['volumi_pezzi'].iloc[-1] / db_assegnato['CI'].iloc[-1]
                                db_assegnato['Macchina assegnata'].iloc[-1] = mac_std
                                try:
                                    db_assegnato['wl'].iloc[-1] = db_assegnato['volumi_pezzi'].iloc[-1] * db_assegnato['tempo_ciclo'].iloc[-1] / 60# wl_start - wl_new
                                    db_assegnato['moving_type'].iloc[-1] = 'iniziale_tipo1'
                                except:
                                    st.write('1')
                                    st.stop()

                        else:
                            moved = pcs_to_move
                            tot_moved += moved
                            pcs_to_move = 0
                            motori = moved/ci
                            wl_new = tc_alt * moved / 60
                            dic_sat[mac_alt] = - ore_disponibili + wl_new

                            db_assegnato = new_row(db_assegnato)
                            db_assegnato['Modello'].iloc[-1] = modello
                            db_assegnato['Macchina standard'].iloc[-1] = mac_std
                            db_assegnato['Macchina assegnata'].iloc[-1] = mac_alt
                            db_assegnato['volumi'].iloc[-1] = motori
                            db_assegnato['tempo_ciclo'].iloc[-1] = tc_alt
                            db_assegnato['wl'].iloc[-1] = wl_new
                            db_assegnato['CI'].iloc[-1] = ci
                            db_assegnato['volumi_pezzi'].iloc[-1] = moved
                            db_assegnato['moving_type'].iloc[-1] = 'moved'

                            db_assegnato.loc[len(db_assegnato)] = to_split.iloc[i]
                            db_assegnato['volumi_pezzi'].iloc[-1] = db_assegnato['volumi_pezzi'].iloc[-1] - db_assegnato['delta_volume'].iloc[-1]
                            db_assegnato['volumi'].iloc[-1] = db_assegnato['volumi_pezzi'].iloc[-1] / db_assegnato['CI'].iloc[-1]
                            db_assegnato['Macchina assegnata'].iloc[-1] = mac_std

                            try:
                                db_assegnato['wl'].iloc[-1] = db_assegnato['volumi_pezzi'].iloc[-1] * db_assegnato['tempo_ciclo'].iloc[-1] / 60
                                db_assegnato['moving_type'].iloc[-1] = 'iniziale_tipo2'
                            except:
                                st.stop()


                            break
                    
                    else:
                        if(alternative.index(elemento) == len(alternative)-1): #se è l'ultima alternativa e non posso spostare niente
                            # devo tenere conto di quello che ho spostato nelle alternative precedenti, in modo da mantenere solo il numero di pezzi residuo
                            db_assegnato.loc[len(db_assegnato)] = to_split.iloc[i]
                            db_assegnato['volumi_pezzi'].iloc[-1] = db_assegnato['volumi_pezzi'].iloc[-1] - tot_moved# - db_assegnato['delta_volume'].iloc[-1]
                            db_assegnato['volumi'].iloc[-1] = db_assegnato['volumi_pezzi'].iloc[-1] / db_assegnato['CI'].iloc[-1]
                            db_assegnato['Macchina assegnata'].iloc[-1] = mac_std

                            try:
                                db_assegnato['wl'].iloc[-1] = db_assegnato['volumi_pezzi'].iloc[-1] * db_assegnato['tempo_ciclo'].iloc[-1] / 60
                                db_assegnato['moving_type'].iloc[-1] = 'iniziale_tipo3'

                            except:
                                db_assegnato['wl'].iloc[-1] = wl_start
                                db_assegnato['moving_type'].iloc[-1] = 'iniziale_tipo4'

                        # assegno i pezzi al df:
                        # devo assegnare una riga con i pezzi mossi sulla macch
            #db_assegnato['mese'] = mese
            lista_assegnati.append(db_assegnato)
            #workload_elaborato = pd.concat([workload_elaborato,workload_graph])


    db_assegnato = pd.concat(lista_assegnati)
    return db_assegnato

# ottimizzazione accumulo============================================

db_assegnato = livella_macchine(workload, mesi)


# da qui in poi serve solo per visualizzare==========================
#'fabbisogno melt'
#st.write(fabbisogno_melt[(fabbisogno_melt.Mese =='GEN') & (fabbisogno_melt.Fase=='rettifica')])


workload_graph = workload_elaborato
workload_graph['Macchina standard'] = pd.Categorical(workload_graph['Macchina standard'], categories=macchine)

cols_ass=[
  "Mese",
  "Linea",
  "Modello",
  "Fase",
  "Macchina assegnata",
  "volumi",
  "tempo_ciclo",
  "wl",
  "CI",
  "volumi_pezzi",
  "moving_type",
  "Macchina standard",
  'key',
  'key_alt'
]
cols_dupl = [
  "Mese",
  "Linea",
  "Modello",
  "Fase",
  "Macchina assegnata",
  "volumi",
  "tempo_ciclo",
  "CI",
  "volumi_pezzi",
  "moving_type",
  "Macchina standard",
  'key'
]

db_assegnato = db_assegnato[cols_ass]
db_assegnato = db_assegnato.drop_duplicates(subset=cols_dupl) # ho tolto le righe di partenza assegnate più volte (quando le macchine alternative sono già piene)
db_assegnato['key'] = db_assegnato['Macchina assegnata']+'-'+db_assegnato['Mese']
#st.write(db_assegnato)
assegnato_aggr = db_assegnato[['key','wl']].groupby(by='key', as_index=False).sum()
assegnato_aggr = assegnato_aggr.rename(columns={'wl':'wl_dopo_split'})
#assegnato_aggr
workload_graph = workload_graph.merge(assegnato_aggr, how='left', left_on='key',right_on='key')
workload_graph['sat_dopo'] = workload_graph['wl_dopo_split'] / workload_graph['ore_disp']

#'db_assegnato'
#st.write(db_assegnato[(db_assegnato.Mese=='GEN') & (db_assegnato.Fase=='rettifica')])
#st.write(workload_graph[(workload_graph.Mese =='GEN') & (workload_graph.Fase == 'rettifica')])
#workload_graph = workload_graph[workload_graph.Fase == fase]
#st.write(workload_graph)

#after = px.bar(workload_graph, x='Macchina standard', y= 'sat_dopo', color='Fase')


workload_graph = workload_graph.sort_values(by=['Mese','Macchina standard'])
st.divider()
st.subheader('Situazione saturazione AS-IS')
asis = px.bar(workload_graph, x='Mese', y= 'saturazione', color='Macchina standard', barmode='group')
asis.add_hline(y=1, line_color='red', line_dash='dash')
st.plotly_chart(asis,use_container_width=True)

st.subheader('Situazione saturazione dopo ottimizzazione')
after = px.bar(workload_graph, x='Mese', y= 'sat_dopo', color='Macchina standard', barmode='group')
after.add_hline(y=1, line_color='red', line_dash='dash')
st.plotly_chart(after,use_container_width=True)


#st.stop()

critiche = list(workload_graph[workload_graph.sat_dopo > 1.01]['key'].unique())
cod_crit = db_assegnato[[any(mac in check for mac in critiche) for check in db_assegnato['key'].astype(str)]]

st.subheader('Situazioni non risolte')
#st.dataframe(cod_crit, use_container_width=True)

#st.dataframe(workload_graph)

cod_crit['moving_type'] = np.where((cod_crit.wl > 400) & (cod_crit.moving_type == 'no_moving'), 'no_moving_iniziale', cod_crit.moving_type)
non_prodotto = cod_crit[['iniziale' in tipo for tipo in cod_crit.moving_type]]


non_prodotto = non_prodotto.merge(workload_graph[['key','sat_dopo','ore_disp']], how='left', left_on='key', right_on='key')
non_prodotto['qty_res [motori]'] = (non_prodotto['sat_dopo']-1) * non_prodotto['ore_disp'] * 60 / non_prodotto['tempo_ciclo'] / non_prodotto.CI
non_prodotto['key_accumulo'] = non_prodotto['Linea']+'-'+non_prodotto['Modello']
non_prodotto = non_prodotto.merge(accumulo[['key','Stock_fine_periodo','Obiettivo_accumulo_adj']], how='left', left_on='key_accumulo', right_on='key')
st.dataframe(non_prodotto[mask_non_prod])


st.divider()
st.subheader('Drill down mese')

selected_month = st.selectbox('Selezionare mese', options=mesi)

workload_graph = workload_graph[workload_graph.Mese == selected_month]
preview = px.bar(workload_graph, x='Macchina standard', y= 'sat_dopo', color='Fase')
preview.add_hline(y=1, line_color='red', line_dash='dash')
st.plotly_chart(preview,use_container_width=True)


fab_print = fabbisogno_melt[fabbisogno_melt.Mese == selected_month]
fab_print = fab_print.drop(columns='alternative')

st.divider()
st.subheader('Drill down fase')

fase_select = st.selectbox('Selezionare fase', options = fab_print.Fase.unique())
workload_graph = workload_graph[workload_graph.Fase == fase_select]


test = go.Figure()
test.add_trace(
    go.Bar(
        x=workload_graph['Macchina'],
        y=workload_graph['saturazione'],
        marker_color = 'pink'
    )
)
test.add_hline(y=1, line_color='red', line_dash='dash')
test.update_layout(
    yaxis=dict(
        range=[0,2.6]
    )
)

test2 = go.Figure()
test2.add_trace(
    go.Bar(
        x=workload_graph['Macchina'],
        y=workload_graph['sat_dopo'],
    )
)
test2.add_hline(y=1, line_color='red', line_dash='dash')
test2.update_layout(
    yaxis=dict(
        range=[0,2.6]
    )
)

sxout, dxout = st.columns([1,1])

with sxout:
    
    st.subheader('Prima')
    st.plotly_chart(test, use_container_width=True)
    st.write('Dettaglio assegnazione di partenza')
    #assegnati_prima = fabbisogno_melt.drop(columns='alternative')
    st.dataframe(fabbisogno_melt[(fabbisogno_melt.Fase == fase_select) & (fabbisogno_melt.Mese == selected_month)][['Macchina standard','Modello','volumi','tempo_ciclo','wl','alternative']], use_container_width=True)
    #if st.toggle('Visualizza alternative'):
     #   for key in cod_crit[cod_crit.Fase == fase_select].key_alt.unique():
      #      st.write(key)
       #     try:
        #        st.write(dic_alt[key])
         #       st.write('---')
          #  except:
           #     st.write('----nessuna alternativa')

with dxout:
    st.subheader('Dopo')
    st.plotly_chart(test2, use_container_width=True)
    st.write('Dettaglio assegnazione dopo ottimizzazione')
    st.dataframe(db_assegnato[(db_assegnato.Fase==fase_select)&(db_assegnato.Mese == selected_month)][['Macchina assegnata','Modello','volumi','tempo_ciclo','wl']],use_container_width=True)
    moving = db_assegnato[db_assegnato.moving_type == 'moved']
    moving = moving[moving.Mese==selected_month]
    moving = moving.rename(columns={'Macchina standard':'Da macchina','Macchina assegnata':'A macchina', 'volumi':'motori_eq' })
    moving = moving[['Fase','Modello','volumi_pezzi','motori_eq','Da macchina','A macchina']]
    st.write('Riassegnazioni effettuate')
    st.dataframe(moving[moving.Fase==fase_select], use_container_width=True)
    #st.dataframe(db_assegnato)






