# DW-OCR Portable

Windows x64向けのDocuWorks OCR実行環境です。Python、OCRライブラリ、PP-OCRv6 mediumモデル、DocuWorks連携コードを含みます。

**v0.1.0 / 試験的リリース** — 2026-09-09版を基にした**公開梱包版 2026-09-10**です。旧配布物と分割ファイル・結合ツールを混ぜないでください。梱包変更後のGPU・実XDW・Viewer通し試験は未実施です。

## ダウンロードと導入

[v0.1.0 Release](https://github.com/gogobousousannrinnsha/dw-ocr/releases/tag/v0.1.0)から、`ocr_join_tools_20260910_public.zip`と`ocr_part_001_transport.zip`～`ocr_part_008_transport.zip`の**全9ファイル**を取得します。ハッシュ資料と第三者対応ソースも同Releaseにあります。

1. 8個のtransport ZIPを同じフォルダーに置きます。
2. **結合ツールZIPだけを展開**し、中の`join_parts.bat`等を同じ階層に置きます。
3. `join_parts.bat`を実行し、`SUCCESS: ZIP restored and verified.`を確認します。
4. `dw_ocr_with_code.zip`を新しいフォルダーに展開します。
5. `verify_environment.bat`を実行し、試験用XDWのコピーで動作を確認します。

GitHubの「Source code」ZIPにはPortable実行環境は入りません。[配布一覧とSHA-256](docs/DISTRIBUTION_FILES.md) / [復元・実行手順](docs/INSTALL_RESTORE.md)

## 機能と必要環境

全ページをOCRし、認識領域の周囲に赤色・塗りなしの矩形を付けた別XDWを保存します。保存済みのOCR結果から、認識文字を配置した確認画像`text-map.png`と`overlay-text.png`を生成できます。基盤ライブラリはCanonical OCR Result 1.0、JSONL、選択領域のMarker付与も提供します。

Windows x64、利用権のあるDocuWorks製品と対応x64 XDWAPI、CUDA対応NVIDIA GPU・ドライバーが必要です。Pythonは同梱され、GPU OCRにCPU自動代替はありません。空き容量は**15～20GB程度＋OCR成果物分**が目安です。[必要環境](docs/REQUIREMENTS.md)

## 復元ZIPのSHA-256

公開梱包版の実物を再計算した値です。

```text
10e5428a9501ed3f2a754a2eb71d989ae7269d1d220acff428151ec7b6bf59b1
```

[SHA256SUMS_RESTORED.txt](SHA256SUMS_RESTORED.txt)は結合後ZIP用、[SHA256SUMS_ASSETS.txt](SHA256SUMS_ASSETS.txt)は個別ダウンロード用です。SHA-256は内容一致の検査であり署名ではありません。

## 検証と制約

公開用ZIPのCRC、個別ハッシュ、元のOCRコード・モデルの同一性、結合データのハッシュを検証しました。元の配布環境については利用者から正常実行の報告があります。1ページ23領域の矩形保存・Viewer表示、4ページ377領域の矩形保存は引継ぎ記録です。[検証の範囲](docs/VERIFICATION.md)

OCR結果には誤認識や位置ずれがあり得ます。Viewer編集可否、全環境での動作、ネイティブOCRテキストの埋込みを保証しません。動画入出力とcuDNN開発は対象外です。[既知の制約](docs/KNOWN_LIMITATIONS.md)

## ライセンスと免責

独自コード・結合ツール・文書は[MIT License](LICENSE)です。第三者ライブラリ・モデル・GPUランタイムはそれぞれの条件を保持します。[適用範囲](LICENSE_NOTICE.md) / [第三者資産](THIRD_PARTY_NOTICES.md)

本ツールは非公式です。製品提供元による提供・保証・推奨を示すものではありません。現状有姿で提供し、法令で認められる範囲で正確性、特定目的への適合性、データ保全を保証せず、使用に伴う損害について責任を負いません。原本をバックアップし、結果は利用者が確認してください。

[Issues](https://github.com/gogobousousannrinnsha/dw-ocr/issues)には、実文書、OCR本文、個人パス、資格情報を含めず、版と匿名化した再現手順を記載してください。
