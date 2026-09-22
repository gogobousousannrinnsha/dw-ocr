# DW-OCR v0.5.0

Core 1.0.1 / Integrations 0.11.0。Windows x64用Pre-releaseです。

- [利用者向け操作・設定・保存先](docs/user/README.md)
- [矩形テンプレートからCSV一覧まで](docs/user/template-csv.md)
- [Python API・結果形式・訂正](docs/api/README.md)
- [保守・配布と構成管理](docs/maintainer/README.md)
- [履歴・公開済み基準・検証](docs/history/README.md)

OCR開始.batは全ページOCR・白紙Review・矩形付きXDW・確認画像と任意の元OCR JSONLを生成します。Viewerでreview.xdwを編集・保存して閉じ、校正結果取込.batへドロップすると独立したReviewed ResultとJSONLを保存します。取り込みは1文書ずつです。

1つのXDWに複数の矩形を配置して項目名・適用条件を設定し、テンプレートとして登録できます。校正後の文字と位置から項目を取得し、Structured Resultへ保存して、同じ登録テンプレートの結果を1文書1レコードのCSVへまとめます。登録・確認・適用・CSV出力はdocuworks-integrations.batから実行します。

新しい取り込み・テンプレートのSDK試験は合成文書を使った確認です。今回のViewer手操作・Excel画面・実帳票・DocuWorks 9.1は未確認です。[構成と検証方針](docs/maintainer/RELEASE_v0.5.0.md)と、Releaseに添付する最終検証報告を参照してください。旧版は保持し、新しいフォルダーへ展開してください。

自作部分はMIT、第三者資産は各条件を維持します。SDK・DLL・実文書は同梱しません。[ライセンス](LICENSE) ／ [第三者条件](THIRD_PARTY_NOTICES.md)

確認用XDWの文字背景は塗りつぶしなしです。新規白紙Reviewの追加処理に加え、矩形生成時のページ情報の再取得を減らしています。
