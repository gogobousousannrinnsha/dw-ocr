# v0.2.0の公開手順

公開先は`gogobousousannrinnsha/dw-ocr`、タグは`v0.2.0`、公開区分はPre-releaseです。v0.1.0のタグ・Release・Assetは変更しません。開発リポジトリの履歴・実文書・生ログ・OCR結果は公開側へ移植しません。

この手順は利用者の最終承認後に実施します。現在はローカルの公開準備です。ローカル引渡しファイル`PUBLICATION_HANDOFF.json`には公開用コミット、公開mainの基準コミット、完成Assetのパスとハッシュが記録されています。リポジトリ内の`release-assets.json`は配布ファイル、`RELEASE_PROVENANCE.json`は採用コードとwheel・モデル・Portableの対応を示します。

## 公開前の確認

1. 公開用アカウントで認証し、`gh api user`と対象リポジトリの`permissions.push`を確認します。今回の準備時に利用したアカウントには公開先の書込み権限がありませんでした。
2. `git remote get-url origin`が公開先を指すこと、作業ツリーがクリーンであること、HEADが引渡しファイルの公開用コミットと一致することを確認します。
3. 公開mainが引渡しファイルの基準コミットのままで、v0.2.0のタグ・Releaseが存在しないことを確認します。変化があれば自動で上書きせず、差分をレビューして配布物との対応を再確認します。
4. Assetを再計算して`release-assets.json`、`SHA256SUMS_ASSETS.txt`と照合します。完成ZIPは`SHA256SUMS_RESTORED.txt`で照合します。

`tools/Measure-ReleaseAssets.ps1 -AssetDirectory <配布ファイルのフォルダー> -OutputDirectory <新規検証先>`でもpayloadのサイズ・ハッシュを照合できます。manifestとハッシュ一覧自身のハッシュは、ローカル引渡しファイルで確認します。

## 公開操作

以下の値は引渡しファイルから読み込み、実行直前に照合してください。個人パスをリポジトリへ書き込まないでください。

```powershell
$handoff = Get-Content -LiteralPath <PUBLICATION_HANDOFF.jsonのパス> -Raw -Encoding UTF8 | ConvertFrom-Json
$targetCommit = $handoff.public_commit
if ((git rev-parse HEAD) -ne $targetCommit) { throw 'Unexpected local commit' }
$currentMain = gh api repos/gogobousousannrinnsha/dw-ocr/commits/main --jq .sha
if ($currentMain -ne $handoff.public_base_commit) { throw 'Public main changed' }
git push origin HEAD:main
if ($LASTEXITCODE -ne 0) { throw 'Push failed' }
gh release create v0.2.0 --repo gogobousousannrinnsha/dw-ocr --target $targetCommit --draft --prerelease --title 'DW-OCR Portable v0.2.0' --notes-file RELEASE_NOTES_v0.2.0.md
if ($LASTEXITCODE -ne 0) { throw 'Draft creation failed' }
foreach ($asset in $handoff.upload_assets) {
    gh release upload v0.2.0 (Join-Path $handoff.asset_directory $asset.name) --repo gogobousousannrinnsha/dw-ocr
    if ($LASTEXITCODE -ne 0) { throw ('Upload failed: '+$asset.name) }
}
```

Draftで全ファイルの名前・個数・サイズ・SHA-256を照合します。GitHubが返すdigestが取得できなければ、別の作業フォルダーへ再ダウンロードして照合します。Release本文・ソース・復元手順のリンクも確認します。アップロードに失敗した場合はDraftのまま調査し、未照合の状態で公開しません。

全照合が完了したら`gh release edit v0.2.0 --repo gogobousousannrinnsha/dw-ocr --draft=false --prerelease`で公開します。公開後にタグの指すコミット、Asset一覧、ダウンロードリンクを確認します。問題が出た場合は新版の利用案内を停止し、保持しているv0.1.0を案内します。旧Releaseのファイルを新版と差し替えません。
