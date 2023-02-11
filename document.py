import json


class Document:
    def __init__(self, file_path):
        with open(file_path, "r") as f:
            file_data = json.load(f)

        self.n_files = len(file_data)
        self.fact_names, self.fact_info = [], []

        for data in file_data:
            if data["name"] and data["name"].split(",")[0] not in self.fact_names:
                self.fact_names.append(data["name"].split(",")[0])
                info = {k: v for k, v in data.items() if k != "name"}
                if "content" not in info.keys():
                    info["content"] = None
                self.fact_info.append(info)

    def shard_document(self, start_idx, end_idx):
        fact_names, fact_info = [], []
        for i in range(start_idx, end_idx + 1):
            fact_names.append(self.fact_names[i])
            fact_info.append(self.fact_info[i])
        return fact_names, fact_info
