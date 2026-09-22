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
Viewerの基本編集以外はSDK代替操作での検証です。全ケースの目視確認済みとは扱いません。
対応DocuWorks・NVIDIA GPUが必要です。旧版と元データは保持してください。

確認用XDWの文字背景は塗りつぶしなしです。新規白紙Reviewの追加処理を軽量化しています。
