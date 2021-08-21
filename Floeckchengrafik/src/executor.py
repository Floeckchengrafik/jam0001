from application_stack_utils import StatementNode
from internals import env as internal_env, internals


env = internal_env


class ComstructExecutor:
    def __init__(self, object_tree):
        for node in object_tree:
            self.walkTree(node)

    def walkTree(self, node):
        global env

        if isinstance(node, StatementNode.MathNode):
            if node.type == "+":
                return self.walkTree(node.var1) + self.walkTree(node.var2)
            elif node.type == "-":
                return self.walkTree(node.var1) - self.walkTree(node.var2)
            elif node.type == "*":
                return self.walkTree(node.var1) * self.walkTree(node.var2)
            elif node.type == "/":
                return self.walkTree(node.var1) / self.walkTree(node.var2)
            elif node.type == "%":
                return self.walkTree(node.var1) % self.walkTree(node.var2)
        elif isinstance(node, StatementNode.EqualNode):
            return self.walkTree(node.var1) == self.walkTree(node.var2)
        elif isinstance(node, StatementNode.NotEqualNode):
            return self.walkTree(node.var1) != self.walkTree(node.var2)
        elif isinstance(node, StatementNode.GreaterThanNode):
            return self.walkTree(node.var1) > self.walkTree(node.var2)
        elif isinstance(node, StatementNode.GreaterOrEqualsThanNode):
            return self.walkTree(node.var1) >= self.walkTree(node.var2)
        elif isinstance(node, StatementNode.SmallerThanNode):
            return self.walkTree(node.var1) < self.walkTree(node.var2)
        elif isinstance(node, StatementNode.SmallerOrEqualsThanNode):
            return self.walkTree(node.var1) <= self.walkTree(node.var2)
        elif isinstance(node, StatementNode.VarAssignNode):
            env[node.var_name] = self.walkTree(node.var_value)
            return self.walkTree(node.var_value)
        elif isinstance(node, StatementNode.VarNode):
            return env[node.var_name]
        elif isinstance(node, StatementNode.LiterallyNode):
            return node.var
        elif isinstance(node, StatementNode.FunctionDefinitionNode):
            return self.walkTree(node.content)  # TODO
        elif isinstance(node, StatementNode.FunctionCallNode):
            if env[node.func_name].content == "internal":
                return internals[node.func_name](node.args)
            ret: StatementNode.GenericNode = StatementNode.LiterallyNode(0)
            for func_node in env[node.func_name].content.content:
                ret = self.walkTree(func_node)
            return ret
