from app.service.menu.schemas import MenuNode, MenuAction

class MenuBuildIndex:
    
    @staticmethod
    def build_index(
    node: MenuNode | MenuAction,
    parent_path: str | None = None,
    parent_crumbs: list[str] | None = None,
) -> dict[str, MenuNode | MenuAction]:
        """
        Рекурсивно обходит дерево и собирает индекс.
        
        Обрабатывает:
        - MenuNode (рекурсивно с детьми)
        - MenuAction (листовой элемент)
        - Списки (группировка кнопок)
        
        Args:
            node: Текущий узел дерева
            parent_path: Путь родительского узла
            parent_crumbs: Хлебные крошки родителя
            
        Returns:
            Словарь {path: MenuNode | MenuAction} для всех узлов дерева
        """
        # Формируем путь
        node.path = node.key if not parent_path else f'{parent_path}-{node.key}'
        node.parent_path = parent_path
        node.crumbs = (parent_crumbs or []) + [node.title]
        
        # Добавляем текущий узел в индекс
        index = {node.path: node}
        
        # Если это MenuNode с детьми — обрабатываем их
        if isinstance(node, MenuNode) and node.childrens:
            for child in node.childrens:
                index.update(MenuBuildIndex._process_child(child, node.path, node.crumbs))
        
        return index

    @staticmethod
    def _process_child(
        child: MenuNode | MenuAction | list,
        parent_path: str,
        parent_crumbs: list[str],
    ) -> dict[str, MenuNode | MenuAction]:
        """
        Обрабатывает один элемент из childrens.
        
        Элемент может быть:
        - MenuNode — рекурсивный вызов
        - MenuAction — добавление в индекс
        - list — группировка, итерируем по элементам
        """
        # Если это список (группа кнопок) — обрабатываем каждый элемент
        if isinstance(child, list):
            index = {}
            for item in child:
                index.update(MenuBuildIndex._process_child(item, parent_path, parent_crumbs))
            return index
        
        # Если это MenuAction — просто добавляем в индекс
        if isinstance(child, MenuAction):
            child.path = f'{parent_path}-{child.key}'
            child.parent_path = parent_path
            child.crumbs = parent_crumbs + [child.title]
            return {child.path: child}
        
        # Если это MenuNode — рекурсивный вызов
        if isinstance(child, MenuNode):
            return MenuBuildIndex.build_index(child, parent_path, parent_crumbs)
        
        # Неизвестный тип
        raise TypeError(f"Неизвестный тип элемента в childrens: {type(child)}")