# DW-OCR v0.4.1

Core 1.0.1 / Integrations 0.8.1。Windows x64用Pre-releaseです。

- [利用者向け操作・設定・保存先](docs/user/README.md)
- [Python API・結果形式・訂正](docs/api/README.md)
- [保守・配布と構成管理](docs/maintainer/README.md)
- [履歴・公開済み基準・検証](docs/history/README.md)

OCR開始.batは全ページOCR・白紙Review・矩形付きXDW・確認画像と任意の元OCR JSONLを生成します。Viewerでreview.xdwを編集・保存して閉じ、校正結果取込.batへドロップすると独立したReviewed ResultとJSONLを保存します。取り込みは1文書ずつです。

Viewerの基本編集は利用者確認済みです。その他の編集操作はSDKで代替検証しており、Viewerの全ケース目視確認が完了したとは扱いません。旧版は保持し、新しいフォルダーへ展開してください。

自作部分はMIT、第三者資産は各条件を維持します。SDK・DLL・実文書は同梱しません。[ライセンス](LICENSE) ／ [第三者条件](THIRD_PARTY_NOTICES.md)

確認用XDWの文字背景は塗りつぶしなしです。新規白紙Reviewの追加処理を軽量化しています。
