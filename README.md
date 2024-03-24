# Парсер языка Pascal
Парсер кода Pascal в AST дерево с помощью библиотеки pyparsing.
## Команда
3 курс, группа 8.1.
- Печенкин Павел
- Шевченко Даниил
- Барышев Артем
## Пример парсинга
Код:
```
Program pr1;
var
i : integer;
arr: array [1 .. 100] of integer;

function Mult10(a: integer):integer;
var y: integer;
begin
a:=a*10;
end;

BEGIN
i:=0;
while (i<5) do
begin
    arr[1]:=i;
    Write(arr[1]);
    i:=i+1;
end;

i:=Mult10(4);
WriteLn(i);

END.
```
AST дерево:
```
Program
├ pr1
├ var
│ ├ var_dec
│ │ ├ idents
│ │ │ └ i
│ │ └ integer
│ ├ arr_decl
│ │ ├ integer
│ │ ├ idents
│ │ │ └ arr
│ │ ├ 1 (int)
│ │ └ 100 (int)
│ └ function
│   ├ Mult10
│   ├ params
│   │ └ var_dec
│   │   ├ idents
│   │   │ └ a
│   │   └ integer
│   ├ integer
│   ├ var
│   │ └ var_dec
│   │   ├ idents
│   │   │ └ y
│   │   └ integer
│   └ Body
│     └ ...
│       └ :=
│         ├ a
│         └ *
│           ├ a
│           └ 10 (int)
└ Body
  └ ...
    ├ :=
    │ ├ i
    │ └ 0 (int)
    ├ while
    │ ├ <
    │ │ ├ i
    │ │ └ 5 (int)
    │ └ ...
    │   ├ :=
    │   │ ├ arr [1 (int)]
    │   │ └ i
    │   ├ call
    │   │ ├ Write
    │   │ └ arr [1 (int)]
    │   └ :=
    │     ├ i
    │     └ +
    │       ├ i
    │       └ 1 (int)
    ├ :=
    │ ├ i
    │ └ call
    │   ├ Mult10
    │   └ 4 (int)
    └ call
      ├ WriteLn
      └ i
```
