# FireStackLang
FireStackLangは逆ポーランド記法をベースにして開発された言語です。

## 使い方
1. ファイルにプログラムを記述する。
2. `python interpreter.py (ファイル名)`を実行する。

## 型一覧
| 型名 | 説明 | 備考 |
| ---- | ---- | ---- |
| number | 整数と浮動小数を区別しない数値型 | 実体はPythonのfloat
| str | 文字列型 | クォーテーションは"のみ使用可能 |
| bool | 真偽値型(True/False) | Pythonに倣って頭文字は大文字とした |
| list | リスト型 | リテラルはなく、emplistやseqを使って作成する |
| dict | 辞書型 | リテラルはなく、empdictやdicsetを使って作成する |
| Variable | 変数型 | 変数そのものを表す型で、getやsetなどと共に使う |
| Program | プログラム型 | プログラムを{}で囲むことでコードブロックをif, for, execなどで使う値として使える |

## コマンド一覧
※使い方の()内は便宜上の引数名です。
### 入出力
| コマンド名 | 引数の型 | 返り値の型 | 使い方 | 説明 |
| ---- | ---- | ---- | ---- | ---- |
| input | 引数なし | string | `input` | 標準入力から文字列を受け取りスタックに積む |
| print | any | 返り値なし | `(value) print` | `value`の文字列表現を標準出力に出す |
| printsp | any | 返り値なし | `(value) printsp` | print + 最後に半角スペース |
| println | any | 返り値なし | `(value) println` | print + 最後に改行 |
| printstack | 引数なし | 返り値なし | `printstack` | スタックの内容を標準出力に出す |

### 演算
| コマンド名 | 引数の型 | 返り値の型 | 使い方 | 説明 |
| ---- | ---- | ---- | ---- | ---- |
| + | number, number | number | `(n1) (n2) +` | `n1`+`n2`の結果をスタックに積む |
| - | number, number | number | `(n1) (n2) -` | `n1`-`n2`の結果をスタックに積む |
| * | number, number | number | `(n1) (n2) *` | `n1`×`n2`の結果をスタックに積む |
| / | number, number | number | `(n1) (n2) /` | `n1`÷`n2`の結果をスタックに積む(ゼロ除算はエラー) |
| % | number, number | number | `(n1) (n2) %` | `n1`÷`n2`の剰余をスタックに積む(ゼロ除算はエラー) |
| > | number, number | bool | `(n1) (n2) >` | `n1`>`n2`ならTrue、そうでなければFalseをスタックに積む |
| < | number, number | bool | `(n1) (n2) <` | `n1`<`n2`ならTrue、そうでなければFalseをスタックに積む |
| >= | number, number | bool | `(n1) (n2) >=` | `n1`≧`n2`ならTrue、そうでなければFalseをスタックに積む |
| <= | number, number | bool | `(n1) (n2) <=` | `n1`≦`n2`ならTrue、そうでなければFalseをスタックに積む |
| == | any, any | bool | `(v1) (v2) ==` | `v1`と`v2`が等しければTrue、等しくなければFalseをスタックに積む |
| != | any, any | bool | `(v1) (v2) !=` | `v1`と`v2`が等しくなければTrue、等しければFalseをスタックに積む

### 文字列処理
| コマンド名 | 引数の型 | 返り値の型 | 使い方 | 説明 |
| ---- | ---- | ---- | ---- | ---- |
| concat | str, str | str | `(s1) (s2) concat` | `s1`の末尾に`s2`を文字列結合した結果をスタックに積む |
| tonum | str | number | `(string) tonum` | `string`を数値として解釈した結果をスタックに積む(解釈できない場合はエラー)
| tostr | any | str | `(value) tostr` | `value`の文字列表現をスタックに積む |

### 変数
| コマンド名 | 引数の型 | 返り値の型 | 使い方 | 説明 |
| ---- | ---- | ---- | ---- | ---- |
| set | Variable, any | 返り値なし | `(V1) (v2) set` | 変数`V1`に`v2`を格納する |
| rset | any, Variable | 返り値なし | `(v1) (V2) rset` | 変数`V2`に`v1`を格納する |
| get | Variable | 変数の値の型 | `(Var) get` | 変数`Var`から値を取得する(変数が存在しない場合はエラー)

### 制御
| コマンド名 | 引数の型 | 返り値の型 | 使い方 | 説明 |
| ---- | ---- | ---- | ---- | ---- |
| if | bool, Program | 返り値なし | `(b1) (P2) if` | `b1`がTrueなら`P2`を実行する |
| unless | bool, Program | 返り値なし | `(b1) (P2) unless` | `b1`がFalseなら`P2`を実行する |
| for | Variable, number, number, number, Program | 返り値なし | `(V1) (n2) (n3) (n4) (P5) for` | 変数`V1`について`n2`から`n3`まで`n4`ずつ増やしながら`P5`をループ実行する |
| exec | Program | 返り値なし | `(Prog) exec` | `Prog`を実行する |

※プログラムが正常に解析できなかったり、実行中にエラーが発生したりといった場合はエラーとなる。

### list
| コマンド名 | 引数の型 | 返り値の型 | 使い方 | 説明 |
| ---- | ---- | ---- | ---- | ---- |
| emplist | 引数なし | list | `emplist` | 空のリストをスタックに積む
| seq | number, number, number | list | `(n1) (n2) (n3) seq` | `n1`から`n2`まで`n3`ずつ増やしながら末尾に追加したリストをスタックに積む |
| put | list, any | list | `(l1) (v2) put` | `l1`のリストの末尾に`v2`のオブジェクトを追加した結果をスタックに積む |
| foreach | Variable, list, Program | 返り値なし | `(V1) (l2) (P3) foreach` | `l2`の中身を先頭から順番に変数`V1`に代入しながら`P3`をループ実行する |
| len | list | number | `(li) len`  | `li`の長さをスタックに積む | 
| getat | list, number | 指定された要素の型 | `(l1) (n2) getat` | `l1`の`n2`番目の要素をスタックに積む |
| setat | list, number, any | list | `(l1) (n2) (v3) setat` | `l1`の`n2`番目の要素を`v3`に書き換えたリストをスタックに積む |
| map | list, Program | list | `(l1) (P2) map` | `l1`の各要素に対して先頭から順に`P2`を実行した結果得られたリストをスタックに積む |
| filter | list, Program | list | `(l1) (P2) filter` | `l1`の各要素に対して先頭から順に`P2`を実行した結果、Trueが得られた要素のリストをスタックに積む(順番は維持される) |

### dict
| コマンド名 | 引数の型 | 返り値の型 | 使い方 | 説明 |
| ---- | ---- | ---- | ---- | ---- |
| empdict | 引数なし | dict | `empdict` | 空の辞書をスタックに積む |
| dicget | dict, str | 指定された値の型 | `(d1) (s2) dicget` | `d1`において`d2`というキーで格納された値をスタックに積む |
| dicset | dict, str, any | dict | `(d1) (s2) (v3) dicset` | `d1`において`s2`というキーで格納された値を`v3`で書き換えた辞書をスタックに積む |
| keys | dict | list | `(di) keys` | `di`のキーを列挙したリストをスタックに積む |
| values | dict | list | `(di) values` |  `di`の値を列挙したリストをスタックに積む |

### 特殊
| コマンド名 | 引数の型 | 返り値の型 | 使い方 | 説明 |
| ---- | ---- | ---- | ---- | ---- |
| # | any | 返り値なし | `(value) #` | `value`を破棄する |
| dup | any | スタックの一番上の値の型×2 | `(value) dup` | `value`を2つに増やす | 
