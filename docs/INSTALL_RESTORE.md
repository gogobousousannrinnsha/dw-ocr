# 復元・インストール・実行

## 1. 全9ファイルを同じ場所へ保存

[v0.1.0](https://github.com/gogobousousannrinnsha/dw-ocr/releases/tag/v0.1.0)から公開版結合ツールと全8個のtransport ZIPを取得します。公開版と旧版を混ぜないでください。15～20GB程度の空き容量とOCR出力分を確保します。

`SHA256SUMS_ASSETS.txt`の値と、各ファイルを`Get-FileHash -Algorithm SHA256`で計算した値を照合してください。例:

```powershell
Get-FileHash -LiteralPath 'C:\DW-OCR-Download\ocr_join_tools_20260910_public.zip' -Algorithm SHA256
```

## 2. 結合ツールだけを展開

`ocr_join_tools_20260910_public.zip`の中身を、8個のtransport ZIPと同じ階層へ置きます。transport ZIPは展開・改名しません。

```text
C:\DW-OCR-Download\
  ocr_part_001_transport.zip ... ocr_part_008_transport.zip
  join_parts.bat
  join_parts.ps1
  verify_parts.bat
  split_manifest.json
  README_JOIN_JA.txt
```

## 3. 結合と完成ZIPの検証

```powershell
Set-Location 'C:\DW-OCR-Download'
.\join_parts.bat
```

`SUCCESS: ZIP restored and verified.`が成功表示です。同じ内容の完成ZIPが既にある場合は`SUCCESS: Existing ZIP already verified:`になります。異なる内容の既存ZIPは上書きせず停止します。検証だけなら`verify_parts.bat`を実行します。分割ファイルは削除しません。

```powershell
$expected = '10e5428a9501ed3f2a754a2eb71d989ae7269d1d220acff428151ec7b6bf59b1'
$actual = (Get-FileHash -LiteralPath '.\dw_ocr_with_code.zip' -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
if ($actual -ne $expected) { throw 'SHA-256不一致。展開・実行を中止してください。' }
```

結合時のPython事前インストールとネット接続は不要です。

## 4. 展開と環境確認

`dw_ocr_with_code.zip`を短い、新規の書込み可能なフォルダー（例`C:\DW-OCR`）へ展開します。`runtime`、`models`、`scripts`、BATが同じ階層に並びます。`verify_environment.bat`のある階層へ移動します。

```powershell
Set-Location 'C:\DW-OCR'
.\verify_environment.bat
```

このスクリプトの`Environment integrity: OK`だけではGPUやDocuWorksの利用可能性は保証されません。GPU数、`System XDWAPI`、`nvidia-smi`の表示も確認してください。GPU数0やDLL不在を表示してもこの最後の表示へ進む実装です。別途`python.bat -m pip check`も確認できます。

## 5. 全ページOCRと矩形保存

原本をバックアップし、最初は作業用コピーで確認します。

```powershell
.\ocr_rectangles.bat 'C:\XDW\sample-copy.xdw'
```

既定出力は入力と同じフォルダーの`sample-copy_ocr_rectangles.xdw`と`sample-copy_ocr_rectangles_ocr_report.json`です。既存出力・レポートがあれば停止します。指定する場合:

```powershell
.\ocr_rectangles.bat 'C:\XDW\sample-copy.xdw' --output 'C:\XDW\checked.xdw'
```

全ページOCR後に原本のコピーを作り、赤色・塗りなしの矩形を追加して保存します。既定余白は0.5mm、最小矩形寸法は3mm、DPIは300（600も指定可）です。認識0領域のページはスキップします。他のOCR失敗時は完成XDWを作成せず、注釈・保存で例外が起きた場合は作成した出力の削除を試みます。失敗時は実際に残ったファイルを確認してください。

BATは`--keep-runs`を渡してページ別bundleを保持します。Pythonを直接実行する場合は明示してください。省略すると収集済みページのbundleを削除する仕様です。出力はViewerで位置、可読性、警告、選択・編集可否を確認します。

## 6. 保存済みbundleから確認画像を生成

OCRログの`Session dir`またはJSONレポートの`session_dir`の下で、**manifest.jsonがあるページ別bundleルート**を指定します。

```powershell
.\text_maps.bat 'C:\DW-OCR\runs\sample-session\page-0001'
```

該当bundleの画像フォルダーに`text-map.png`と`overlay-text.png`、bundleルートに`text-map-report.json`を生成します。親セッションフォルダーや画像だけのフォルダーを指定しないでください。

```powershell
.\text_maps.bat 'C:\DW-OCR\runs\sample-session\page-0001' --font 'C:\Windows\Fonts\meiryo.ttc'
.\text_maps.bat 'C:\DW-OCR\runs\sample-session\page-0001' --overwrite
```

既存PNGを置換する場合だけ`--overwrite`を使います。レポートは同名を置換するため、元のmanifest等を`--report`へ指定しないでください。元のフォント・縦書き・傾斜を忠実に復元する機能ではありません。確認画像作成だけならGPU・XDWAPIは使用しません。

## トラブル時

分割不足・hash不一致は版と全9ファイルを確認して再取得します。モデルhashを変更して検証を回避しないでください。GPUエラーはGPU・ドライバー、XDWAPIエラーは正規製品のx64 DLLと関連DLLを確認します。既存出力への衝突時は新しい名前・フォルダーを使います。

OCR bundleやレポートは実文書コピー・認識内容・個人パスを含み得ます。そのまま公開しないでください。
