"""Module"""


class DDIProcessor:

    def __init__(self):
        self.selected_fields = [
            'rt', 'ruleName', 'reason', 'evtSubCat', 'Serverity',
            'request', 'cs8', 'fname', 'fileHash', 'requestClientApplication',
            'src', 'dst', 'spt', 'dpt'
        ]

    def set_selected_fields(self, selected_fields):
        self.selected_fields = selected_fields

    def get_selected_fields(self):
        return self.selected_fields

    def filter_all_hits_by_selected_fields(self, hits):
        filtered_hits = []
        for hit in hits:
            doc = {}
            for field in self.selected_fields:
                if field in hit:
                    doc[field] = hit[field]
                else:
                    doc[field] = None
            filtered_hits.append(doc)

        return filtered_hits


if __name__ == '__main__':
    dp = DDIProcessor()
    print(dp.get_selected_fields())
