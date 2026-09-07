# アーキテクチャ

## 概要

やりたいことリストをビジュアルに表示するシングルページアプリ。フレームワーク・ビルドツールなし、素の HTML/CSS/JS のみ。

## ファイル構成

```
want-to-do/
├── index.html          # メインページのHTML（本番）
├── style.css           # メインページのスタイル
├── script.js           # メインページの表示・操作ロジック
├── data.json           # 表示データ（やりたいこと・やってみたいこと・行きたいライブ）
├── demo.html           # 表示モード比較デモ（横流れ・3Dカルーセル・球体・オービット）
├── やりたいこと.txt      # データの元ネタ・メモ
├── tests/
│   ├── test_static_assets.py # 静的ファイル構成のテスト
│   ├── test_completion.py # 完了表示の回帰テスト（pytest + Node.js）
│   └── test_resize.py   # リサイズ追従と状態維持の回帰テスト（pytest + Node.js）
└── docs/
    ├── ARCHITECTURE.md # このファイル
    ├── CURRENT_TASK.md # 進行中タスク
    └── MEMO.md         # 実装ログ
```

## メインページの構成

- `index.html`: ページ構造と外部ファイルの読み込み
- `style.css`: レイアウト、装飾、レスポンシブ対応
- `script.js`: データ取得、件数表示、カルーセル、スフィアの制御

### セクション構成

| セクション | 表示内容 | UI コンポーネント |
|---|---|---|
| Hero | タイトル・件数統計 | テキスト |
| やりたいこと | やりたいことリスト | 3D カルーセル |
| やってみたいこと | やってみたいことリスト | 3D カルーセル |
| 行きたいライブ | アーティストリスト | 3D スフィア |
| Footer | - | テキスト |

### データ

- 表示データは `data.json` で管理する
- `script.js` は `fetch('./data.json')` で読み込み、件数表示・カルーセル・スフィアを初期化する
- `yariItems`: やりたいこと（現在 12 件）
- `tryItems`: やってみたいこと（現在 34 件）
- `artists`: 行きたいライブ（現在 36 件）
- `tryItems` の各項目の `completed`（真偽値）で完了状態を保持する。`true` の項目はカードに「✓ 完了」と緑色の枠を表示し、`false` または未指定は未完了として表示する
- 完了状態の変更は配信元の `data.json` を編集して反映する。画面は読み取り専用で、ブラウザへの保存や画面からの切り替えは行わない

### 3D カルーセル

- `initCarousel(wrapId, data)` を共通関数として定義し、やりたいこと・やってみたいことの両方に使用
- 半径 600px 固定（モバイル 260px）
- 画面幅が 640px 以下かをリサイズ時にも判定し、既存カードの寸法と半径を更新する。回転角とカードの内容は維持する
- スロット数は 24 固定
- angular step 固定 = 360 / slots
- ドラッグ＋慣性＋オート回転
- `renderCarouselItem(card, item)` で初期表示と回転中のカード差し替えを共通化し、項目ごとに完了表示を更新する

### 3D スフィア

- フィボナッチ格子でアーティストを球面に均等配置
- 基準座標は単位球として保持し、`ResizeObserver` で表示領域の幅・高さ・半径を更新して投影する。リサイズ時も回転とホバーの状態を維持し、幅または高さが 0 の間は描画を待機する
- ホバー: font-size 1.22 倍・白色・カラーグロー
- クリック: Google 検索（`[アーティスト名] ライブ チケット`）を別タブ
- 当たり判定は `transform: scale()` を使わず `font-size` のみで制御（hit area = 見た目）

## 技術スタック

- HTML / CSS / Vanilla JS
- Google Fonts（Noto Serif JP, Noto Sans JP, IBM Plex Mono）
- Web API: requestAnimationFrame, IntersectionObserver, ResizeObserver
