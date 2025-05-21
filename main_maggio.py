import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly_express as px
from io import BytesIO

st.set_page_config(layout='wide')
st.title('RCCP Lavorazioni Meccaniche')
#st.subheader(':red[Input dati]', divider='red')

def scarica_excel(df, filename):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()

    st.download_button(
        label="Download Excel workbook",
        data=output.getvalue(),
        file_name=filename,
        mime="application/vnd.ms-excel"
    )


mask_non_prod = [
  "Mese",
  #"Linea",
  "Modello",
  #"Fase",
  "Macchina assegnata",
  "volumi",
  #"tempo_ciclo",
  #"CI",
  #"volumi_pezzi",
  #"moving_type",
  #"sat_dopo",
  "qty_res [motori]",
  #"Stock_fine_periodo",
  #"Obiettivo_accumulo_adj"
]

mesi_old = ['GEN','FEB','MAR','APR','MAG','GIU','LUG','AGO','SETT','OTT','NOV','DIC']
mesi = ['GEN','FEB','MAR','APR','MAG','GIU','LUG','AGO','SET','OTT','NOV','DIC']

line = st.sidebar.radio('Selezionare linea', options=['AD','AM'])

path = st.sidebar.file_uploader('Caricare il file')
if not path:
    st.stop()

df = pd.read_excel(path)
df = df.rename(columns={'SETT':'SET'})
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
calendario = calendario.rename(columns={'SETT':'SET'})
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

#cad = cad[[any(key in check for key in righe_filtro) for check in cad['PPP 2025 esp 013'].astype(str)]]
cad = cad[[any(key in check for key in righe_filtro) for check in cad[cad.columns[1]].astype(str)]]
cad = cad.drop(columns = ['Unnamed: 2','1° sem','2°sem','anno'])
#cad = cad.rename(columns={'Unnamed: 0': 'Gruppo', 'PPP 2025 esp 013':'Modello'})
cad = cad.rename(columns={'Unnamed: 0': 'Gruppo', cad.columns[1]:'Modello', 'SETT':'SET'})
cad = cad.fillna(0)
cad = cad[cad.columns[0:14]]
#cad
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

coperture = fabbisogno_melt.copy()

fabbisogno_melt = fabbisogno_melt.rename(columns={'variable':'mese', 'value':'volumi'})
fabbisogno_melt['key']=fabbisogno_melt['mese']+'-'+fabbisogno_melt['Linea']+'-'+fabbisogno_melt['Modello'].astype(str)

# carico qui la tabella delle variazioni

var = pd.read_excel(flat_path, sheet_name = 'Variazioni')
if 'utilizzo' not in st.session_state:
    st.session_state.utilizzo = var



# dopo aver elaborato fabbisogno melt metto questo punto di interruzione, così se faccio operazioni manuali riparte da qui (utilizzo manuale accumulo what-if)
#if 'fab_melt' not in st.session_state:
#    st.session_state.fab_melt = fabbisogno_melt.copy()


# test: tengo in cache solo le variazioni (fab_change)
# qui ogni volta ricalcola con fab_change, devo sottrarre le quantità di fab_change

# utilizzo va inizializzato come session state


for i in range(len(st.session_state.utilizzo)):
        fabb_change = fabbisogno_melt.copy()
        util = st.session_state.utilizzo.Var.iloc[i]
        #st.write(util)
        mese = st.session_state.utilizzo.Mese.iloc[i]
        modello = st.session_state.utilizzo.Modello.iloc[i]

        for j in range(len(fabb_change)):
            asis=fabb_change.volumi.iloc[j]
            if (fabb_change.iloc[j].mese == mese) & (fabb_change.Modello.iloc[j] == modello):
                fabb_change.volumi.iloc[j] = asis + util
        #st.write(fabb_change[(fabb_change.mese == mese) & (fabb_change.Modello == modello)])
        fabbisogno_melt = fabb_change

#


# qui ricalcolo anche lo stock

stock = pd.read_excel(flat_path, sheet_name='Stock')

if line=='AD':
    stock = stock[stock.Tipo=='Albero_camme']
else:
    stock = stock[stock.Tipo!='Albero_camme']

