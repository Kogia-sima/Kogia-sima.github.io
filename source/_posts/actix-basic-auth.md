---
title: Rust (actix-web) でBasic認証を実装する
date: 2022-03-12 21:41:57
categories:
  - [Rust]
tags:
  - [actix-web]
  - [Basic認証]
---

# 背景

Actix-webでBasic認証を実装しようとしたけど情報があまり出てこなかったのでメモ

# Basic認証とは？

[Mozillaの説明](https://developer.mozilla.org/ja/docs/Web/HTTP/Authentication)が非常に分かりやすいのでそちらを参照するのが良いと思われます。。

簡単に言うと、クライアントがユーザ名とパスワードをBase64エンコードして送信し、サーバがそれをデコードしてパスワードを比較するという認証方法です。

<br>

パスワードが暗号化されないので、セキュリティ的にはあまり好ましい認証方式ではありません。

クライアント側がBasic認証しか対応していないなど特別な場合を除き、より安全な認証方式を用いるべきです。

# 実装

## まず基本的なサーバを作る

まずは[Actix-webのREADME](https://github.com/actix/actix-web#example)を参考に、基本的なHTTPサーバを実装します。

```rust
use actix_web::{get, App, HttpServer};

#[get("/")]
async fn greet() -> String {
    format!("Hello world!")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new().service(greet)
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}
```

このプログラムを動かして、[http://127.0.0.1:8080](http://127.0.0.1:8080)にアクセスしてみると、"Hello, world!"と表示されると思います。

## Basic認証を行う

Actix-webでBasic認証を行うには、[actix_web_httpauth](https://docs.rs/actix-web-httpauth/latest/actix_web_httpauth/index.html)を使用します。

```rust
use actix_web::{get, App, HttpServer};
use actix_web_httpauth::extractors::basic::{BasicAuth, Config};
use actix_web_httpauth::extractors::AuthenticationError;

#[get("/")]
async fn greet(auth: BasicAuth) -> Result<String, Error> {
    // クライアントから渡されたユーザ名とパスワードを取得する
    let user = auth.user_id().as_ref();
    let password = match auth.password() {
        Some(p) => p.as_ref().trim(),
        None => ""
    };

    // ユーザ名とパスワードが正しくない場合、401 Unauthorizedを返す
    if user != "foo" || password != "bar" {
        return Err(AuthenticationError::from(Config::default()).into());
    }

    format!("Hello, {user}!")
}
```

アプリケーション全体、または特定のスコープ全体にBasic認証を設けたい場合は、[HttpAuthentication](https://docs.rs/actix-web-httpauth/latest/actix_web_httpauth/middleware/struct.HttpAuthentication.html)というミドルウェアが便利です。

（参考：[https://turreta.com/2020/06/07/actix-web-basic-and-bearer-authentication-examples/](https://turreta.com/2020/06/07/actix-web-basic-and-bearer-authentication-examples/)）

```rust
use actix_web::dev::ServiceRequest;
use actix_web::{get, App, Error, HttpServer};
use actix_web_httpauth::extractors::basic::{BasicAuth, Config};
use actix_web_httpauth::extractors::AuthenticationError;
use actix_web_httpauth::middleware::HttpAuthentication;

// スコープ内のすべてのリクエストに対して実行される認証用の関数
async fn validator(req: ServiceRequest, auth: BasicAuth) -> Result<ServiceRequest, Error> {
    let user = auth.user_id().as_ref();
    let password = match auth.password() {
        Some(p) => p.as_ref().trim(),
        None => ""
    };

    if user == "foo" && password == "bar" {
        Ok(req)
    } else {
        Err(AuthenticationError::from(Config::default()).into())
    }
}

#[get("/")]
async fn greet(auth: BasicAuth) -> Result<String, Error> {
    // 認証情報が欲しいときは引数にBasicAuthを指定すれば良い
    let user = auth.user_id().as_ref();
    format!("Hello, {user}")
}


#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        let auth = HttpAuthentication::basic(validator);

        // wrap()メソッドでミドルウェアをスコープ全体に適用
        App::new()
            .wrap(auth)
            .service(greet)
    })
    .bind(("127.0.0.1", 8080))?
    .run()
    .await
}
```

## realmを指定する

上記のプログラムの場合、ユーザ名とパスワードのフォームに表示されるメッセージ（realm）は指定されていません。

この場合、メッセージの内容はクライアント依存（多くの場合メッセージなし）になります。

<br>

メッセージの内容を変更したい場合は、[Config::realm()メソッド](https://docs.rs/actix-web-httpauth/latest/actix_web_httpauth/extractors/basic/struct.Config.html#method.realm)を使用します。


```rust
async fn validator(req: ServiceRequest, credentials: BasicAuth) -> Result<ServiceRequest, Error> {
    let user = auth.user_id().as_ref();
    let password = match auth.password() {
        Some(p) => p.as_ref().trim(),
        None => ""
    };

    if user == "foo" && password == "bar" {
        Ok(req)
    } else {
        // realmを指定
        let config = Config::default().realm("ユーザ名とパスワードを入力してください。");
        Err(AuthenticationError::from(config).into())
    }
}
```

# 最後に

最初の方にも述べましたが、Basic認証はセキュリティ上好ましくない認証方式です。

以下のような認証方式が使用可能な場合は、そちらを実装することを推奨します。

- bcrypt暗号化に基づくフォーム認証
- APIトークンを使用したBearer認証（いわゆる「JWT認証」などもこれに含まれる）
- 事前のアクセストークン発行に基づくOAuth認証
- デバイス認証
- MFA (多要素認証)
