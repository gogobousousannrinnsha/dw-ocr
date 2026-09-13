# v0.1.0からv0.2.0への移行

旧アプリとデータを残し、新版を別フォルダーへ新規展開します。旧settings.iniをそのまま上書きせず、新版の設定項目へ必要な値を手作業で移してください。実行中にフォルダーを移動しないでください。

| 項目 | v0.1.0 | v0.2.0 |
|---|---|---|
| 基盤 | Core 1.0.0 / Integrations 0.3.0 | Core 1.0.0 / Integrations 0.6.0 |
| 標準入口 | ocr_rectangles.bat | OCR開始.bat、INPUT、複数ドロップ |
| 保存単位 | ページ別run | 文書の全処理ページを1run |
| 派生物 | 旧スクリプトの出力配置 | OUTPUTの文書別フォルダー |
| OCR結果 | スクリプト設定に依存 | runsへ常に保持 |
| 確認画像上書き | 旧入口で対応 | --overwriteを拒否し新規出力を要求 |

旧`ocr_rectangles.bat`は共通処理へつなぐ互換入口として残します。出力指定を維持し、共通jobも保存します。`text_maps.bat`の既定出力はrunの隣の`<run名>-text-maps`です。

Result 1.0/1.1と旧runの読込みを維持します。旧ページ別runの自動結合は行いません。明示的な変換例は次のとおりです。Portableのルートから実行し、パスは実際の保存先へ置き換えてください。

```powershell
.\runtime\python.exe -I -X utf8 -m docuworks_integrations convert-ocr-run --run-dir D:\old-run --output-dir D:\converted-run
.\runtime\python.exe -I -X utf8 -m docuworks_integrations export-ocr --run-dir D:\converted-run --format jsonl --output D:\regions.jsonl
```

変換・JSONLはOCR・SDK不要です。変換元は残します。新しい矩形consumerはrun内の原本コピーを利用します。外部原本指定はハッシュ一致が必要です。既存mark-regionの原本照合契約は変わりません。

不具合時は新版の処理を停止し、残しておいたv0.1.0を使います。v0.2.0で作成したResult 1.1を旧readerへ戻すことはできないため、旧版の入力・runを保持してください。
