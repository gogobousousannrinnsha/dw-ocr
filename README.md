# DW-OCR Portable v0.2.0

Windows x64向けの、Python・OCRライブラリ・PP-OCRv6 mediumモデルを含む実行環境です。**v0.2.0はPre-release（試験的リリース）**です。Core 1.0.0 / Integrations 0.6.0を使用します。

## ダウンロードと最初の実行

[v0.2.0 Release](https://github.com/gogobousousannrinnsha/dw-ocr/releases/tag/v0.2.0)から、`ocr_join_tools.zip`と`ocr_part_001_transport.zip`～`ocr_part_008_transport.zip`の全9ファイルを、旧版と別の空フォルダーへ取得します。

1. 結合ツールZIPだけを展開し、中のBAT・PowerShell・manifestを8個のtransport ZIPと同じ階層へ置きます。
2. `join_parts.bat`を実行し、成功表示を確認します。transport ZIPは個別に展開する必要はありません。
3. 復元された`dw_ocr_with_code.zip`を、新しい書込み可能な短いフォルダーへ展開します。
4. `verify_environment.bat`で環境を確認します。
5. 試験用XDWのコピーを`INPUT`へ置き、`OCR開始.bat`を実行します。XDW・フォルダーの複数ドロップにも対応します。

GitHubの「Source code」ZIPと`dw-ocr-source-v0.2.0.zip`はソースです。Python・GPUライブラリ・モデルを含むPortableとは異なります。分割ファイルと結合ツールは同じReleaseのものだけを組み合わせてください。

## 機能

- 文書単位で全ページをOCRし、認識領域の矩形付きXDWと確認画像を作成します。原本は変更しません。
- `settings.ini`で再帰探索、300/600dpi、信頼度、矩形色・余白、日本語フォント、JSONL出力を設定できます。
- 結果は`OUTPUT/job-.../doc-.../`、再利用できるOCR結果は`runs/job-.../doc-.../`に保存します。
- 保存runから矩形・確認画像・JSONLを再生成できます。文字や色の確認のたびにOCRをやり直す必要はありません。
- 旧入口と旧runの利用を継続できます。新しい出力先を使い、run内部は直接編集しません。

既定は300dpi、INPUT直下のみ、赤い矩形、JSONLなしです。停止後にアプリ全体をまとめて移動できます。

## 必要環境と説明書

Windows x64、正規のDocuWorks製品と対応x64 XDWAPI、CUDA対応NVIDIA GPU・ドライバー、日本語フォントが必要です。Pythonは同梱されます。15～20GB以上の空き容量に、OCR成果物の保存分を追加してください。GPU OCRにCPUへの自動切替はありません。

[復元・実行](docs/INSTALL_RESTORE.md) / [設定・API](docs/UNIFIED_0.6.0.md) / [移行](docs/MIGRATION_v0.2.0.md) / [ソース導入・ビルド](docs/SETUP.md) / [配布一覧](docs/DISTRIBUTION_FILES.md) / [検証](docs/VERIFICATION.md) / [制約](docs/KNOWN_LIMITATIONS.md)

確認画像は組版の再現や校正結果ではありません。XDWの検索用OCRテキスト層を埋め込む機能ではありません。認識文字・矩形位置は利用者が確認してください。

## ライセンス

独自部分は[MIT](LICENSE)、第三者資産はそれぞれの条件です。[適用範囲](LICENSE_NOTICE.md) / [第三者資産・対応ソース](THIRD_PARTY_NOTICES.md)。DocuWorks製品・SDK・DLL、GPUドライバー、Windowsフォントは同梱しません。本ツールは非公式で、現状有姿で提供します。

[Issues](https://github.com/gogobousousannrinnsha/dw-ocr/issues)には、版と匿名化した再現手順を記載してください。実文書・OCR本文・個人パス・資格情報は掲載しないでください。
