import csv
import os
from typing import List


class FileIterator:
    def __init__(self, source):
        self.file_list = []
        self.index = 0

        if isinstance(source, list):
            self.file_list = [os.path.abspath(p) for p in source]
        elif isinstance(source, str) and source.endswith(".csv"):
            self.file_list = self.read_csv(source)
        else:
            self.dir_path = os.path.abspath(source)
            self.file_list = [
                os.path.join(self.dir_path, f)
                for f in os.listdir(self.dir_path)
                if f.lower().endswith(".mp3")
            ]

    def read_csv(self, csv_path: str) -> List[str]:
        tracks = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                track_path = row.get("absolutepath") or row.get("abs_path")
                if track_path and track_path.strip():
                    tracks.append(track_path.strip())
        return tracks

    def __iter__(self):
        return self

    def __next__(self) -> str:
        while self.index < len(self.file_list):
            file_path = self.file_list[self.index]
            self.index += 1
            if file_path.lower().endswith(".mp3"):
                return file_path
        raise StopIteration

    def prev(self) -> str:
        self.index -= 2
        if self.index < 0:
            self.index = len(self.file_list) - 1
        return next(self)

    @property
    def file_list(self):
        return self._file_list

    @file_list.setter
    def file_list(self, value):
        self._file_list = value
