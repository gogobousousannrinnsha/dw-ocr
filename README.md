# DW-OCR Portable v0.3.0

**Pre-release / 試験的リリース**。Core 1.0.0 / Integrations 0.7.0 / Python 3.13.15。

[v0.3.0の配布](https://github.com/gogobousousannrinnsha/dw-ocr/releases/tag/v0.3.0)から、結合ツールと全8個のtransport ZIPを同じ空フォルダーへ取得します。
結合ツールを展開してjoin_parts.batを実行し、復元したZIPを新規フォルダーへ展開してください。旧版と既存データは残してください。
INPUTにXDWのコピーを入れ、既存のOCR開始.batを実行します。複数ファイル・フォルダーのドロップにも対応します。

## 0.7.0で追加した機能

保存済みOCRの文字を別JSONへ訂正保存し、元runを保ったまま訂正後JSONLを出力できます。
同じページの指定領域を原本重ね合わせ型の確認用XDWへ出し、編集・別保存した文字を領域IDに対応付けて取り込めます。
同じ文字の領域同士を、文字列や表示位置で推測して対応付けることはありません。

**訂正・確認用XDWはPython APIです。通常のOCR開始操作へ自動組込みする機能ではありません。**
既存の矩形・確認画像・元結果JSONLの動作は維持します。訂正後のJSONLにはexport_effective_jsonlを使用します。

- [0.7.0の機能・検証](docs/RELEASE_0.7.0.md)
- [文字訂正API](docs/CORRECTIONS_0.7.0.md) / [使用例](examples/correct_saved_ocr.py)
- [1領域レビュー](docs/REVIEW_XDW_0.7.0.md) / [複数領域レビュー](docs/REVIEW_XDW_REGIONS_0.7.0.md)
- [複数領域の使用例](examples/use_review_xdw_regions.py)
- [移行手順](docs/MIGRATION_v0.3.0.md) / [検証条件](docs/VERIFICATION_v0.3.0.md)
- [既存OCR操作](docs/UNIFIED_0.6.0.md)

白紙型、複数ページ確認XDW、検索、テンプレート、再OCR、領域の追加・削除・分割・結合は未対応です。
Viewerの1領域6ケース・複数領域の正常1ケースの利用者確認を継承し、今回の配布環境でも保存済み文書を再取り込みします。
複数領域のViewer異常操作は未確認です。既知のMarker 13pt編集問題は別の未解決課題です。

Windows x64、対応DocuWorks・x64 XDWAPI、NVIDIA GPUと対応ドライバーが必要です。CPU自動切替はありません。
同梱のモデル・第三者実行環境はv0.2.0の組合せを維持しています。

独自部分はMIT、第三者資産は各条件です。[適用範囲](LICENSE_NOTICE.md) / [第三者表示と対応ソース](THIRD_PARTY_NOTICES.md)。
DocuWorks製品・SDK・DLL、GPUドライバー、Windowsフォント、実文書、OCR本文、個人設定は同梱しません。
報告には匿名化した再現手順を使い、実文書・OCR本文・個人パス・資格情報を掲載しないでください。
