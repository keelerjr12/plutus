from prettytable.prettytable import PrettyTable

class TableComponentModel:
    def __init__(self, header, rows):
        self.header = header
        self.rows = rows

class TableComponentView:

    def __init__(self, model):
        self.table = PrettyTable()
        self.model = model

    def show(self):
        self.table.field_names = self.model.header
        self.table.add_rows(self.model.rows)

        print(self.table)