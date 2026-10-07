# R36 MAX 2 Hardware Monitor

**用一台低成本掌機，隨時查看多台電腦的硬體狀態。**

把 R36 MAX 2 變成桌上的獨立監控螢幕，透過 MQTT 顯示 CPU、GPU、VRAM、記憶體、網路、磁碟與溫度。保留原本的遊戲選單，從 **Ports → Hardware Monitor** 就能進入監控。

## 實機畫面

以下為 R36 MAX 2 上擷取的實際畫面，解析度為 1024 × 768。

### 三台電腦，一眼看懂

總覽每頁最多三台；更多電腦以分頁呈現。可以自動輪播，也能用按鍵選取一台查看詳細資訊。

![三台電腦的硬體監控總覽](browser/comic-overview-tested.png)

### 單台詳細頁，大字查看主要指標

所有監控頁面的右上角都有固定的 R36 本機狀態列，顯示掌機 SoC 溫度、CPU 使用率、記憶體使用率和電池電量，每兩秒更新。這些讀值來自掌機本身，與 MQTT 電腦資料分開；充電中顯示閃電，充滿但仍接著電源時顯示插頭。無法取得的資料顯示 `—`。

單台主機的第一層詳細頁以約 50 公分的桌面觀看距離為設計目標：CPU、記憶體使用率採 64 px 大字，網路接收／傳送與磁碟讀取／寫入流量採 48 px 大字，同屏顯示，不需要上下捲動。GPU 有幾張就列出幾張使用率與 VRAM；字級依數量調整，兩張 GPU 時使用率為 44 px，更多 GPU 的完整資訊可進入 GPU 單項頁查看。

第一層保留簡單使用量條、VRAM 和記憶體容量，核心明細、裝置清單與趨勢圖放在單項詳細頁。溫度和趨勢圖可從底部入口開啟；實際可讀性仍取決於亮度與使用者視力。

![大字顯示 CPU、GPU、記憶體與網路、磁碟流量](browser/comic-detail-tested.png)

### 點開 CPU 或 GPU，查看單項圖形資訊

在設備詳細頁用方向鍵選擇資訊卡，按 A 開啟單項詳細頁。也可以點擊卡片。CPU 顯示整體負載、最忙四核心與溫度趨勢；GPU 逐張顯示負載、VRAM 和趨勢圖。記憶體、網路、磁碟、溫度與活動趨勢同樣可以各自開啟。

![CPU 單項詳細頁的圖形化負載與趨勢](browser/comic-cpu-tested.png)

![GPU 單項詳細頁的負載、VRAM 與趨勢](browser/comic-gpu-tested.png)

單項頁仍採整屏版面，使用 L1／R1 切換資訊類別，按 B 返回設備詳細頁，再按 B 返回總覽。單項頁的標題、主要數值與圖表一併放大。GPU 每頁顯示兩張；網路、磁碟和溫度每頁顯示四個項目，上下方向鍵或類比搖桿切換項目頁，也可以按畫面上的箭頭。全部項目均可查看，網路與磁碟總量仍包含全部裝置。

### 遊戲選單裡的固定入口

笑臉晶片圖示讓監控入口容易辨認。退出監控後，回到原本的遊戲選單。

![Ports 選單中的硬體監控圖示](browser/ports-icon-tested.png)

## 低成本的價值

需要的顯示設備就是一台 R36 MAX 2、系統 SD 卡和電源。如果手邊已經有掌機，就能沿用螢幕、實體按鍵與 Wi-Fi，把它放在桌邊查看電腦狀態。

採集程式在被監控電腦上執行，掌機負責接收與顯示。已有 MQTT broker 的使用者可以直接接上原本的資料流；這份專案不要求另建一套 broker。

漫畫風的晶片角色、色塊儀表和使用量條，讓資訊容易辨識。監控開啟期間保持常亮、阻止閒置休眠，並從啟動時隱藏滑鼠游標，全程使用掌機按鍵操作。

## 按鍵操作

