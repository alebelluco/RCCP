import pandas as pd
import streamlit as st
import plotly_express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(layout='wide')
st.title('RCCP Lavorazioni Meccaniche')
st.subheader(':red[Draft]', divider='red')
path = st.file_uploader('Caricare il file')
if not path:
    st.stop()

df = pd.read_excel(path)

df = df[df.columns[0:15]]
df = df.drop(columns=['I°sem','II°sem'])
# eliminazione prima riga
df = df[1:]


flat_path = st.file_uploader('Caricare il file statico')
if not flat_path:
    st.stop()
flat = pd.read_excel(flat_path)

flat = flat.melt(id_vars=['Linea','Codice','Fase','Macchina standard'])
flat = flat[flat['Macchina standard'] == flat['variable']]
flat['Codice'] = [stringa.replace(' ','') for stringa in flat.Codice]

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
#st.write(cad)

# OEE

oee = pd.read_excel(flat_path, sheet_name='OEE')

#st.stop()

# isolo i dati di pianificazione

#df_pian = df[0:4].copy()
#st.subheader('Dati di pianificazione', divider='grey')
#st.dataframe(df_pian, use_container_width=True)

st.subheader('Volumi', divider='grey')

df = df[5:] # elimino la parte di pianificazione
df = df[df[df.columns[0]].astype(str) != 'nan']

esclusioni = ['Produz', 'Preserie','Progressivo','gg']
df = df[[all(escluso not in test for escluso in esclusioni) for test in df[df.columns[0]].astype(str)]]
#df = df[[all(escluso not in test for escluso in esclusioni) for test in df['PPP 2025 esp 013'].astype(str)]]
df = df[:-5]
df = df.reset_index(drop=True)
df=df.rename(columns={df.columns[0]:'Modello'})
df = df.fillna(0)

#filtro per 896 - scr
df = df[['SCR' not in check for check in df.Modello.astype(str)]]
df = df[['896' not in check for check in df.Modello.astype(str)]]

df['Gruppo']='PPP_Veicoli'

df_tot = pd.concat([df, cad])

df_tot = df_tot.merge(bom, how='left', left_on='Modello', right_on='Modello')
df_tot = df_tot[df_tot.Nota.astype(str) != 'in phase out, non lo consideriamo']

fabbisogno_aggregato_alberi = df_tot.copy()
fabbisogno_aggregato_camme = df_tot.copy()

fabbisogno_aggregato_alberi = fabbisogno_aggregato_alberi.drop(columns=['Modello','Gruppo','Nota','Albero_camme','CI [2 | 4]'])
fabbisogno_aggregato_alberi = fabbisogno_aggregato_alberi.groupby(by='Albero', as_index=False).sum()
fabbisogno_aggregato_alberi = fabbisogno_aggregato_alberi.rename(columns={'Albero':'Modello'})
fabbisogno_aggregato_alberi['CI']=1
fabbisogno_aggregato_alberi['Linea']='AM'

fabbisogno_aggregato_camme = fabbisogno_aggregato_camme.drop(columns=['Modello','Gruppo','Nota','Albero'])
fabbisogno_aggregato_camme = fabbisogno_aggregato_camme.groupby(by=['Albero_camme','CI [2 | 4]'], as_index=False).sum()
fabbisogno_aggregato_camme = fabbisogno_aggregato_camme.rename(columns={'CI [2 | 4]':'CI', 'Albero_camme':'Modello'})
fabbisogno_aggregato_camme['Linea']='AD'

fabbisogno = pd.concat([fabbisogno_aggregato_alberi,fabbisogno_aggregato_camme])

st.dataframe(fabbisogno, use_container_width=True)
#st.write(flat)

# melt dei volumi
# creazione chiave adatta
# merge dei volumi su flat
# groupby per macchina

flat['key'] = flat['Linea']+'-'+flat['Codice']
fabbisogno_melt= fabbisogno.melt(id_vars=['Modello','Linea','CI'])
fabbisogno_melt['key']=fabbisogno_melt['Linea']+'-'+fabbisogno_melt['Modello'].astype(str)
fabbisogno_melt = fabbisogno_melt.rename(columns={'variable':'mese', 'value':'volumi'})
fabbisogno_melt = fabbisogno_melt.merge(flat, how='left', left_on='key', right_on='key')



#flat
fabbisogno_melt = fabbisogno_melt[fabbisogno_melt.Codice.astype(str)!='nan']

fabbisogno_melt['wl'] = fabbisogno_melt['volumi']*fabbisogno_melt['CI']*fabbisogno_melt.value / 60
#fabbisogno_melt['wl'] = fabbisogno_melt['volumi']*fabbisogno_melt.value / 60

workload = fabbisogno_melt[['mese','Macchina standard','wl']].groupby(by=['mese','Macchina standard'], as_index=False).sum()


workload = workload.merge(oee, how='left', left_on='Macchina standard', right_on='Macchina')



mesi = ['GEN','FEB','MAR','APR','MAG','GIU','LUG','AGO','SET','OTT','NOV','DIC']

workload['mese'] = pd.Categorical(workload['mese'], categories=mesi)
workload = workload.sort_values(by='mese')


workload['ore_disp'] = 24.6*7.5*3 * workload.OEE#metterle dal file flat
workload['saturazione'] = workload['wl'] / workload['ore_disp']
workload['limite'] = 1
#workload

select=[
'STAMA 1',
'STAMA 2',
'LICON',
'STAMA 3',
'STAMA 5'
]

mesi = ['GEN','FEB','MAR','APR','MAG','GIU','LUG']

workload = workload[[any(mese in check for mese in mesi) for check in workload.mese.astype(str)]]


st.subheader('Saturazione impianti per mese', divider='red')
sx,cx,dx=st.columns([1,8,1])
with sx:    
    mese_select = st.selectbox('Selezionare mese', options=workload.mese.unique())
with dx:
    select2 = st.multiselect('Selezionare macchina', options=fabbisogno_melt['Macchina standard'].unique())
    if len(select2)==0:
        select2 = fabbisogno_melt['Macchina standard'].unique()
#workload = workload[workload.mese == mese_select]
#workload = workload[[any(macchina in check for macchina in select) for check in workload['Macchina standard'].astype(str)]]
workload['colore'] = np.where(workload.mese == mese_select,'pink','grey')


carico = go.Figure()

carico.add_trace(
    go.Bar(
        x=workload['mese'].astype(str)+workload['Macchina standard'],
        y= workload.saturazione,
        marker_color=workload['colore']
    )
)

carico.add_trace(
    go.Scatter(
        x=workload['mese'].astype(str)+workload['Macchina standard'],
        y=workload.limite,
        line = dict(color='red')
    )
)

carico.update_layout(height=600)

c1,c2 = st.columns([2,1])

with c1:
    st.divider()
    st.plotly_chart(carico, use_container_width=True)

with c2:
    st.subheader('Dettaglio', divider='grey')
    fabbisogno_melt = fabbisogno_melt[fabbisogno_melt.mese == mese_select]
    fabbisogno_melt[[any(macchina in check for macchina in select2) for check in fabbisogno_melt['Macchina standard'].astype(str)]]