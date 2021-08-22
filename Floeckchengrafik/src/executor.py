from application_stack_utils import StatementNode
from internals import env as internal_env, internals
import uuid

env = internal_env.copy()


class ComstructExecutor:
    def __init__(self, object_tree):
        global env
        for node in object_tree:
            self.walkTree(node, env)

    def walkTree(self, node, _env):

        if isinstance(node, StatementNode.MathNode):
            if node.type == "+":
                return self.walkTree(node.var1, _env) + self.walkTree(node.var2, _env)
            elif node.type == "-":
                return self.walkTree(node.var1, _env) - self.walkTree(node.var2, _env)
            elif node.type == "*":
                return self.walkTree(node.var1, _env) * self.walkTree(node.var2, _env)
            elif node.type == "/":
                return self.walkTree(node.var1, _env) / self.walkTree(node.var2, _env)
            elif node.type == "%":
                return self.walkTree(node.var1, _env) % self.walkTree(node.var2, _env)
        elif isinstance(node, StatementNode.EqualNode):
            return self.walkTree(node.var1, _env) == self.walkTree(node.var2, _env)
        elif isinstance(node, StatementNode.NotEqualNode):
            return self.walkTree(node.var1, _env) != self.walkTree(node.var2, _env)
        elif isinstance(node, StatementNode.GreaterThanNode):
            return self.walkTree(node.var1, _env) > self.walkTree(node.var2, _env)
        elif isinstance(node, StatementNode.GreaterOrEqualsThanNode):
            return self.walkTree(node.var1, _env) >= self.walkTree(node.var2, _env)
        elif isinstance(node, StatementNode.SmallerThanNode):
            return self.walkTree(node.var1, _env) < self.walkTree(node.var2, _env)
        elif isinstance(node, StatementNode.SmallerOrEqualsThanNode):
            return self.walkTree(node.var1, _env) <= self.walkTree(node.var2, _env)
        elif isinstance(node, StatementNode.VarAssignNode):
            _env[node.var_name] = self.walkTree(node.var_value, _env)
            return _env[node.var_name]
        elif isinstance(node, StatementNode.VarNode):
            return _env[node.var_name]
        elif isinstance(node, StatementNode.LiterallyNode):
            if node.walk_function is not None:
                node.walk_function(self.walkTree, node)
            return node.var
        elif isinstance(node, StatementNode.StoredProcedureNode):
            return node
        elif isinstance(node, StatementNode.ExecuteStoredProcedureNode):
            for stmt_node in node.exec.content:
                if type(stmt_node) == StatementNode.FunctionDescriptionNode:
                    node.description = stmt_node.attributes
                    break

            if node.description is None:
                node.description = []

            ret: StatementNode.GenericNode = StatementNode.LiterallyNode(0)

            for stmt_node in node.exec.content:
                can_return = False
                for item in node.description:
                    if item[0] == "returns":
                        can_return = True
                        break

                if stmt_node:
                    ret_evt = self.walkTree(stmt_node, _env)

                    if can_return:
                        ret = ret_evt

            return ret
        elif isinstance(node, StatementNode.FunctionDefinitionNode):
            return node
        elif isinstance(node, StatementNode.ClassDefinitionNode):
            return node
        elif isinstance(node, StatementNode.FunctionCallNode):
            processed_args = []
            node_call = _env[node.func_name].content

            for arg in node.args:
                processed_args.append(self.walkTree(arg, _env))
            if node_call == "internal":
                return self.walkTree(internals[node.func_name](processed_args), _env)

            for stmt_node in node_call.content:
                if type(stmt_node) == StatementNode.FunctionDescriptionNode:
                    node_call.description = stmt_node.attributes
                    break

            if node_call.description is None:
                node_call.description = []

            old_env = _env
            new_env = _env.copy()
            i = 0
            for elem in node_call.description:
                if elem[0] != "param":
                    continue
                try:
                    new_env[elem[1]] = processed_args[i]
                except IndexError:
                    new_env[elem[1]] = None
                i += 1

            env = new_env

            ret: StatementNode.GenericNode = StatementNode.LiterallyNode(0)
            for func_node in node_call.content:
                ret_evt = self.walkTree(func_node, _env)
                can_return = False
                for item in node_call.description:
                    if item[0] == "returns":
                        can_return = True
                        break

                if can_return:
                    if func_node:
                        ret = ret_evt

            env = old_env

            return ret

        elif isinstance(node, StatementNode.ClassInstanciacionNode):
            uid = uuid.uuid4().hex

            classnode: StatementNode.ClassDefinitionNode = _env[node.class_name]

            # old_env = _env.copy()
            # env = {}

            for stmt_node in classnode.content:
                if type(stmt_node) != StatementNode.VarAssignNode:
                    print("[EXEC] Tried to do something different than assigning a var inside a class.")
                    continue
                self.walkTree(stmt_node, _env[uid])

            # new_env = env.copy()
            # env = old_env
            # env[uid] = new_env

            return StatementNode.LiterallyNode(ClassClass(uid, _env[uid]))

        elif isinstance(node, StatementNode.ForLoopExecutorNode):
            ret: StatementNode.GenericNode = StatementNode.LiterallyNode(0)
            prev = None
            try:
                prev = _env[node.varname]
            except LookupError:
                pass
            for i in node.tgetfrm:
                _env[node.varname] = i
                ret = self.walkTree(StatementNode.ExecuteStoredProcedureNode(node.execute), _env)

            if prev is not None:
                _env[node.varname] = prev
            else:
                del _env[node.varname]

            return ret
        else:
            return node


class ClassClass:
    def __init__(self, uid, envrnmt):
        self.uid = uid
        self.env = envrnmt
