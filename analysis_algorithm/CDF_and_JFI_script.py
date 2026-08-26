import pandas as pd

# ==========================================
# 1. IMPOSTAZIONI
# ==========================================
# File Downlink
NOME_FILE_DL = "good_rr_dl.csv"
SEC_INIZIO_DL = 650
SEC_FINE_DL = 940

# File Uplink
NOME_FILE_UL = "good_rr_ul.csv"
SEC_INIZIO_UL = 285
SEC_FINE_UL = 575
# ==========================================

def calcola_e_stampa_medie(nome_file, sec_inizio, sec_fine, direzione):
    """Funzione che legge il CSV, taglia il tempo e stampa le medie gestendo i cambi di RNTI."""
    try:
        df = pd.read_csv(nome_file)
        
        # Assicuriamoci che la colonna del tempo sia numerica
        col_tempo = df.columns[0]
        df[col_tempo] = pd.to_numeric(df[col_tempo], errors='coerce')
        
        # Ritagliamo solo l'intervallo di test
        df_test = df[(df[col_tempo] >= sec_inizio) & (df[col_tempo] <= sec_fine)].copy()
        
        if not df_test.empty:
            num_colonne = len(df.columns)
            
            if num_colonne == 4:
                # CASO RNTI CAMBIATO (es. Uplink: 4603 e 4604 per il Q1)
                somma_q1_bit = df_test.iloc[:, 1] + df_test.iloc[:, 3]
                media_q1 = (somma_q1_bit / 1000000).mean()
                media_q2 = (df_test.iloc[:, 2] / 1000000).mean()
                label_q1 = "Quectel 1 (4603 + 4604)"
            else:
                # CASO NORMALE (3 colonne)
                media_q1 = (df_test.iloc[:, 1] / 1000000).mean()
                media_q2 = (df_test.iloc[:, 2] / 1000000).mean()
                label_q1 = "Quectel 1 (4603)"
                
            print("=" * 50)
            print(f"📊 RISULTATI MEDI {direzione} ({sec_inizio}s - {sec_fine}s)")
            print(f"📁 File analizzato: {nome_file}")
            print("=" * 50)
            print(f"📱 {label_q1}: {media_q1:.2f} Mbps")
            print(f"📱 Quectel 2 (4605): {media_q2:.2f} Mbps")
            print("-" * 50)
            print(f"🚀 THROUGHPUT TOTALE: {media_q1 + media_q2:.2f} Mbps")
            print("=" * 50)
            print("\n") # Spazio vuoto per separare i due blocchi
            
        else:
            print(f"⚠️ Nessun dato trovato in {nome_file} nell'intervallo {sec_inizio}s - {sec_fine}s.\n")

    except FileNotFoundError:
        print(f"❌ Errore: Il file '{nome_file}' non è stato trovato.\n")
    except Exception as e:
        print(f"❌ Errore durante l'elaborazione di {nome_file}: {e}\n")


# ==========================================
# 2. ESECUZIONE DEL CALCOLO
# ==========================================
# Eseguiamo la funzione prima per il DL e poi per l'UL
calcola_e_stampa_medie(NOME_FILE_DL, SEC_INIZIO_DL, SEC_FINE_DL, "DOWNLINK")
calcola_e_stampa_medie(NOME_FILE_UL, SEC_INIZIO_UL, SEC_FINE_UL, "UPLINK")