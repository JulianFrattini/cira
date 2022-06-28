from dataclasses import dataclass

@dataclass
class Label:
    id: str
    name: str
    begin: int
    end: int