# docuworks-integrations 0.8.1

保存済みOCR結果を中心に、OCR実行・矩形と確認画像・文字訂正・編集用XDWを提供します。Core 1.0.0を使用します。

この開発候補ではPaddleの空文字・空白だけの認識結果を除外し、正常文字を保持して処理を継続します。
不正な座標・信頼度・非文字列は引き続き拒否します。公開Portable v0.3.0には未反映です。
[再現手順と検証範囲](https://github.com/gogobousousannrinnsha/dw-ocr/blob/v0.4.1/docs/maintainer/PADDLE_BLANK_TEXT.md)

- [全体のAPI案内](https://github.com/gogobousousannrinnsha/dw-ocr/blob/v0.4.1/docs/api/README.md)
- [保存形式とAPIの正本](OCR_RESULT_FORMAT.md)
- [白紙Review・独立したReviewed Result 1.0の仕様とAPI](REVIEWED_RESULT_FORMAT.md)
- [訂正の検証・保存・適用](https://github.com/gogobousousannrinnsha/dw-ocr/blob/v0.4.1/docs/api/corrections.md)
- [編集用XDW：1ページ内の指定領域](https://github.com/gogobousousannrinnsha/dw-ocr/blob/v0.4.1/docs/api/review-regions.md)
- [利用手順](https://github.com/gogobousousannrinnsha/dw-ocr/blob/v0.4.1/docs/user/README.md) ／ [検証範囲](https://github.com/gogobousousannrinnsha/dw-ocr/blob/v0.4.1/docs/history/README.md)

標準OCRのBATは全ページOCR・矩形・確認画像と任意JSONLを生成します。編集用XDWと訂正はPython APIで明示実行します。元runを変更せず、文字以外の座標・順序・信頼度を維持します。

旧workflow APIは0.2.0形式との互換用です。新規コードではrecognition、results、consumersを利用してください。新規OCRはResult 1.1、1.0・旧runは読込み互換です。

新しい白紙Reviewは全ページの独立SessionとReviewed Resultを提供し、Portableから生成・取り込みできます。Viewerの基本編集は利用者確認済みで、その他はSDK代替操作の検証です。検索・テンプレートは対象外です。