stock.drop(columns=['Tipo','Stock_inizio_periodo'], inplace=True)
stock = stock.melt(id_vars=['Modello'])
obiettivi = stock[stock.variable == 'Obiettivo_fine_periodo']
stock = stock[stock.variable != 'Obiettivo_fine_periodo']
stock = stock.rename(columns={'variable':'Mese'})
stock['Mese'] = pd.Categorical(stock['Mese'], categories=mesi)
stock.sort_values(by=['Modello','Mese'], inplace=True)
stock['Modello'] = [string.replace(' ','') for string in stock.Modello]
stock_change = st.session_state.utilizzo.copy()
stock = stock.merge(stock_change, how='left', left_on=['Modello','Mese'], right_on=['Modello','Mese'])
stock = stock.fillna(0)

# la cumulativa va fatta per modello
cum_var = []
for modello in stock.Modello.unique():
    work = stock[stock.Modello==modello]
    work['cum_sum']=work.Var.cumsum()
    cum_var = cum_var + list(work.cum_sum)
stock['cum_var'] = cum_var
stock['andamento'] = stock['value']+stock['cum_var'] 
#stock.drop(columns=['value', 'Var', 'cum_var'], inplace=True)

#st.session_state.utilizzo
#stock

#fabbisogno_melt = st.session_state.fab_melt.copy()

fabbisogno_melt = fabbisogno_melt.merge(flat, how='left', left_on='key', right_on='key')

#flat

fabbisogno_melt = fabbisogno_melt[fabbisogno_melt.Codice.astype(str)!='nan']
#fabbisogno_melt = fabbisogno_melt.merge(contolavoro[['key','Quantità']], how='left', left_on='key', right_on='key')
#fabbisogno_melt['Quantità'] = fabbisogno_melt['Quantità'].fillna(0)
#fabbisogno_melt = fabbisogno_melt.rename(columns={'volumi':'volumi_ppp'})
# toglie i volumi di contolavoro
#fabbisogno_melt['volumi'] = fabbisogno_melt['volumi_ppp'] - fabbisogno_melt['Quantità']
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

st.subheader('Fabbisogno')

fabbisogno_print = fabbisogno.copy()
excl_comp = ['AA','AP','SA','SP','-O','-V', 'Dummy','Contralb']
fabbisogno_print = fabbisogno_print[[all(escl not in modello for escl in excl_comp) for modello in fabbisogno_print.Modello]]

fabbisogno_print.loc['Totale'] = fabbisogno_print.sum()
fabbisogno_print.drop(columns=['CI','Linea'], inplace=True)
fabbisogno_print['Modello'].iloc[-1] = ""
fabbisogno_print.loc[:,'Totale'] = fabbisogno_print.sum(numeric_only=True, axis=1)
fabbisogno_print

fab_sx, fab_dx= st.columns([1,4])

with fab_sx:
    st.metric('Motori totali', value=int(fabbisogno_print.Totale.iloc[-1]), border=True)


# FINE IMPORTAZIONE DEI DATI ===============================================

machines_retrieve=calendario[['Linea','Macchina']]

if line == 'AD':
    macchine = list(machines_retrieve[machines_retrieve.Linea=='AD']['Macchina'])

