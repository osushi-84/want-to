# 実装メモ

---

## [claudecode] 2026-05-19 — 初期セッション実装まとめ

### やったこと

**データ管理**
- `やりたいこと.txt` をやりたいこと / やってみたいこと / 行きたいライブ の3セクションに整形
- txt を正として、index.html のデータを手動同期する運用に

**カルーセル**
- `initCarousel(wrapId, data)` に共通関数化し、2セクションで使い回し
- 半径を固定（600px / モバイル 260px）してアイテム数に依存しない見た目に
- スロット数 = `Math.ceil(24 / n) * n` でアイテムを複製して全周を埋め、途切れなくループ
- angular step = 360 / slots で常に一定間隔

**スフィア**
- アーティスト名クリック → `window.open` で Google 検索（ライブ チケット）を別タブ
- ホバー時: font-size 1.22 倍・color #fff・text-shadow でカラーグロー
- 当たり判定の問題（transform: scale は hit area に影響しない）を `font-size` のみで奥行きスケールすることで解消

**モバイル対応**
- カルーセル: 半径 260px・カード 62×46px・フォント縮小（メディアクエリ + JS の isMobile フラグ）
- スフィア: `.sp-tag { font-size: .6rem !important }` でフォント縮小（JS inline style を上書きするため !important 必須）
- `touchmove` を `passive: false` にして `e.preventDefault()` でドラッグ中の画面スクロールを防止

### 気をつけること

- スフィアのフォントサイズは tick() 内で毎フレーム inline style で上書きされるため、CSS から変更する場合は `!important` が必要
- カルーセルの `isMobile` は初期化時の `window.innerWidth` で判定しているため、リサイズしても更新されない（許容）

---

## [codex] 2026-05-24 — やりたいこと.txt の最新内容反映

### やったこと

- `やりたいこと.txt` の追加分を `index.html` に反映
  - やりたいこと: キャッチボール
  - やってみたいこと: シュラスコ食べる
  - 行きたいライブ: 水曜日カンパネラ
- ヒーローの件数表示とライブバッジを最新件数に更新（12 / 32 / 34）
- `demo.html` のやってみたいこと配列も最新内容に同期

### 気をつけること

- 現状は `やりたいこと.txt` が正で、HTML 内の配列へ手動反映する運用のまま

---

## [codex] 2026-06-04 — 行きたいライブ追加

### やったこと

- `やりたいこと.txt` の行きたいライブにナナオアカリ・NEEを追加
- `index.html` の `artists` 配列と表示件数を最新件数に更新（36）
- `docs/CURRENT_TASK.md` と `docs/ARCHITECTURE.md` の件数メモを更新

---

## [codex] 2026-06-09 — やってみたいこと追加

### やったこと

- `やりたいこと.txt` のやってみたいことに泥団子作りを追加
- `index.html` / `demo.html` のやってみたいこと配列に泥団子作りを追加
- ヒーローのやってみたいこと件数と `docs/ARCHITECTURE.md` の件数メモを 33 件に更新

---

## [codex] 2026-06-21 — 表示データの JSON 分離

### やったこと

- `index.html` に直書きしていた `yariItems` / `items` / `artists` を `data.json` に移動
- `index.html` は `fetch('./data.json')` でデータを読み込み、件数表示・カルーセル・スフィアを初期化する形に変更
- 件数表示とライブバッジを `data.json` の件数から自動更新するように変更

### 気をつけること

- ローカルで確認する場合、`index.html` を直接開くのではなく `python -m http.server 8000` などで配信して確認する
- GitHub Pages では `index.html` と同階層の `data.json` がそのまま配信されるため、この構成で動作する

---

## [codex] 2026-06-25 — やってみたいこと追加

### やったこと

- `data.json` のやってみたいことに「麻辣湯食べる」を追加
- `やりたいこと.txt` と `demo.html` の表示データを同期
- `docs/ARCHITECTURE.md` のやってみたいこと件数を 34 件に更新

---

## [codex] 2026-06-25 — CSS / JavaScript の外部ファイル分離

### やったこと

- `index.html` 内の `<style>` を `style.css` に分離
- `index.html` 内の `<script>` を `script.js` に分離
- `index.html` から両ファイルを外部読み込みする構成へ変更
- 表示や処理の内容は変更せず、ファイル構成のみ整理
- 外部ファイル参照と主要コードの存在を確認する静的テストを追加

---

## [codex] 2026-09-07 — 配信データに基づく完了チェック表示

### やったこと

- `data.json` の `tryItems` に `completed` を追加。完了した項目を `true` に変更して配信すると、カードに「✓ 完了」と緑色の枠が表示される
- 完了済み項目の指定はまだないため、初期値は全件 `false` とした
- ユーザーの指定に従い、完了状態は配信元の JSON で管理し、画面では読み取って表示する。画面操作による変更や localStorage 保存は追加しない
- `script.js` でカードの初期表示と回転中の差し替えに同じ描画関数を使い、前の項目のチェックが残らないようにした
- 完了表示のスタイルは `style.css` に追加
- `tests/test_completion.py` とテスト生成物用の `.gitignore` を追加

### 検証

- `pytest -q`: 10 件成功、0 件失敗（既存 2 件と完了表示 8 件。Node.js で実際の JavaScript を実行し、完了・未完了・未指定・カード再利用・文字エスケープ・JSON の型を確認）
- `git diff --check`: 問題なし
- 実ブラウザの確認は、確認用ブラウザの接続エラーにより未実施
