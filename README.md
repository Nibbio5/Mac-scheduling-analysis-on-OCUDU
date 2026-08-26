# Multi-User MAC Scheduling Evaluation and Enhancement in srsRAN 5G Standalone

This repository contains the implementation, experimental configurations, and analysis tools developed for evaluating and enhancing **multi-user MAC scheduling algorithms** within the **OCUDU** 5G Standalone (SA) software suite, focusing on the O-RAN aligned **OCUDU framework**.

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
*   **Network Diagnostics:**
    *   **Throughput & Distribution:** Analyzed globally and individually using **Cumulative Distribution Functions (CDF)**.
    *   **Queue Dynamics:** Monitored through **Buffer Status Report (BSR)** evolution over time and post-processed using **gnb console logs** packet analysis.
    *   **Resource Fairness:** Quantified strictly using the standard **Jain's Fairness Index** to evaluate resource distribution equity.
## Network Setup & Experimental Testbed

The experimental network is configured as a **5G Standalone (SA) Private Network**. The deployment disaggregates the Control/User Plane and is divided into three main segments: the 5G Core Network, the Radio Access Network (gNodeB), and the User Equipments (UEs).

      SCENARIO A: MIXED CONDITIONS                          SCENARIO B: BOTH CELL-CENTER
      (Cell-Center vs. Cell-Edge)                             (Both in Good Conditions)

       +-----------------------+                             +-----------------------+
       |    5G CORE NETWORK    |                             |    5G CORE NETWORK    |
       |       (Open5GS)       |                             |       (Open5GS)       |
       +-----------+-----------+                             +-----------+-----------+
                   |                                                     |
                   | (S1 / NG-C, NG-U)                                   | (S1 / NG-C, NG-U)
                   |                                                     |
       +-----------+-----------+                             +-----------+-----------+
       | RADIO ACCESS NETWORK  |                             | RADIO ACCESS NETWORK  |
       |  srsRAN (OCUDU Fw)    |                             |  srsRAN (OCUDU Fw)    |
       |  Host PC + USRP B210  |                             |  Host PC + USRP B210  |
       +-----+-----------+-----+                             +-----+-----------+-----+
             |           |                                         |           |
       (RF Center)   (RF Edge)                               (RF Center)   (RF Center)
             |           |                                         |           |
       +-----+----+  +---+------+                            +-----+----+  +---+------+
       |  UE (Q1) |  |  UE (Q2) |                            |  UE (Q1) |  |  UE (Q2) |
       | Quectel  |  | Quectel  |                            | Quectel  |  | Quectel  |
       | (Center) |  |  (Edge)  |                            | (Center) |  | (Center) |
       +----------+  +----------+                            +----------+  +----------+


### 1. 5G Core Network (5GCN)
*   **Software Core:** **Open5GS**, an open-source implementation of the 5G Core.
*   **Configuration:** Configured with custom Network Slicing (S-NSSAI) and Dedicated APNs. Static routing and NAT are established between the host system and the containerized core. Configurations file are inside the __configuration__ folder.

### 2. Radio Access Network (gNodeB)
*   **SDR Frontend:** **Ettus USRP B210** transceiver connected via high-speed USB interface acting as the RF frontend.
*   **Protocol Stack:** **srsRAN** integrated within the **OCUDU framework**.
*   **Custom Tuning:** The `gnb.yaml` file (present in the __configuration__ folder) was modified to adapt PHY-layer parameters, physical resource blocks (PRBs), and scheduling policies (`scheduler_policy.h`) for multi-user testcases.

### 3. User Equipments (UEs) & Traffic Generation
*   **Devices under Test:** Commercial **Quectel 5G modules** equipped with custom lab SIM cards and connected directly to test laptops.
*   **Traffic Generator:** **iPerf3** is run on the client laptops via UDP mode to generate Uplink (UL) and Downlink (DL) traffic flows.
*   **Performance Tracking:** 
    *   **PCAP Logging:** Packet captures (PCAP) are recorded on the gNodeB host PC via Wireshark to accurately estimate throughput.
    *   **Metrics Extraction:** Real-time JSON output metrics are streamed via WebSocket and parsed using **Python and Pandas** to compare the performance profiles of the selected scheduling algorithms.
## Data Generation & PCAP Capturing

To evaluate the scheduling performance of each algorithm under realistic conditions, we generate controlled traffic and capture raw packet data directly at the gNodeB interface. This allows us to perform diagnostics of throughput and packet queues.

### 1. Synthetic Traffic Generation (iPerf3)
*   **Traffic Engine:** We utilize **iPerf3** to generate continuous, bidirectional TCP/UDP traffic flows between the client laptops (connected to the Quectel 5G UEs) and the 5G Core Network.
*   **Test Scenarios:** 
    *   **Uplink (UL) Stress Testing:** Simulating high-demand data uploads to analyze queue growth in the Buffer Status Reports (BSR).
    *   **Downlink (DL) Stress Testing:** Simulating massive streaming/downloads to evaluate how resource blocks are distributed among multiple users under different policies.

