DW-OCR @RELEASE_VERSION@ / Integrations @INTEGRATIONS_VERSION@ / Core @CORE_VERSION@
Windows x64用Pre-releaseです。旧版と別の新しいフォルダーへ展開してください。

INPUTへXDWを入れてOCR開始.batを実行、またはXDW・フォルダーをドロップします。
全ページOCR、白紙Review、矩形付きXDW、確認画像をOUTPUTへ、元結果をrunsへ保存します。
設定はsettings.ini。詳細はdocs/user/README.md、全体の案内はdocs/README.mdです。
表示されたreview.xdwをViewerで編集・保存して閉じ、校正結果取込.batへドロップします。
校正後の文字・位置を別のReviewed ResultとJSONLへ保存します。取り込みは1文書ずつです。
取り込みはID照合中心の保存形式2.0です。付箋の作業メモは本文から除外し、保存済みXDWには残します。
ページ追加・削除・並べ替え・寸法変更・ページ回転は対象外で、自動検出を保証しません。
複数の原本参照の明示設定と旧形式互換はdocs/api/reviewed-import-v2.mdを参照してください。
校正後は、矩形テンプレートを登録・適用して項目を取得し、同じ登録テンプレートの結果をCSVへまとめられます。
登録・確認・適用・CSV出力はdocuworks-integrations.batを使用します。操作例はdocs/user/template-csv.mdです。
CSVはUTF-8 BOM付きです。Excelには取得値の列を文字列として取り込み、先頭ゼロなどを保持してください。
今回のViewer手操作・Excel画面・実帳票・DocuWorks 9.1は未確認です。確認範囲はdocs/maintainer/RELEASE_v0.5.0.mdと公開Releaseの最終検証報告を参照してください。
対応DocuWorks・NVIDIA GPUが必要です。旧版と元データは保持してください。

確認用XDWの文字背景は塗りつぶしなしです。新規白紙Reviewの追加処理を軽量化しています。
