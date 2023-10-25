import ast
class DataclassFinder(list):
    def __init__(self, file):
        super().__init__()
        
        tree = self._parse_file(file)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and self._has_dataclass_decorator(node):
                dataclass = self._parse_dataclass(node)
                self.append(dataclass)

    def _parse_file(self, file):
            return ast.parse(file)

    def _has_dataclass_decorator(self, class_node):
        decorators = {d.id for d in class_node.decorator_list}
        return "dataclass" in decorators

    def _parse_dataclass(self, class_node):
        dataclass = {"name": class_node.name, "elements": []}
        for class_element in class_node.body:
            if isinstance(class_element, ast.AnnAssign):
                element = self._parse_class_element(class_element)
                dataclass["elements"].append(element)
        return dataclass

    def _parse_class_element(self, class_element):
        element = {"name": class_element.target.id, "type": None, "default": None, "help": None}
        if isinstance(class_element.annotation, ast.Name):
            element["type"] = class_element.annotation.id
        if class_element.value and isinstance(class_element.value, ast.Call):
            for keyword in class_element.value.keywords:
                if keyword.arg == 'default':
                    element["default"] = ast.literal_eval(keyword.value)
                elif keyword.arg == "metadata":
                    element["help"] = ast.literal_eval(keyword.value)["help"]
        return element
