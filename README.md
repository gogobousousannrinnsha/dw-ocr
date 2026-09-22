# DocuWorks OCR

このmainブランチは、Core **1.0.1** / Integrations **0.11.0** を含む次期公開版のソースです。公開済みの[DW-OCR v0.4.1 Pre-release](https://github.com/gogobousousannrinnsha/dw-ocr/releases/tag/v0.4.1)（Integrations 0.8.1）へ、新しいReviewed取り込み規則、矩形テンプレートによる項目取得、構造化結果のCSV出力、矩形生成の速度改善を追加しています。これらの変更を含むPortableはまだ公開していません。

XDWをOCRし、Canonical原記録・白紙Review・矩形付きXDW・確認画像を生成します。Viewerで保存した文字と位置は、別のReviewed ResultとJSONLへ取り込みます。原記録を変更せず、既存CorrectionSet APIも維持します。

- [利用者向け：操作・設定・保存先](docs/user/README.md)
- [Python API：結果形式・訂正・XDW](docs/api/README.md)
- [ID照合中心の取り込み2.0・複数参照のAPI](docs/api/reviewed-import-v2.md)
- [矩形テンプレートによる項目取得](docs/RECTANGLE_TEMPLATE.md)
- [構造化結果のCSV出力](docs/STRUCTURED_CSV.md)
- [保守担当：構造・試験・配布](docs/maintainer/README.md)
- [履歴・検証・公開済み基準](docs/history/README.md)

ソース中の校正結果取込BATはidentityモードを使用し、付箋の作業メモを本文から除外します。APIの既定値は従来のstrictモードです。テンプレート登録・確認・適用・CSV出力はCLI/APIで利用します。全体の入口は[文書案内](docs/README.md)です。

Viewerの基本編集は利用者確認済みです。その他の編集操作はSDKで代替検証しており、Viewerの全ケース目視確認が完了したとは扱いません。新機能の確認範囲は各機能の仕様・検証文書を参照してください。

自作部分はMIT、第三者資産は各条件を維持します。SDK・DLL・実文書は同梱しません。[ライセンス](LICENSE) ／ [第三者条件](THIRD_PARTY_NOTICES.md)
