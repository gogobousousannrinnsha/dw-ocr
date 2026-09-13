# docuworks-integrations 0.7.0

同じページの領域IDを複数指定する確認用XDWに対応しました。
[複数領域APIと検証範囲](../../docs/REVIEW_XDW_REGIONS_0.7.0.md)。複数領域はSDK往復に加え、同じ文字を持つ2領域の片方だけをViewer編集・別名保存後に取り込む正常1ケースを検証済みです。
Viewerの操作・再表示は利用者報告、保存ファイルの照合とJSONL反映はコード検証です。複数領域のViewer異常操作は未確認です。

1ページ・1領域の確認用XDWの生成と訂正候補の読取りを追加しました。
[API仕様](../../docs/REVIEW_XDW_0.7.0.md) ／ [SDK・Viewer検証記録](../../docs/REVIEW_XDW_VERIFICATION.md)。
形式1.0の1ページ・1領域の原本重ね合わせ型についても、SDK往復とViewer編集・別名保存後の取り込みを検証済みです。白紙型は対象外です。

Pythonから保存済みOCR文字を別JSONで訂正し、元bundleを保ったまま修正後JSONLを生成できます。
使用例・保存形式・例外は [文字訂正基盤](../../docs/CORRECTIONS_0.7.0.md) を参照してください。
Core、既存CLI、Portableの動作は維持しています。

## 0.6.0 統合機能

保存結果を使うannotate-rectanglesとrender-text-maps、複数入力をまとめるprocess-documentsを追加しました。矩形は塗りなし・1ptで保存と再オープンを検証します。OCR bundleは保持し、派生成果物は別ディレクトリへ保存します。各CLIの--helpで引数を確認できます。

## 0.5.0 フォルダOCR

ocr-folder --input-dir ... --batch-dir ... --model-root ... を追加しました。通常は直下、--recursiveでサブフォルダも含め、各XDWの全ページを独立runに保存します。既知の文書エラーは記録して継続し、GPU等の共通障害は停止します。操作・API・失敗の詳細はSETUP_PYTHON313.mdを参照してください。

## 0.4.0 複数ページOCR

--all-pages / --pages 1,3-5 を追加。新規結果は形式1.1、検出0件は正常な空ページとして保存します。旧1.0読込みは維持します。

## 0.3.0 OCR結果の分離

OCR実行、版管理されたOCR結果、保存結果の利用を分離したDocuWorks連携ライブラリです。

- Recognition：XDWの全ページまたは指定ページを300/600dpiで画像化し、PP-OCRv6 mediumで認識。
- Results：Rawとは別に、文字列・px/mm座標・ページ情報・固定IDをJSONで保存。
- Consumers：保存結果からマーカーまたはJSONLを生成。OCRを再実行しません。

導入とCLIはSETUP_PYTHON313.md、保存形式とPython APIはOCR_RESULT_FORMAT.mdを参照してください。
Core 1.0.0を維持し、実行検証基準はWindows x64 / Python 3.13.15です。
OCR環境はPaddle GPU 3.2.2 CUDA 12.9、PaddleOCR 3.7.0、PaddleX 3.7.2です。

既存OcrRegion、OcrEngine、JsonOcrEngine、注釈APIは維持しています。
workflow.ocr_xdwとworkflow.mark_regionは0.2.0形式用のPython互換APIとして残ります。
新規コードはrecognition.ocr_xdwとconsumers.mark_regionを使います。
CLIのocr-xdwは0.3.0からmanifest.jsonを持つ新形式を出力します。
元文書は変更せず、新規XDWへ保存して再オープン検証します。Viewer確認は別記録です。


> 集約版の運用入口: [README](../../README.md)。試験件数・既知不具合・Viewer確認範囲は[検証記録](../../docs/VERIFICATION.md)を正としてください。
