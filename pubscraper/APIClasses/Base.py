class Base:
    def get_publications_by_author(self, author_name: str, rows: int = 10):
        pass

    def get_name(self):
        class_name = type(self).__name__
        return class_name
