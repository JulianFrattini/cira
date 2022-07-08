from dataclasses import dataclass, field

@dataclass
class Parameter:
    id: str
    variable: str = None
    condition: str = None

@dataclass 
class Configuration:
    conditions: dict
    expected: dict

@dataclass
class Testsuite:
    conditions: list[Parameter] = field(default_factory=list)
    expected: list[Parameter] = field(default_factory=list)

    cases: list[Configuration] = field(default_factory=list)