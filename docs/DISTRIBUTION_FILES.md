# v0.3.0配布ファイル

実行には結合ツールと8個のtransport ZIPを使用します。完成ZIPは3,223,823,853 bytesです。
Core 1.0.0・Integrations 0.7.0のwheelとsdist、日本語検証記録、変更点、移行手順、モデル一覧を添付します。
ビルド用公開ソースはdw-ocr-source-v0.3.0.zipです。Portableの実行環境はソースZIPに含みません。
第三者対応ソースはv0.2.0と同じthird-party-sources-v0.1.0.zipです。

source-manifest.jsonは自身・release-assets.json・SHA256SUMS_ASSETS.txtを除く公開ソースのサイズとハッシュ一覧です。
ソースZIPは循環参照を避けるためrelease-assets.jsonとSHA256SUMS_ASSETS.txtを除きます。この2ファイルはReleaseへ別添します。
release-assets.jsonとSHA256SUMS_ASSETS.txtは自身を除く添付物、SHA256SUMS_RESTORED.txtは復元ZIPを照合します。
最終公開コミットと公開後の実ダウンロード照合は、公開後の検証記録で別途対応付けます。