### 2. Packet Capture (PCAP) on the gNodeB Host

*   **Capture Mechanism:** Wireshark/Tshark is run on the gNodeB host to sniff and save the exact arrival and departure times of packet headers. This happens automatically, if not is required to run the __gnb__ file as administrator. By default the file is saved in the temp folder
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
### 1. Throughput & CDF (Cumulative Distribution Function) Computation
To evaluate how effectively each scheduling policy distributes resources, the Python pipeline calculates and plots the Cumulative Distribution Function (CDF) of the throughput:
*   **Sliding Window Extraction:** Packets are grouped by their RNTI (`mac-nr.rnti`) and direction (`mac-nr.direction`). The throughput \\(R_i(t)\\) for each user \\(i\\) is calculated over a sliding time window (e.g., \\(100\text{ ms}\\) or \\(1\text{ s}\\)) using the packet lengths.
*   **Empirical CDF Plotting:** The script computes the CDF of these throughput values. This allows us to easily extract and compare:
    *   **Average/Peak Throughput:** The median (50th percentile) and peak (95th percentile) performance.
    *   **Cell-Edge Robustness:** The 5th percentile, which mathematically represents the worst-performing scenario. A higher 5th percentile indicates that the scheduler successfully prevents starvation for users in degraded signal conditions (Cell-Edge).

### 2. BSR Queue Evolution & Transient Analysis
The Buffer Status Report (BSR) values (ranging from 0 to 255) extracted via `mac-nr.control.bsr.bs-lcg2` are plotted chronologically to visualize MAC-layer queue dynamics:
*   **Queue Depth Tracking:** The script tracks how the buffer size fluctuates over time. This maps directly to the `pending_bytes` parameter in our modified srsRAN scheduler logic.

### 3. Quantitative Fairness Evaluation
Using the final throughput arrays calculated for each active User Equipment (UE), the script computes the **Jain's Fairness Index (JFI)** to mathematically quantify resource equity:
$$J(x_1, x_2, \dots, x_n) = \frac{\left( \sum_{i=1}^{n} x_i \right)^2}{n \sum_{i=1}^{n} x_i^2}$$

Where:
*   **$n$** is the number of active users (in our experimental setup, $n = 2$ for Quectel 1 and Quectel 2).
*   **$x_i$** represents the throughput (in Mbps) obtained by the $i$-th User Equipment.

#### Interpretation of the Index:
*   **$J = 1.0$**: **Perfect Fairness**. Resource allocation is completely equal ($x_1 = x_2$).
*   **$J = 1/n$ ($0.50$ for 2 UEs)**: **Worst-case Fairness (Starvation)**. One user receives all the resources while the other receives near-zero. This is highly visible in our *Max Throughput* scheduler tests under Low SNR conditions, where the index drops to **$0.528$** in Uplink and **$0.502$** in Downlink.

