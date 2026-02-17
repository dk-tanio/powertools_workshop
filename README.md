# Lambda Powertools for Python ワークショップ資料

## 目的

このリポジトリは、AWS Lambda Powertools を使った実践的な開発体験を通じて、
ロギング、ルーティング、入力検証、例外処理、出力検証の基本を身に付けることを目的とします

## このワークで得られるもの

- 構造化ログの設計と実装の考え方
- API Gateway + Lambda のルーティング実装の流れ
- Pydantic によるリクエスト検証とレスポンス検証
- 例外の設計とハンドラでの安全な復元
- ドメイン層とインフラ層を分離した構成の読み方

## 利用ライブラリのバージョン

- Python 3.14.1
  - aws-lambda-powertools 3.23.0
  - boto3 1.42.16
  - boto3-stubs 1.42.16
  - pydantic 2.12.5
  - pytest 9.0.2
  - ruff 0.14.10

## 事前準備

mise/uv で簡単に環境構築が可能です

```bash
mise install
mise trust
```

依存関係の導入は次の手順を推奨します

```bash
uv sync
```

## 公式ドキュメント

- [Logger](https://docs.aws.amazon.com/powertools/python/latest/core/logger/)
- [REST API](https://docs.aws.amazon.com/powertools/python/latest/core/event_handler/api_gateway/)

## 参考ディレクトリ構成

- 本ワークは [cosmic python](https://www.cosmicpython.com/)を参考に設計している(AIが)
- 本書は Python で DDD を前提としたアーキテクチャを学べるオープン書籍で別途おすすめ

- `src/handler.py` : Lambda の handler 関数
- `src/domain/` : 値オブジェクトや集約
- `src/infrastructure/` : DynamoDB へのアクセス
- `infra/` : AWS の IaC リソース

## AWS 環境へのデプロイ

- 本ワーク自体は実際にリソースを構築することを主としていないため、デプロイ自体はオプションです
- `infra/` 配下は CDK による IaC のコードです
- 任意の環境でデプロイ可能です
- なおデフォルトの APIGateway に認証は入っていないため、リソースは自己責任で構築ください

### 自分のアカウントにデプロイする場合

```bash
cd infra
npm install
npx cdk deploy
```

### 砂場アカウントにデプロイする場合

GitHub Actions の `Deploy CDK Resources` ワークフローを `workflow_dispatch` で実行するとデプロイできます

- GitHub の Actions 画面で `Deploy CDK Resources` を選び、`Run workflow` から実行してください
- スタック名を変更する場合は `infra/bin/アプリ.ts` の `new 書籍Apiスタック(app, "PowertoolsWorkshopBookApi");` の文字列を変更してください
- 変更したスタック名でデプロイする場合は、Actions 実行時の `stack_name` に同じ名前を指定してください
- このリポジトリは public のため、機密情報や不要なファイルを push しないよう注意してください

## ブランチ構成と進め方

以下の順で進めますワークは1つ前のブランチをベースに修正・機能追加していきます

1. `01_logger/question`（配布用の初期コード）
2. `02_logger/sample`（ロギングの解答例）
3. `03_routing/sample`（ルーティングの解答例）
4. `04_requestBody/sample`（リクエスト検証の解答例）
5. `05_exception/sample`（例外ルーティングの解答例）
6. `06_response/sample`（レスポンス検証の解答例）

## ワーク内容

### 1. Logger

**このワークのゴール**

- 可観測性を高めるためにはログを出力して、リソース上に何が発生したのか記録することがまず何よりも重要です
- 特に問題が発生しやすいのは DB など外部のリソースとやりとりする部分
- エラーが発生した際、どのような入力だったのかをログに出力しよう

**確認ポイント**

- ログ出力が情報不足になっていないか
- 例外時のログが調査に使える粒度になっているか

**注目ポイント**

- 実際のプロダクトでは複数の非同期通信が発生します
- 中にはエラーが出る（たとえば get を試みたが 404 だった）ケースが正常であることも想定されます
- AWS ではログを逐次、出力しているとログが溜まって視認性が悪そう・・・？

### 2. Routing

**このワークのゴール**

- 現在の handler 層では Lambda のパスを関数ごとに切り分けている
- Lambda Powertools ではこれを1つの Lambda に集約する([Lambdalith](https://speakerdeck.com/slsops/lambdalith?slide=7))が簡単に実現可能
- API Gateway のパスに応じて適切な handler 関数へルーティングできるようにしよう

**確認ポイント**

- パスとメソッドの組合せが仕様どおりに動くか

**注目ポイント**

- パスパラメータは app 以外からも受け取れるぞ

### 3. Request Body

**このワークのゴール**

- リクエストのパラメータの型は `body_data: Any | dict[Unknown, Unknown]` である
- そのため値オブジェクトのインスタンスで型エラーが発火する
- Pydantic BaseModel を作成し Request Body のスキーマを定義しよう
- そのスキーマを handler の入力に対して型ヒントとして与えよう

**確認ポイント**

- 必須項目の欠落や型の不一致が検知されるか
- 値オブジェクトの制約が正しく適用されているか

### 4. Exception

**このワークのゴール**

- 2. Routing のワークで Event Handler がパスごとにハンドリングされるようになった
- しかしエラー発生時の処理が重複している
- たとえば本が見つからなかった時は必ず Not Found の Status Code を返したい
- 例外発生時の処理を例外ごとにハンドリングしよう

**確認ポイント**

- 書籍が存在しない場合や重複する場合に正しい応答になるか
- 例外時のログが適切に記録されるか

**注目ポイント**

- どのパスでエラーが発生したか分からなくなってしまうので、 logging の内容を整理しよう

### 5. Response ワーク

**このワークのゴール**

- handler の出力の型が Response になっている
- これは型の検証をしていないため、想定していない出力を返す恐れがある
- handler の戻り値の型を定義しよう

**確認ポイント**

- 返却するデータがスキーマと一致しているか
- シリアライズ形式が期待どおりか

## Powertools の要点

- Logger: 構造化ログの出力やコンテキスト追加が簡潔にできる
- Event Handler: API Gateway のルーティングやバリデーションを簡潔にできる
- 型注釈との相性が良く、Pydantic と組み合わせると検証が強固になる