else:
    macchine = list(machines_retrieve[machines_retrieve.Linea=='AM']['Macchina'])
    

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
            #if fase=='rettifica' and mese=='GEN':
            #    st.subheader(mese)
            #    workload_graph
            #    to_split
            #to_split = to_split[to_split.Fase == fase].reset_index(drop=True)

            # dizionario di saturazione di partenza, che viene aggiornato via via che si assegnano volumi
            dic_sat = dict(zip(workload_graph['Macchina standard'], workload_graph['delta_ore'])) #delta + = macchina sovra satura
            
            if (line=='AM') and ('Tacchella 2' not in dic_sat.keys()):
                dic_sat['Tacchella 2'] = - 2000

            
            for i in range(len(to_split)):
                macchina_check = to_split['Macchina standard'].iloc[i]

                tc = to_split['tempo_ciclo'].iloc[i] / 60

                #if fase=='rettifica' and mese=='GEN':
                  #  st.write('saturazione', dic_sat[macchina_check])

                if dic_sat[macchina_check] > 0.001: #solo se la macchina ha ancora lavoro in eccesso
                    #pcs_to_move = to_split.delta_volume.iloc[i]
                    pcs_to_move = dic_sat[macchina_check] / tc 
                    if pcs_to_move > to_split.delta_volume.iloc[i]:
                        pcs_to_move = to_split.delta_volume.iloc[i]


                    #if fase=='rettifica' and mese=='GEN':
                    #    st.write(pcs_to_move)
                    # ho calcolato i pezzi da spostare in base alla saturazione dinamica della macchina preferita
                    
                    wl_start = to_split['wl'].iloc[i]
                    key_alt = to_split.key_alt.iloc[i]

                    try:
                        alternative = dic_alt[key_alt]
                    except:
                        alternative = []

                
                    #pcs_to_move = dic_sat[macchina_check] / tc

                    modello = to_split.Modello.iloc[i]
                    mac_std = to_split['Macchina standard'].iloc[i]
                    ci = to_split.CI.iloc[i]
                    tot_moved = 0

                    #if fase == 'rettifica' and mese=='GEN':
                    #    st.subheader(modello)
                    #    st.write('--Pezzi da spostare: ', pcs_to_move)

                    for elemento in alternative:
                        #if fase == 'rettifica' and mese=='GEN':
                         #   st.write(f'---Sto provando {elemento[0]}')
                        mac_alt = elemento[0]
                        tc_alt = elemento[1]
                        ore_disponibili = - dic_sat[mac_alt]
                        #if (mese=='GEN') & (fase=='rettifica'):
                        #    st.write(f'macchina {mac_alt} ore disp:{ore_disponibili}')

                        if ore_disponibili > 0:
                            max_pcs = ore_disponibili * 60 / tc_alt
                            #if fase=='rettifica' and mese=='GEN':
                             #   st.write(f'----Ore disponibili: {ore_disponibili}')
                             #   st.write(f'-----Max pcs: {max_pcs}')
                            if max_pcs < pcs_to_move:
                                #if fase=='rettifica' and mese=='GEN':
                                 #   st.write('------Capienza non sufficiente, ne prendo il massimo')
                                moved = max_pcs
                                tot_moved += moved
                                #if fase == 'rettifica' and mese=='GEN':
                                 #   st.write(f'--------ne ho spostati {moved}')
                                pcs_to_move -= max_pcs
                                motori = moved/ci
                                wl_new = tc_alt * moved / 60
                                #dic_sat[mac_alt] = - ore_disponibili + wl_new
                                dic_sat[mac_alt] += wl_new
                                dic_sat[macchina_check] -= moved*tc

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
                                dic_sat[macchina_check] -= moved*tc
                                #if fase == 'rettifica' and mese=='GEN':
                                 #   st.write(f'!!mossi tutti!!--------ne ho spostati {moved} sulla macchina {mac_alt}')


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
                                #db_assegnato['volumi_pezzi'].iloc[-1] = db_assegnato['volumi_pezzi'].iloc[-1] - db_assegnato['delta_volume'].iloc[-1]
                                db_assegnato['volumi_pezzi'].iloc[-1] = db_assegnato['volumi_pezzi'].iloc[-1] - tot_moved
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

                    
                else:
                    db_assegnato = new_row(db_assegnato)
                    db_assegnato['Modello'].iloc[-1] = to_split.Modello.iloc[i]
                    db_assegnato['Macchina standard'].iloc[-1] = to_split['Macchina standard'].iloc[i]
                    db_assegnato['Macchina assegnata'].iloc[-1] = to_split['Macchina standard'].iloc[i]
                    db_assegnato['volumi'].iloc[-1] = to_split['volumi'].iloc[i]
                    db_assegnato['tempo_ciclo'].iloc[-1] = to_split['tempo_ciclo'].iloc[i]
                    db_assegnato['wl'].iloc[-1] = to_split['wl'].iloc[i]
                    db_assegnato['CI'].iloc[-1] = to_split['CI'].iloc[i]
                    db_assegnato['volumi_pezzi'].iloc[-1] = to_split['volumi_pezzi'].iloc[i]
                    db_assegnato['moving_type'].iloc[-1] = 'no_moving_tipo2'

                #db_assegnato = new_row(db_assegnato)

                # se arrivo qui, devo aggiungere al db assegnato le righe che in partenza erano da spostare, ma dopo i primi movimenti non lo sono più
                
                
                #if fase=='rettifica' and mese=='GEN':
                 #   db_assegnato
                #lista_assegnati.append(db_assegnato)
                #continue
            
            #workload_elaborato = pd.concat([workload_elaborato,workload_graph])
            lista_assegnati.append(db_assegnato)

    db_assegnato = pd.concat(lista_assegnati)
    return db_assegnato

