# 必要環境

Windows x64、利用権のあるDocuWorks製品と対応x64 XDWAPI、CUDA対応NVIDIA GPU・ドライバー、日本語フォント、書込み可能な短い配置先が必要です。配布物・復元ZIP・展開先に15～20GB以上とOCR成果物分の空き容量を確保します。

Portable同梱基準はPython 3.13.15、Paddle GPU 3.2.2、CUDA 12.9、cuDNN 9.9.0.52、PaddleOCR 3.7.0、PaddleX 3.7.2、Pillow 12.3.0、PP-OCRv6 medium det/rec、Core 1.0.0、Integrations 0.6.0です。CUDAランタイムは同梱されるため、CUDA Toolkit一式を手動導入することから始める必要はありません。対応ドライバーは別途必要です。

ソースから実行する場合は[SETUP](SETUP.md)に従います。CoreのPython互換性の記録とGPU OCRの実測基準を区別してください。標準GPU OCRにCPUの自動代替はありません。
