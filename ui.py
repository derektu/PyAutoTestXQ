import pywinauto

"""
TreeViewExtension: extend treeview function
"""
class TreeViewExtension():
    def __init__(self, treeview):
        self.treeview = treeview

    def get_child_paths(self, root_path):
        """
        Return child nodes of root_path as an array of nodepath
        :param root_path: path of the root node, defined as a list of string, for example ['技術指標'] or ['XS指標', '系統']
        return an array of list of string, for example [ ['技術指標', 'RSI], ['XS指標', '系統', '主圖指標', 'EMA']] 
        """    
        all_paths = []
        root_node = self.treeview.get_item(root_path)
        self.__traverse_children(all_paths, root_node, root_path)
        return all_paths

    def __traverse_children(self, all_paths, current_node, current_path):
        # print(f"current_path={','.join(current_path)}")
        if len(current_node.children()) == 0:
            all_paths.append(current_path)
        for child_node in current_node.children():
            # print(f"len of [{child_node.text()}] = {len(child_node.children())}")
            child_path = current_path.copy()
            child_path.append(child_node.text())
            self.__traverse_children(all_paths, child_node, child_path)


