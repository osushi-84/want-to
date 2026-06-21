# アーキテクチャ

## 概要

やりたいことリストをビジュアルに表示するシングルページアプリ。フレームワーク・ビルドツールなし、素の HTML/CSS/JS のみ。

## ファイル構成

```
want-to-do/
├── index.html          # メインページ（本番）
├── data.json           # 表示データ（やりたいこと・やってみたいこと・行きたいライブ）
├── demo.html           # 表示モード比較デモ（横流れ・3Dカルーセル・球体・オービット）
├── やりたいこと.txt      # データの元ネタ・メモ
└── docs/
    ├── ARCHITECTURE.md # このファイル
    ├── CURRENT_TASK.md # 進行中タスク
    └── MEMO.md         # 実装ログ
```

## index.html の構成

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
- `index.html` は `fetch('./data.json')` で読み込み、件数表示・カルーセル・スフィアを初期化する
- `yariItems`: やりたいこと（現在 12 件）
- `tryItems`: やってみたいこと（現在 33 件）
- `artists`: 行きたいライブ（現在 36 件）

### 3D カルーセル

- `initCarousel(wrapId, data)` を共通関数として定義し、やりたいこと・やってみたいことの両方に使用
- 半径 600px 固定（モバイル 260px）
- スロット数は 24 固定
- angular step 固定 = 360 / slots
- ドラッグ＋慣性＋オート回転

### 3D スフィア

- フィボナッチ格子でアーティストを球面に均等配置
- ホバー: font-size 1.22 倍・白色・カラーグロー
- クリック: Google 検索（`[アーティスト名] ライブ チケット`）を別タブ
- 当たり判定は `transform: scale()` を使わず `font-size` のみで制御（hit area = 見た目）

## 技術スタック

- HTML / CSS / Vanilla JS
- Google Fonts（Noto Serif JP, Noto Sans JP, IBM Plex Mono）
- Web API: requestAnimationFrame, IntersectionObserver
