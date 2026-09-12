# DW-OCR Portable v0.2.0

**Pre-release / 試験的リリース**。Core 1.0.0 / Integrations 0.6.0。v0.1.0を残し、新しいフォルダーへ展開して使用してください。

## ダウンロード

`ocr_join_tools.zip`と`ocr_part_001_transport.zip`～`ocr_part_008_transport.zip`の全9ファイルを同じ空フォルダーへ保存します。結合ツールだけ展開して`join_parts.bat`を実行し、復元ZIPを新規フォルダーへ展開します。`verify_environment.bat`で確認後、INPUTへ文書コピーを入れ`OCR開始.bat`を実行してください。

復元ZIP: 3,223,574,617 bytes、SHA-256:

```text
551c190d18bc323c499bfec4b3e21e735891588743384e322733fc639fda577d
```

個別ファイルは`release-assets.json`と`SHA256SUMS_ASSETS.txt`で照合できます。別版の同名ファイルを混ぜないでください。第三者対応ソースは内容を維持した`third-party-sources-v0.1.0.zip`です。GitHubのSource codeと`dw-ocr-source-v0.2.0.zip`にPortableの実行環境は含まれません。

## 変更点

- INPUT／複数ドロップから全ページOCR→矩形→確認画像→任意JSONLを共通処理で実行します。
- settings.iniで再帰探索・300/600dpi・信頼度・矩形・フォント・JSONLを設定できます。
- 文書単位のOCR結果をrunsへ保持し、OUTPUTに派生物を保存します。保存runから再OCRなしで矩形・確認画像・JSONLを作成できます。
- 旧入口を共通処理に統合しました。公開準備で見つかった旧BAT2本のPython存在確認の誤りも修正しました。
- Core・Integrationsのビルド可能な公開ソース、依存一覧、モデル照合ツール、移行・API説明を揃えました。GPU実行環境・モデルは従来の組合せを維持しています。

## 移行と検証

旧settings.iniを丸ごとコピーせず、新版に必要な値を移してください。旧runは独立して利用でき、自動結合しません。新しい出力先が必要です。旧版を残すことで戻して使用できます。

最終配布物の再結合、同梱PythonによるGPU OCR、破損文書後の継続、移動後利用、旧入口と旧run、Viewer確認を実施しました。詳細と限界は`VERIFICATION_JA.md`を参照してください。

Windows x64、正規DocuWorks・対応x64 XDWAPI、NVIDIA GPU・ドライバー、日本語フォントが必要です。CPU自動切替はありません。Markerの13pt問題は未解決です。認識文字・位置を利用者が確認してください。独自部分はMIT、第三者部分は各条件です。

[使い方・移行・検証](https://github.com/gogobousousannrinnsha/dw-ocr/tree/v0.2.0)