兩支類比搖桿皆可使用，具有中心死區，長推會連續移動。斜推依偏移較大的方向移動。

| 按鍵 | 操作 |
| --- | --- |
| 方向鍵／左右類比搖桿 | 上下選取電腦，左右翻頁；設備詳細頁依卡片位置四方向選取；單項頁左右切換類別、上下切換項目頁 |
| A | 進入設備詳細頁，再進入選定資訊卡的單項頁；輪播保持暫停 |
| B | 逐層返回，保持暫停 |
| L1／R1 | 前後翻頁；單項頁中切換資訊類別；輪播保持暫停 |
| Start | 在總覽暫停或恢復輪播 |
| Select + B | 退出監控，回到遊戲選單 |

自動輪播每 15 秒換頁。手動操作後，只有按 Start 才恢復輪播。主機 10 秒未傳來資料便移除；若正在查看該主機，畫面會回到總覽。趨勢圖保留最近 60 次資料更新。

## 資料串接

```text
被監控電腦上的 Agent → MQTT broker → R36 MAX 2 監控畫面
```

本專案相容 [hwmonitor-mqtt](https://github.com/jhihweijhan/hwmonitor-mqtt) 的資料格式，預設訂閱 `sys/agents/+/metrics`。每台電腦使用不同的 `host` 名稱，掌機就會自動建立對應項目。

先依 [hwmonitor-mqtt 的安裝說明](https://github.com/jhihweijhan/hwmonitor-mqtt#快速開始) 設定 Linux 或 Windows 採集端與 broker。掌機上的 Python 程式接收 MQTT，再把資料送給本機瀏覽器；broker 不需要支援 WebSocket。

## 安裝到掌機

目前交付的是**顯示端原始碼與啟動腳本**，不包含整合完成的刷機映像。以下步驟用於已安裝 dArkOS4Clone、可透過 SSH 登入的 R36 MAX 2，帳號為 `ark`。系統安装請參考 [(d)ArkOS4Clone](https://github.com/lcdyk0517/arkos4clone) 的 R36Max2 文件。

實機環境為 Debian 13 ARM64、Chromium、Xorg modesetting 與 Python 3。其他 R36 型號與原廠系統尚未驗證；遊戲選單路徑與按鍵代碼可能不同。

### 1. 安裝依賴並下載程式

在掌機的 SSH 終端執行：

```bash
sudo apt update
sudo apt install --no-install-recommends git chromium xserver-xorg-core xinit x11-xserver-utils python3-paho-mqtt
sudo loginctl enable-linger ark
git clone https://github.com/KarlSideProjects/r36max2-hwmonitor.git
cd r36max2-hwmonitor
mkdir -p /home/ark/device-browser/assets /home/ark/device-browser/lib
cp browser/*.py browser/*.html browser/*.sh browser/xorg.conf /home/ark/device-browser/
cp browser/assets/hardware-buddy.svg /home/ark/device-browser/assets/
chmod +x /home/ark/device-browser/*.sh
```

`enable-linger` 讓系統開機後保留 `ark` 的使用者執行環境。否則退出 SSH 後，`/run/user/1000` 可能被移除，監控入口會因無權建立該目錄而退回遊戲選單。

如果遊戲選單載入較多內容，與 Chromium 同時執行可能造成記憶體不足、網頁崩潰。這台 dArkOS4Clone 已提供 512 MB ZRAM 服務，可啟用壓縮交換記憶體並設為開機啟動：

```bash
sudo sed -i 's/^ENABLED=0$/ENABLED=1/' /etc/zram.conf
sudo systemctl enable --now zram-swap.service
cat /proc/swaps
```

確認輸出包含 `/dev/zram0`。上述操作使用系統內建設定，適用於已有 `/etc/zram.conf` 與 `zram-swap.service` 的映像。

### 2. 準備瀏覽器專用圖形函式庫

這台 dArkOS4Clone 的 Mali `libgbm` 無法直接供 Chromium 使用。瀏覽器使用獨立的 Debian `libgbm`，放在應用程式目錄，不替換遊戲系統的函式庫。

```bash
mkdir -p /tmp/hardware-monitor-gbm
cd /tmp/hardware-monitor-gbm
apt download libgbm1:arm64
dpkg-deb -x ./libgbm1_*_arm64.deb extracted
cp -L extracted/usr/lib/aarch64-linux-gnu/libgbm.so.1 /home/ark/device-browser/lib/libgbm.so.1
```

### 3. 設定 MQTT

回到下載的專案目錄，建立本機設定：

```bash
cd ~/r36max2-hwmonitor
install -m 600 browser/mqtt-config.example.json /home/ark/device-browser/mqtt-config.json
nano /home/ark/device-browser/mqtt-config.json
```

依照自己的 broker 填入位址、埠號與帳密：

```json
{
  "host": "YOUR_BROKER_HOST",
  "port": 1883,
  "topic": "sys/agents/+/metrics",
  "username": "YOUR_MQTT_USERNAME",
  "password": "YOUR_MQTT_PASSWORD",
  "tls": false
}
```

broker 使用 TLS 時將 `tls` 設成 `true`，並填入對應埠號。匿名 broker 可把 `username` 與 `password` 留空。實際設定與帳密不放進 Git；`MQTT_CONFIG` 環境變數可指定其他設定檔。

### 4. 加入 Ports 選單

先退出正在執行的監控或遊戲，再於 SSH 終端執行：

```bash
cd ~/r36max2-hwmonitor
sudo systemctl stop emulationstation
mkdir -p /roms/ports/images
cp 'browser/Hardware Monitor.sh' 'browser/Device Info.sh' /roms/ports/
chmod +x '/roms/ports/Hardware Monitor.sh' '/roms/ports/Device Info.sh'
cp browser/assets/hardware-buddy.png /roms/ports/images/
python3 browser/install-menu.py
sudo systemctl start emulationstation
```

選取 **Ports → Hardware Monitor**，收到資料後即可看到電腦。`Device Info` 則用於查看掌機本身的系統狀態。

## 驗證與限制

2026-10-07 已在 R36 MAX 2 上接收三台電腦的真實資料，驗證總覽、詳細頁、按鍵操作、常亮及退出後回到遊戲選單。程式測試涵蓋七台主機分頁；版面測試涵蓋零、兩、四張 GPU，以及 1024 × 768 下沒有捲動或裁切。

GPU、VRAM 與溫度等資訊取決於採集端回報內容。缺少資料時以橫線標示，不以零值代替。更多主機的實機顯示，以及其他掌機型號，仍需各自驗證。

在開發電腦執行基本測試，Python 測試不需要連接 MQTT broker：

```bash
python3 browser/test_monitor.py
python3 browser/test_monitor_events.py
python3 browser/test_menu.py
python3 browser/test_device_info.py
node browser/test_monitor_ui.cjs
bash -n browser/client.sh browser/xserver.sh 'browser/Hardware Monitor.sh'
```

版面測試需要 Node.js 與 Playwright，可執行 `node browser/test_monitor_layout.cjs`。在已開啟監控的掌機上，`measure_startup.py`、`measure_input.py` 與 `test_awake.py` 分別检查啟動等待、按鍵到畫面的延遲，以及常亮設定。

## 授權與相關專案

程式碼採用 [GNU GPL v3](LICENSE)。本專案連接 [hwmonitor-mqtt](https://github.com/jhihweijhan/hwmonitor-mqtt) 的監控資料，掌機系統來自 [(d)ArkOS4Clone](https://github.com/lcdyk0517/arkos4clone)。

漫畫晶片圖示與監控頁面原始碼位於 [browser/assets](browser/assets) 與 [browser/monitor.html](browser/monitor.html)。Ports 截圖中的 EmulationStation 介面使用 [es-theme-switch](https://github.com/Jetup13/es-theme-switch)，其第三方元件依原專案授權；本儲存庫不包含完整遊戲系統或其二進位套件。