# ottimizzazione accumulo============================================
db_assegnato = livella_macchine(workload, mesi)
#st.write(db_assegnato[(db_assegnato.Mese == 'GIU') & (db_assegnato.Fase == 'rettifica') & (db_assegnato['Macchina standard']=='Tacchella 3')])
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
asis = px.bar(workload_graph, x='Mese', y= 'saturazione', color='Macchina', barmode='group')
asis.add_hline(y=1, line_color='red', line_dash='dash')
st.plotly_chart(asis,use_container_width=True)

st.subheader('Situazione saturazione dopo livellamento su macchine alternative')
after = px.bar(workload_graph, x='Mese', y= 'sat_dopo', color='Macchina', barmode='group')
after.add_hline(y=1, line_color='red', line_dash='dash')
st.plotly_chart(after,use_container_width=True)

tab1, tab2 = st.tabs(['Accumulo','Drill down'])

#callback di aggiornamento non prod + fabbisogno

def callback():
    # va aggiornata anche st.session_state.utilizzo ma non
    for i in range(len(utilizzo)):
        fabb_change = st.session_state.fab_melt.copy()
        util = utilizzo.utilizzo.iloc[i]
        #st.write(util)
        mese = utilizzo.Mese.iloc[i]
        modello = utilizzo.Modello.iloc[i]

        for j in range(len(fabb_change)):
            asis=fabb_change.volumi.iloc[j]
            if (fabb_change.iloc[j].mese == mese) & (fabb_change.Modello.iloc[j] == modello):
                fabb_change.volumi.iloc[j] = asis - util
        #st.write(fabb_change[(fabb_change.mese == mese) & (fabb_change.Modello == modello)])
        st.session_state.fab_melt = fabb_change

def callback2():
    change = st.session_state.utilizzo.copy()
    for i in range(len(utilizzo)):
        delta = utilizzo.Var.iloc[i]
        mese = utilizzo.Mese.iloc[i]
        modello = utilizzo.Modello.iloc[i]
        for j in range(len(change)):
            if (change.iloc[j].Mese == mese) & (change.Modello.iloc[j] == modello):
                change.Var.iloc[j] = delta
    st.session_state.utilizzo = change



