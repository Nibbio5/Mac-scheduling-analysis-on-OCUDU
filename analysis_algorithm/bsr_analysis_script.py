import sys

# ==========================================
# --- CONFIGURAZIONE ---
# ==========================================
# Inserisci il nome del file di testo contenente i log del trace gNB
nome_file_log = "bsr.txt" 
# ==========================================

def converti_valore(val_str):
    """
    Converte stringhe come '39.8k' o '1.5M' in numeri reali (float).
    """
    val_str = val_str.strip()
    if val_str == '0': 
        return 0.0
        
    # Gestione suffissi 'k' (kilo) e 'M' (mega)
    if val_str.endswith('k') or val_str.endswith('K'):
        return float(val_str[:-1]) * 1000.0
    elif val_str.endswith('M') or val_str.endswith('m'):
        return float(val_str[:-1]) * 1000000.0
    else:
        # Nel caso fosse un numero puro (es. '142')
        return float(val_str)

def analizza_bsr_trace(file_log):
    somma_bsr = {}
    conteggio = {}

    print(f"Lettura del trace gNB dal file: '{file_log}'...\n")

    try:
        with open(file_log, 'r', encoding='utf-8') as file:
            for linea in file:
                linea = linea.strip()
                
                # Salta le righe vuote o le intestazioni della tabella
                if not linea or 'DL' in linea or 'pci rnti' in linea:
                    continue
                
                # Dividiamo la riga usando il separatore '|'
                parti = linea.split('|')
                if len(parti) < 3:
                    continue # Non è una riga contenente statistiche DL/UL
                
                try:
                    # 1. Estraiamo l'RNTI dalla prima parte (es. "1 4602")
                    rnti_str = parti[0].split()[-1]
                    rnti = int(rnti_str)

                    # 2. Estraiamo i dati di Uplink (la terza parte)
                    ul_tokens = parti[2].split()
                    
                    # L'ottavo indice (nona colonna) è il BSR
                    # Colonne UL: pusch, rsrp, ri, mcs, brate, ok, nok, (%), bsr, ta, phr
                    bsr_str = ul_tokens[8]
                    
                    # Convertiamo il valore in un numero reale
                    bsr_val = converti_valore(bsr_str)

                    # 3. Aggiorniamo le statistiche per questo RNTI
                    if rnti not in somma_bsr:
                        somma_bsr[rnti] = 0.0
                        conteggio[rnti] = 0
                        
                    somma_bsr[rnti] += bsr_val
                    conteggio[rnti] += 1
                    
                except (ValueError, IndexError):
                    # Ignoriamo righe corrotte o non formattate come previsto
                    continue
                    
    except FileNotFoundError:
        print(f"Errore: Il file '{file_log}' non è stato trovato.")
        return

    if not conteggio:
        print("Nessun dato RNTI o BSR valido trovato nel file.")
        return

    # --- CALCOLO DELLA MEDIA E STAMPA PER LA TESI ---
    print("=" * 55)
    print(" RISULTATI BSR (DA INSERIRE NELLA TESI)")
    print("=" * 55)
    
    # Ordiniamo gli RNTI per una stampa coerente (es. 4602 poi 4603)
    rntis = sorted(somma_bsr.keys())
    medie = []
    
    for i, rnti in enumerate(rntis):
        media = somma_bsr[rnti] / conteggio[rnti]
        medie.append(media)
        print(f"UE {i+1} (RNTI {rnti}) | Campioni: {conteggio[rnti]:<4} | BSR Medio: {media:,.1f} Bytes")
        
    print("=" * 55)

    # Breve analisi automatica dello squilibrio (se ci sono 2 UE)
    if len(medie) == 2:
        media_ue1, media_ue2 = medie[0], medie[1]
        print("\n-> Interpretazione dei dati per la Tesi:")
        if media_ue1 > (media_ue2 * 3) or media_ue2 > (media_ue1 * 3):
            print("Emerge un forte SQUILIBRIO. Uno degli UE accumula grandi quantità")
            print("di dati in coda, denotando un collo di bottiglia trasmissivo.")
        else:
            print("I buffer sono bilanciati. Entrambi gli UE smaltiscono i dati")
            print("in modo efficiente e simmetrico.")

if __name__ == "__main__":
    analizza_bsr_trace(nome_file_log)