# DW-OCR Portable v0.3.0

**Pre-release / 試験的リリース**。Core 1.0.0 / Integrations 0.7.0。旧版を残し、新規フォルダーへ展開してください。

`ocr_join_tools.zip`と`ocr_part_001_transport.zip`〜`ocr_part_008_transport.zip`を同じ空フォルダーへ保存し、結合ツールを展開して既存の`join_parts.bat`で復元します。
完成ZIPは3,223,823,853 bytes、SHA-256 `3a26d3c3d5c45f370e2a6a38e93b472a773a7880566aec7d0943c11ca83d61d6`。別版の同名部品を混ぜないでください。

保存済みOCRの文字訂正を別JSONへ保存・適用し、訂正後JSONLへ出力するPython APIと、1ページの指定領域を確認用XDWで訂正して取り込むPython APIを追加しました。
訂正対象の識別には領域情報を使い、文字列や位置で推測しません。元run・座標・信頼度を保持します。
通常のOCR操作へ訂正機能を自動組込みしていません。既存のOCR・矩形・確認画像・元結果JSONLは従来どおりです。

SDK往復と既存Viewer保存文書の再取り込み、通常pip導入、未加工sdist、同梱PythonのGPU OCR、移動後利用、旧run・旧入口を確認しました。検証条件・未確認範囲は`VERIFICATION_JA.md`を参照してください。
Windows x64、対応DocuWorksとx64 XDWAPI、NVIDIA GPUと対応ドライバーが必要です。CPU自動切替はありません。
独自部分はMIT、第三者資産は各条件です。第三者対応ソースは変更していないため`third-party-sources-v0.1.0.zip`を維持します。

[機能・API・移行手順](https://github.com/gogobousousannrinnsha/dw-ocr/tree/v0.3.0)