with tab1:
    critiche = list(workload_graph[workload_graph.sat_dopo > 1.01]['key'].unique())
    cod_crit = db_assegnato[[any(mac in check for mac in critiche) for check in db_assegnato['key'].astype(str)]]
    cod_crit['moving_type'] = np.where((cod_crit.wl > 400) & (cod_crit.moving_type == 'no_moving'), 'no_moving_iniziale', cod_crit.moving_type)
    #non_prodotto = cod_crit[['iniziale' in tipo for tipo in cod_crit.moving_type]]
    non_prodotto = cod_crit
    non_prodotto = non_prodotto.merge(workload_graph[['key','sat_dopo','ore_disp']], how='left', left_on='key', right_on='key')
    non_prodotto['qty_res [motori]'] = (non_prodotto['sat_dopo']-1) * non_prodotto['ore_disp'] * 60 / non_prodotto['tempo_ciclo'] / non_prodotto.CI
    non_prodotto['key_accumulo'] = non_prodotto['Linea']+'-'+non_prodotto['Modello']

    #non_prodotto = non_prodotto.merge(accumulo[['key','Stock_fine_periodo','Obiettivo_accumulo_adj']], how='left', left_on='key_accumulo', right_on='key')

    #prendo le righe peggiori per mese e modello (quelle con il maggior numero di motori non fatti)
    #'non prodotto'
    #non_prodotto
    non_prodotto['qty_res [motori]'] = np.where(non_prodotto['qty_res [motori]'].astype(str)=='nan', non_prodotto.volumi, non_prodotto['qty_res [motori]'])
    non_prodotto = non_prodotto.loc[list(non_prodotto[['Mese','Modello','qty_res [motori]']].groupby(by=['Mese','Modello']).idxmax()['qty_res [motori]'])]
    #'non prod dopo'
    #non_prodotto
    #if 'utilizzo' not in st.session_state:
        # per la prima volta lo creo, poi dovrà pescare il db variazioni
       # st.session_state.utilizzo = db_assegnato[['Mese','Modello']].copy().drop_duplicates()

        #st.session_state.utilizzo = non_prodotto[['Mese','Modello']].copy()
        #st.session_state.utilizzo['utilizzo']=0
        #st.session_state.non_prod = st.session_state.non_prod.groupby(by=['Mese','Modello','Macchina assegnata'], as_index=False).acgg({'qty_res[motori]':'max','Stock_fine_periodo':'mean','Obiettivo_accumulo_adj':'mean','utilizzo':'sum'})


    st.subheader('Situazioni non risolte')
    non_prodotto['qty_res [motori]'] = np.where(non_prodotto['qty_res [motori]']<non_prodotto.volumi,non_prodotto['qty_res [motori]'],non_prodotto.volumi )
    non_prodotto = non_prodotto.sort_index()
    #'workload 669'
   # workload
    non_prodotto['volumi'] = [np.round(vol, 0) for vol in non_prodotto.volumi]
    non_prodotto['qty_res [motori]'] = [np.round(vol, 0) for vol in non_prodotto['qty_res [motori]']]
    st.dataframe(non_prodotto[mask_non_prod])

    


    st.subheader('Gestione accumulo')
    selected_item = st.selectbox('Selezionare codice', options=fabbisogno.Modello.unique())
    sxt1, dxt1 = st.columns([2,1])
    with sxt1:  
        #st.title('Grafico andamento stock')
        st.subheader('Andamento stock')
        stock_graph = stock[stock.Modello==selected_item]
        stock_and = px.line(stock_graph, x='Mese',y='andamento')
        st.plotly_chart(stock_and)

        pass

    with dxt1:
        st.subheader('Gestione Stock')
        st.write(' il segno + indica un aumento della quantità da produrre \n\n ne consegue un aumento di stock')

        utilizzo = st.session_state.utilizzo.copy()
        utilizzo = utilizzo.sort_index()
        utilizzo['Mese'] = pd.Categorical(utilizzo['Mese'], categories=mesi)
        utilizzo = utilizzo[utilizzo.Modello == selected_item]
        utilizzo = utilizzo.sort_values(by='Mese').reset_index(drop=True)
        utilizzo = st.data_editor(utilizzo)
        submit_button = st.button(label='Ricalcola', on_click=callback2)
        'Download file variazioni'
        scarica_excel(st.session_state.utilizzo, 'Variazioni_aggiornato.xlsx')
        
   
    prog_prod = db_assegnato[['Mese','Linea','Fase','Macchina assegnata','Modello','volumi','volumi_pezzi']]
    prog_prod['Mese'] = pd.Categorical(prog_prod['Mese'], categories=mesi)
    prog_prod=prog_prod.sort_values(by=['Mese','Linea','Fase','Macchina assegnata']).reset_index(drop=True)
    

    #coperture
    coperture = coperture.rename(columns={'variable':'Mese'})
    stock_cop = stock[['Modello','Mese','andamento']].merge(coperture[['Modello','Mese','value']], how='left', left_on=['Modello','Mese'], right_on=['Modello','Mese'])
    stock_cop = stock_cop[stock_cop.value.astype(str) != 'nan']

    list_cop = []
    stock_cop['copertura']=0
    for cod in stock_cop.Modello.unique():
        frame_work = stock_cop[stock_cop.Modello == cod]
        for i in range(len(frame_work)-1):
            stock_val = frame_work.andamento.iloc[i]
            cop = 0
            for j in range(i,len(frame_work)):
                domanda = frame_work.value.iloc[j]
                if stock_val > domanda:
                    cop+=1
                    stock_val -= domanda
                else:
                    cop += stock_val / domanda
                    break
            if cop < 0:
                cop = 0
            frame_work.copertura.iloc[i] = cop
        frame_work.copertura.iloc[11] = frame_work.andamento.iloc[11]/frame_work.value.iloc[11] #l'ultimo mese ha copertura 1 per convenzione
        list_cop.append(frame_work)
    
    coperture_tot = pd.concat(list_cop)
    

    def highlighter(x):
        is_negative = x < soglia
        style_lt = "background-color: #EE2E31; color: white; font-weight: bold;"
        style_gt = "background-color: #006E50; color: white; font-weight: bold;"
        return [style_lt if i else style_gt for i in is_negative]
    
    coperture_tot = coperture_tot[['Modello','Mese','copertura']].fillna(0)
    coperture_tot['copertura'] = [np.round(val, 2) for val in coperture_tot.copertura]
    #coperture_tot['copertura'] = coperture_tot['copertura'].astype(float)
    #coperture_tot

    coperture_tot = coperture_tot.pivot(index='Modello',columns='Mese')
    coperture_tot = coperture_tot[[('copertura','GEN'),('copertura','FEB'),('copertura','MAR'),('copertura','APR'),('copertura','MAG'),('copertura','GIU'),('copertura','LUG'),('copertura','AGO'),('copertura','SET'),('copertura','OTT'),('copertura','NOV'),('copertura','DIC')]]
    st.subheader('Coperture', divider='grey')
    #coperture_tot.style.apply(highlighter)
    sx_soglia, dx_soglia = st.columns([1,8])
    with sx_soglia:
        soglia = st.number_input('Inserire soglia',value=1.0, step=0.1)

    st.write(coperture_tot.style.apply(highlighter).format("{:.2f}"))
    stock_andamento = stock[['Modello','Mese','andamento']].pivot(index='Modello',columns='Mese')
    stock_andamento=stock_andamento[[('andamento','GEN'),('andamento','FEB'),('andamento','MAR'),('andamento','APR'),('andamento','MAG'),('andamento','GIU'),('andamento','LUG'),('andamento','AGO'),('andamento','SET'),('andamento','OTT'),('andamento','NOV'),('andamento','DIC')]]
    st.subheader('Stock', divider='grey')
    st.dataframe(stock_andamento)

    #prog_prod
    #prog_piv = prog_prod[['Mese','Modello','volumi_pezzi']].groupby(by=['Mese','Modello'],as_index=False).min().pivot(index='Modello',columns='Mese')

    st.subheader('Programma di produzione', divider='grey')
    #st.write(prog_prod)
    #st.write(prog_piv)

    #'fabbisogno melt debug'
    #fabbisogno_melt
    prpr = fabbisogno_melt[['Mese','Modello','volumi']].drop_duplicates()
    prpr = prpr.merge(var, how='left', left_on=['Mese','Modello'], right_on=['Mese','Modello'])
    #prpr
    prpr['Prod'] = prpr['volumi'] #+prpr['Var']
    prpr = prpr[['Mese','Modello','Prod']].pivot(index='Modello',columns='Mese')
    prpr=prpr[[('Prod','GEN'),('Prod','FEB'),('Prod','MAR'),('Prod','APR'),('Prod','MAG'),('Prod','GIU'),('Prod','LUG'),('Prod','AGO'),('Prod','SET'),('Prod','OTT'),('Prod','NOV'),('Prod','DIC')]]
    st.write(prpr)


    'Download programma di produzione'
    db_assegnato['volumi'] = [int(numero) for numero in db_assegnato.volumi]
    db_assegnato['tempo_ciclo'] = [np.round(numero, 2) for numero in db_assegnato.tempo_ciclo]
    db_assegnato['wl'] = [np.round(numero, 2) for numero in db_assegnato.wl]
    db_assegnato['volumi_pezzi'] = [int(numero) for numero in db_assegnato.volumi_pezzi]
    db_assegnato = db_assegnato[db_assegnato.volumi != 0]
    scarica_excel(db_assegnato[db_assegnato.columns[:10]], 'Programma_prod.xlsx')
    #db_assegnato
    
with tab2:

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

        fabbisogno_melt['alternative'] = fabbisogno_melt['alternative'].fillna(0)
        fabbisogno_melt['wl'] = [np.round(wl, 2) for wl in fabbisogno_melt.wl]
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
