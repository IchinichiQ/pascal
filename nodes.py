from abc import ABC, abstractmethod
from typing import Callable, Tuple, Optional, Union
from enum import Enum
import inspect

class AstNode(ABC):
    def __init__(self, row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__()
        self.row = row
        self.line = line
        for k, v in props.items():
            setattr(self, k, v)

    @property
    def childs(self) -> Tuple['AstNode', ...]:
        return ()

    @abstractmethod
    def __str__(self) -> str:
        pass

    @property
    def tree(self) -> [str, ...]:
        res = [str(self)]
        childs_temp = self.childs
        for i, child in enumerate(childs_temp):
            ch0, ch = '├', '│'
            if i == len(childs_temp) - 1:
                ch0, ch = '└', ' '
            res.extend(((ch0 if j == 0 else ch) + ' ' + s for j, s in enumerate(child.tree)))
        return res

    def __getitem__(self, index):
        return self.childs[index] if index < len(self.childs) else None


class ExprNode(AstNode):
    pass

# Значение переменной и ее типа
class LiteralNode(ExprNode):
    def __init__(self, literal: str,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.literal = literal
        self.value = eval(literal)

    def __str__(self) -> str:
        return '{0} ({1})'.format(self.literal, type(self.value).__name__)

# Название переменной
class IdentNode(ExprNode):
    # k,j..
    def __init__(self, name: str, row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.name = str(name)

    def __str__(self) -> str:
        return str(self.name)


# Элементы массива
class ArrayIdentNode(ExprNode):
    def __init__(self, name: IdentNode, literal: LiteralNode, row: Optional[int] = None, line: Optional[int] = None,
                 **props):
        super().__init__(row=row, line=line, **props)
        self.name = name
        self.literal = literal

    def __str__(self) -> str:
        return '{0} [{1}]'.format(self.name, self.literal)

class BinOp(Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIVISION = '/'
    DIV = 'div'
    MOD = 'mod'
    GE = '>='
    LE = '<='
    NE = '<>'
    EQ = '='
    GT = '>'
    LT = '<'
    LOGICAL_AND = 'and'
    LOGICAL_OR = 'or'

# Бинарная операция
class BinOpNode(ExprNode):
    def __init__(self, op: BinOp, arg1: ExprNode, arg2: ExprNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2

    @property
    def childs(self) -> Tuple[ExprNode, ExprNode]:
        return self.arg1, self.arg2

    def __str__(self) -> str:
        return str(self.op.value)


class StmtNode(ExprNode):
    pass

# Список переменных определенного типа
class IdentListNode(StmtNode):
    def __init__(self, *idents: Tuple[IdentNode, ...], row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.idents = idents

    @property
    def childs(self) -> Tuple[ExprNode, ...]:
        return self.idents

    def __str__(self) -> str:
        return "idents"


# Тип переменной или списка переменных
class TypeSpecNode(StmtNode):
    def __init__(self, name: str, row: Optional[int] = None, line: Optional[int] = None, **props):
        super(TypeSpecNode, self).__init__(row=row, line=line, **props)
        self.name = name

    def __str__(self) -> str:
        return self.name


class VarDeclNode(StmtNode):
    def __init__(self, ident_list: IdentListNode, vars_type: TypeSpecNode,  # *vars_list: Tuple[AstNode, ...],
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.ident_list = ident_list
        self.vars_type = vars_type

    @property
    def childs(self) -> Tuple[ExprNode, ...]:
        return (self.ident_list,) + (self.vars_type,)

    def __str__(self) -> str:
        return 'var_dec'

# Объявление массива
class ArrayDeclNode(StmtNode):
    def __init__(self, name: Tuple[AstNode, ...],
                 from_: LiteralNode, to_: LiteralNode, vars_type: TypeSpecNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        # Имя массив
        self.name = name
        # Первый индекс
        self.from_ = from_
        # Последний индекс
        self.to_ = to_
        # Тип значений массива
        self.vars_type = vars_type

    @property
    def childs(self) -> Tuple[ExprNode, ...]:
        # return self.vars_type, (*self.vars_list)
        return (self.vars_type,) + (self.name,) + (self.from_,) + (self.to_,)

    def __str__(self) -> str:
        return 'arr_decl'

# Раздел описания переменных
class VarsDeclNode(StmtNode):
    def __init__(self, *var_decs: Tuple[VarDeclNode, ...],
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.var_decs = var_decs

    @property
    def childs(self) -> Tuple[ExprNode, ...]:
        return self.var_decs

    def __str__(self) -> str:
        return 'var'

# Вызов функции или процедуры
class CallNode(StmtNode):
    def __init__(self, func: IdentNode, *params: Tuple[ExprNode],
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.func = func
        self.params = params

    @property
    def childs(self) -> Tuple[IdentNode, ...]:
        # return self.func, (*self.params)
        return (self.func,) + self.params

    def __str__(self) -> str:
        return 'call'


# Оператор присваивания значения
class AssignNode(StmtNode):
    def __init__(self, var,
                 val: ExprNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.var = var
        self.val = val

    @property
    def childs(self):
        return self.var, self.val

    def __str__(self) -> str:
        return ':='


# Оператор if
class IfNode(StmtNode):
    def __init__(self, cond: ExprNode, then_stmt: StmtNode, else_stmt: Optional[StmtNode] = None,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode, Optional[StmtNode]]:
        return (self.cond, self.then_stmt) + ((self.else_stmt,) if self.else_stmt else tuple())

    def __str__(self) -> str:
        return 'if'

# Цикл while
class WhileNode(StmtNode):
    def __init__(self, cond: ExprNode, stmt_list: StmtNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.cond = cond
        self.stmt_list = stmt_list

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode, Optional[StmtNode]]:
        return (self.cond, self.stmt_list)

    def __str__(self) -> str:
        return 'while'

# Цикл repeat
class RepeatNode(StmtNode):
    def __init__(self, stmt_list: StmtNode, cond: ExprNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.stmt_list = stmt_list
        self.cond = cond

    @property
    def childs(self) -> Tuple[ExprNode, StmtNode, Optional[StmtNode]]:
        return (self.stmt_list, self.cond)

    def __str__(self) -> str:
        return 'repeat'

# Цикл for
class ForNode(StmtNode):
    def __init__(self, init: Union[StmtNode, None],
                 to,
                 body: Union[StmtNode, None],
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        # Начальное значение
        self.init = init if init else _empty
        # Конечно значение
        self.to = to
        self.body = body if body else _empty

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return self.init, self.to, self.body

    def __str__(self) -> str:
        return 'for'

# Список выражений
class StmtListNode(StmtNode):
    def __init__(self, *exprs: StmtNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.exprs = exprs

    @property
    def childs(self) -> Tuple[StmtNode, ...]:
        return self.exprs

    def __str__(self) -> str:
        return '...'

# Тело с выражениями
class BodyNode(ExprNode):
    def __init__(self, body: Tuple[StmtNode, ...],
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.body = body

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return (self.body,)

    def __str__(self) -> str:
        return 'Body'

# Параметры функции или процедуры
class ParamsNode(StmtNode):
    def __init__(self, *vars_list: VarDeclNode,
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.vars_list = vars_list if vars_list else _empty

    @property
    def childs(self) -> Tuple[ExprNode, ...]:
        return self.vars_list

    def __str__(self) -> str:
        return 'params'

class ProgramNode(ExprNode):
    def __init__(self, prog_name: Tuple[AstNode, ...], vars_decl: Tuple[AstNode, ...],
                 stmt_list: Tuple[AstNode, ...],
                 row: Optional[int] = None, line: Optional[int] = None, **props):
        super().__init__(row=row, line=line, **props)
        self.prog_name = prog_name
        self.vars_decl = vars_decl
        self.stmt_list = stmt_list

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return (self.prog_name,) + (self.vars_decl,) + (self.stmt_list,)

    def __str__(self) -> str:
        return 'Program'

# Объявление процедуры
class ProcedureDeclNode(ExprNode):
    def __init__(self, *args, **props):
        super().__init__(row=_empty, line=_empty, **props)
        self.proc_name = args[0]
        # 4 аргумента, если процедура с параметрами
        if(len(args) == 4):
            self.params = args[1]
            self.vars_decl = args[2]
            self.stmt_list = args[3]
        else:
            self.params = _empty
            self.vars_decl = args[1]
            self.stmt_list = args[2]

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return (self.proc_name,) + (self.params,) + (self.vars_decl,) + (self.stmt_list,)


    def __str__(self) -> str:
        return 'procedure'


# Ообъявление функции
class FunctionDeclNode(ExprNode):
    def __init__(self,*args,**props):
        super().__init__(row=_empty, line=_empty, **props)
        self.proc_name = args[0]
        # 5 аргументов, если функция с параметрами
        if (len(args) == 5):
            self.params = args[1]
            self.returning_type = args[2]
            self.vars_decl = args[3]
            self.stmt_list = args[4]
        else:
            self.params = _empty
            self.returning_type = args[1]
            self.vars_decl = args[2]
            self.stmt_list = args[3]

    @property
    def childs(self) -> Tuple[AstNode, ...]:
        return (self.proc_name,) + (self.params,) + (self.returning_type,) + (self.vars_decl,) + (self.stmt_list,)

    def __str__(self) -> str:
        return 'function'


_empty = StmtListNode()