## CDF graphic result 
![alt text](https://github.com/Nibbio5/Mac-scheduling-analysis-on-OCUDU/blob/main/graphics_generated/cdf_median_uplink_bad_qos.png)

## Scheduling Algorithms & Code Implementation

Within the **OCUDU framework**, the gNodeB scheduler is responsible for distributing Physical Resource Blocks (PRBs) to active User Equipments (UEs) in every Transmission Time Interval (TTI). 

This project evaluates and compares four distinct scheduling policies, highlighting the fundamental trade-off between total cell capacity and user fairness:

### 1. Implemented Scheduling Policies

*   **Round Robin (RR) — *Focus: Fairness***  
    An algorithm that allocates radio resources sequentially and equally among all active UEs, regardless of their channel conditions. It ensures maximum resource equity (Jain's Fairness Index close to $1.0$) but suffers from severe **spectral inefficiency** in mixed channel scenarios (mixed Cell-Center/Cell-Edge).
*   **Maximum Throughput (MAX) — *Focus: System Capacity***  
    A channel-aware policy that prioritizes the UE with the highest instantaneous Signal-to-Noise Ratio (SNR) and Channel Quality Indicator (CQI). While maximizing the cumulative cell throughput, it completely ignores disadvantaged users, causing total resource **starvation** for Cell-Edge devices.
*   **Proportional Fair (PF) — *Focus: Trade-off Balance***  
    An algorithm designed to balance system throughput and fairness. It assigns resource grants by computing the ratio between the instantaneous supportable rate $R_i(t)$ (derived from CQI) and the historical average throughput $\bar{R}_i(t)$ of each user, offering an elegant compromise.
*   **QoS-Aware Scheduling — *Focus: Queue Management***  
    An advanced policy based on Proportional Fair that dynamically adjusts priorities according to the traffic class and buffer requirements. It actively monitors buffer occupancy (Buffer Status Reports) to prioritize users with accumulating data.

---

### 2. srsRAN & OCUDU Code Integration

All scheduling policies in our gNodeB are integrated into the protocol stack by implementing the unified **`scheduler_policy`** C++ interface:

*   **Policy Files (`lib/scheduler/policy`):** Header and implementation files specify how priorities are computed [8]. Any active policy is forced to implement the virtual methods defined in `scheduler_policy.h`:
    *   `add_ue()` / `rem_ue()`: To register and clean up active devices.
    *   `compute_ue_dl_priorities()` / `compute_ue_ul_priorities()`: Executed dynamically to calculate the `ue_sched_priority` (as a `double` score) for each UE in queue, checking the `ue_newtx_candidate` struct and its `pending_bytes`.
    *   `save_dl_newtx_grants()` / `save_ul_newtx_grants()`: Used to feedback the allocated resources to the scheduler, allowing average historical throughput tracking ($\bar{R}_i$).
*   **Policy Registry (`scheduler_policy_factory.cpp`):**  
    While OCUDU natively provided the *Round Robin* and *Quality of Service* schedulers, **we successfully expanded the framework** by implementing and registering both a **Pure Proportional Fair** policy and a **Max Throughput** policy. This was achieved through target modifications of the QoS-scheduler codebase to re-configure priority calculations based on CQI and throughput states.


## Experimental Results & Performance Tables

Below are the detailed experimental results and statistics obtained from the physical 5G Standalone network under different scheduling policies (Round Robin, QoS-Aware, Proportional Fair, and Max Throughput).

### 1. Throughput & Fairness Evaluation: High SNR Scenario
This scenario represents optimal channel quality where both UEs are located near the cell center (high SNR, CQI 13–15). It tests the maximum cell capacity and balanced scheduling behavior.

| Algorithm | UL UE 1 (Mbps) | UL UE 2 (Mbps) | JFI (UL) | DL UE 1 (Mbps) | DL UE 2 (Mbps) | JFI (DL) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **QoS-aware** | 13.15 | 13.15 | 1.000 | 29.25 | 29.25 | 1.000 |
| **Round Robin (RR)** | 12.73 | 10.94 | 0.994 | 30.22 | 28.05 | 0.998 |
| **Proportional Fair (PF)** | 8.39 | 9.31 | 0.997 | 29.17 | 20.20 | 0.967 |
| **Max Throughput (MAX)** | 24.58 | 0.32 | 0.536 | 29.24 | 29.25 | 1.000 |

### 2. Throughput & Fairness Evaluation: Low SNR / Cell-Edge Scenario
In this scenario, UE 2 was moved far from the gNodeB to simulate a degraded, Cell-Edge link (low SNR, CQI 7–9), evaluating how well the policies prevent starvation for disadvantaged users.

| Algorithm | UL UE 1 (Mbps) | UL UE 2 (Mbps) | JFI (UL) | DL UE 1 (Mbps) | DL UE 2 (Mbps) | JFI (DL) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **QoS-aware** | 10.92 | 5.64 | 0.908 | 20.49 | 10.09 | 0.895 |
| **Round Robin (RR)** | 11.46 | 8.62 | 0.980 | 30.14 | 9.09 | 0.772 |
| **Proportional Fair (PF)** | 14.28 | 4.26 | 0.725 | 30.22 | 6.55 | 0.699 |
| **Max Throughput (MAX)** | 23.02 | 0.60 | 0.528 | 58.21 | 0.03 | 0.502 |

### 3. MAC-Layer Buffer Analytics (BSR Statistics)
This table summarizes the total BSR control element samples and the average queue size (in bytes) waiting in the devices' transmission buffers during the respective scenarios.

| Algorithm & Scenario | UE 1 Samples | UE 1 Avg BSR (Bytes) | UE 2 Samples | UE 2 Avg BSR (Bytes) |
| :--- | :---: | :---: | :---: | :---: |
| **MAX Throughput (High SNR)** | 286 | 665,901.40 | 286 | 3,424.50 |
| **Proportional Fair (High SNR)** | 296 | 44,194.75 | 295 | 46,045.95 |
| **QoS-Aware (High SNR)** | 275 | 286,528.40 | 275 | 233,068.00 |
| **Round Robin (High SNR)** | 296 | 143,821.60 | 297 | 153,464.00 |
| **Round Robin (Low SNR)** | 308 | 150,559.10 | 308 | 85,559.10 |
| **QoS-Aware (Low SNR)** | 294 | 76,564.40 | 294 | 39,220.40 |
| **MAX Throughput (Low SNR)** | 305 | 559,610.50 | 308 | 5,128.10 |
| **Proportional Fair (Low SNR)** | 296 | 89,974.10 | 295 | 18,332.70 |


