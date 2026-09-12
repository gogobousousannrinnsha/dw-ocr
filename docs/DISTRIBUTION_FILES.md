# v0.2.0配布ファイル

実行に必要な取得ファイルは結合ツールと8個のtransport ZIPの全9個です。1部品400MiB未満です。完成ZIPは3,223,574,617 bytesで、通常は分割ファイルから復元します。

| ファイル | 用途 |
|---|---|
| ocr_join_tools.zip | 結合・検証BAT、PowerShell、split manifest |
| ocr_part_001_transport.zip～ocr_part_008_transport.zip | Portableの分割データ |
| split_manifest.json | 分割前ZIPと生部品のサイズ・ハッシュ |
| dw-ocr-source-v0.2.0.zip | ビルド可能な公開ソース・説明書 |
| Core 1.0.0 / Integrations 0.6.0のwheel・sdist各1個 | 採用ライブラリ配布物 |
| third-party-sources-v0.1.0.zip | 内容を維持した第三者対応ソース |
| MODEL_HASHES.json / RELEASE_PROVENANCE.json | モデルと採用コード・配布物の対応 |
| VERIFICATION_JA.md / RELEASE_NOTES_v0.2.0.md | 検証条件、変更点、移行 |
| release-assets.json / SHA256SUMS_ASSETS.txt | 個別配布ファイルのサイズ・ハッシュ |
| SHA256SUMS_RESTORED.txt | 復元ZIPのハッシュ |

ソースZIPには循環参照を避けるためrelease-assets.jsonとSHA256SUMS_ASSETS.txtを含めず、これらはReleaseへ別添します。source-manifest.jsonは自身とこの2ファイルを除く公開ソースのハッシュ一覧です。Gitタグの自動Source code ZIPにはリポジトリ内のこれらのメタデータも含まれます。

第三者対応ソースのファイル名にv0.1.0が残るのは、その資産を変更していないためです。OCR実行版はv0.2.0です。ハッシュは内容一致の確認であり署名ではありません。
