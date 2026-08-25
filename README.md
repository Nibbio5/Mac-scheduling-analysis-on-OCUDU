# Multi-User MAC Scheduling Evaluation and Enhancement in srsRAN 5G Standalone

This repository contains the implementation, experimental configurations, and analysis tools developed for evaluating and enhancing **multi-user MAC scheduling algorithms** within the **srsRAN** 5G Standalone (SA) software suite, focusing on the O-RAN aligned **OCUDU framework**.

The project transitionally evaluates how resource allocation policies impact overall network performance under real-world conditions, utilizing a software-defined radio (SDR) testbed.

## Project Overview

The core of this work lies in the **modification of C++ header files and scheduler policy interfaces** (specifically `scheduler_policy.h`) within srsRAN to implement and refine priority-based scheduling logic. The performance of several algorithms is compared, including:
*   **Round Robin (RR)**
*   **Proportional Fair (PF)**
*   **Maximum Throughput**
*   **QoS-Aware / Custom Priority Scheduling** (utilizing parameters like `pending_bytes` from the `ue_newtx_candidate` struct)

---

## Key Features & Methodology

*   **Real Hardware Testbed:** Validation is performed on an end-to-end 5G SA network utilizing an **Ettus USRP B210** as the gNodeB, **Open5GS** as the Core Network, and commercial **Quectel 5G modules** as User Equipments (UEs).
*   **Realistic Scenario Testing:** Evaluation of scheduling behavior across distinct environment setups, specifically contrasting **Cell-Center scenarios** (high SNR/CQI) with challenging **Cell-Edge scenarios** (low SNR, CQI 5–7).
*   **Advanced Network Diagnostics:**
    *   **Throughput & Distribution:** Analyzed globally and individually using **Cumulative Distribution Functions (CDF)**.
    *   **MAC-Layer Latency & Queue Dynamics:** Monitored through **Buffer Status Report (BSR)** evolution over time and post-processed using **Wireshark (PCAP)** packet analysis.
    *   **Resource Fairness:** Quantified strictly using the standard **Jain's Fairness Index** to evaluate resource distribution equity.
## Network Setup & Experimental Testbed

The experimental network is configured as a **5G Standalone (SA) Private Network**. The deployment disaggregates the Control/User Plane and is divided into three main segments: the 5G Core Network, the Radio Access Network (gNodeB), and the User Equipments (UEs).

                 +----------------------------------+   
                 |         5G CORE NETWORK          |
                 |            (Open5GS)             |
                 +-----------------+----------------+
                                   |
                                   | (S1-MME / NG-C, NG-U)
                                   |
                 +-----------------+----------------+
                 |       RADIO ACCESS NETWORK       |
                 |    srsRAN (OCUDU Framework)      |
                 |        Host PC + USRP B210       |
                 +--------+----------------+--------+
                          |                |
            (RF Link Center)               (RF Link Edge)
                          |                |
         +----------------+---+        +---+----------------+
         |     USER EQUIPMENT |        |   USER EQUIPMENT   |
         |   Quectel 5G Modem |        |   Quectel 5G Modem |
         |   (Good Condition) |        |   (Cell-Edge/Bad)  |
         +--------------------+        +--------------------+

### 1. 5G Core Network (5GCN)
*   **Software Core:** **Open5GS**, an open-source implementation of the 5G Core.
*   **Configuration:** Configured with custom Network Slicing (S-NSSAI) and Dedicated APNs. Static routing and NAT are established between the host system and the containerized core.

### 2. Radio Access Network (gNodeB)
*   **SDR Frontend:** **Ettus USRP B210** transceiver connected via high-speed USB interface acting as the RF frontend.
*   **Protocol Stack:** **srsRAN** integrated within the **OCUDU framework**.
*   **Custom Tuning:** The `gnb.yaml` file was modified to adapt PHY-layer parameters, physical resource blocks (PRBs), and scheduling policies (`scheduler_policy.h`) for multi-user testcases.

### 3. User Equipments (UEs) & Traffic Generation
*   **Devices under Test:** Commercial **Quectel 5G modules** equipped with custom lab SIM cards and connected directly to test laptops.
*   **Traffic Generator:** **iPerf3** is run on the client laptops to generate synthetic Uplink (UL) and Downlink (DL) traffic flows.
*   **Performance Tracking:** 
    *   **PCAP Logging:** Packet captures (PCAP) are recorded on the gNodeB host PC via Wireshark to accurately estimate MAC-layer scheduling latency.
    *   **Metrics Extraction:** Real-time JSON output metrics are streamed via WebSocket and parsed using **Python and Pandas** to compare the performance profiles of the selected scheduling algorithms.
## Data Generation & PCAP Capturing

To evaluate the scheduling performance of each algorithm under realistic conditions, we generate controlled traffic and capture raw packet data directly at the gNodeB interface. This allows us to perform high-resolution diagnostics of throughput, packet queues, and MAC-layer latency.

### 1. Synthetic Traffic Generation (iPerf3)
*   **Traffic Engine:** We utilize **iPerf3** to generate continuous, bidirectional TCP/UDP traffic flows between the client laptops (connected to the Quectel 5G UEs) and the 5G Core Network.
*   **Test Scenarios:** 
    *   **Uplink (UL) Stress Testing:** Simulating high-demand data uploads to analyze queue growth in the Buffer Status Reports (BSR).
    *   **Downlink (DL) Stress Testing:** Simulating massive streaming/downloads to evaluate how resource blocks are distributed among multiple users under different policies.

### 2. Packet Capture (PCAP) on the gNodeB Host
Instead of measuring end-to-end latency (such as standard ICMP Ping), we record **raw packet captures (PCAP format)** directly on the laptop hosting the gNodeB (USRP B210). 

*   **Capture Mechanism:** Wireshark/Tshark is run on the gNodeB host to sniff and save the exact arrival and departure times of packet headers.
*   **Why Capturing on the gNodeB?** 
    Questo approccio ci consente di bypassare i tempi morti della rete di trasporto esterna. Possiamo confrontare il timestamp esatto in cui un pacchetto raggiunge l'interfaccia di rete fisica con l'istante in cui lo scheduler MAC assegna effettivamente la "grant" (parola) radio per inviarlo.
*   **Data Flow:**
    
    ```
    [UE / iPerf3 Client] ---> (Radio Link) ---> [gNodeB (USRP B210) Capture Interface] ---> [Open5GS Core]
                                                   |
                                                   +---> [Saved PCAP Log File] 
                                                               |
                                                               v
                                                   [Wireshark MAC-Layer Analysis]
    ```

### 3. Post-Processing & Analysis
Once the PCAP is saved at the gNodeB, we analyze the raw scheduling data in two steps:
1.  **Wireshark Filter Analysis:** We use targeted dissectors (such as LTE/NR MAC protocols) to filter queue updates and estimate latency from physical packet timestamps.
2.  **Automated Parsing:** Using Python scripts paired with `pandas`, we extract the timestamp arrays from the PCAP metadata and correlate them with the real-time WebSocket JSON metrics, producing the final cumulative distribution functions (CDF) and throughput graphs.
