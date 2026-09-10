# DW-OCR Portable v0.1.0

**試験的リリース / 公開梱包版 2026-09-10**

2026-09-09版の環境を基に、公開用に梱包と権利表示を整えました。配布セットの版はv0.1.0、基盤はdocuworks-ctypes 1.0.0 / docuworks-integrations 0.3.0です。

## ダウンロード

`ocr_join_tools_20260910_public.zip`と`ocr_part_001_transport.zip`～`ocr_part_008_transport.zip`の全9ファイルが必要です。旧版の同名transport ZIPを混ぜないでください。

結合ツールだけを展開して8個のZIPと同じ階層へ置き、`join_parts.bat`を実行します。成功表示を確認した後、`dw_ocr_with_code.zip`を新規フォルダーへ展開し、`verify_environment.bat`を実行します。

復元ZIP SHA-256:

```text
10e5428a9501ed3f2a754a2eb71d989ae7269d1d220acff428151ec7b6bf59b1
```

個別サイズ・SHA-256はRelease添付の`release-assets.json`と`SHA256SUMS_ASSETS.txt`にあります。第三者対応ソースは`third-party-sources-v0.1.0.zip`です。

## 公開梱包での変更

- 開発用の出所・ビルド履歴、独自パッケージのローカル導入情報を除去。
- 権利者の指定により独自部分へMITを適用。wheelのメタデータとRECORDを更新。
- 第三者LICENSE・NOTICEは保持し、モデルのApache本文・NOTICEと対応ソースを追加。
- OCRに不要なOpenCV FFmpeg動画プラグインとcuDNN開発用includeを除外。
- OCRコード2本、基盤Pythonソース、モデル重み、保持するランタイムバイナリは変更なし。
- 再分割し、結合ツール・manifest・SHA-256を新しい内容へ更新。

## 必要環境

Windows x64、正規のDocuWorks製品・対応x64 XDWAPI、CUDA対応NVIDIA GPU・ドライバー。Pythonは同梱です。空き容量は15～20GB程度にOCR成果物分を加えてください。

## 検証と既知の制約

公開ZIPのCRC、分割ハッシュ、コード・モデル同一性を確認しました。旧配布環境の正常実行は利用者報告です。1ページ23領域の矩形保存とViewer表示、4ページ377領域の矩形保存は引継ぎ記録であり、**今回の公開梱包版でGPU・実XDW・Viewerの通し試験を再実行したものではありません**。

OCR誤認識・矩形位置ずれ、別環境の互換性、Viewerの編集可否に注意してください。動画入出力・cuDNN開発は配布対象外です。既存の画像OCR機能向けの試験的配布です。

独自部分はMIT、第三者部分は各条件です。現状有姿で提供し、法令で認められる範囲で保証・責任を負いません。原本をバックアップし、試験用コピーで確認してください。

詳しい手順・検証記録・制約は[リポジトリREADME](https://github.com/gogobousousannrinnsha/dw-ocr/tree/v0.1.0)を参照してください。
