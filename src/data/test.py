from dataclasses import dataclass, field

@dataclass
class Parameter:
    id: str
    variable: str = None
    condition: str = None

    def __eq__(self, other: 'Parameter') -> bool:
        return self.variable == other.variable and self.condition == other.condition

@dataclass 
class Configuration:
    conditions: dict
    expected: dict

    def __eq__(self, other: 'Configuration') -> bool:
        return False

@dataclass
class Testsuite:
    conditions: list[Parameter] = field(default_factory=list)
    expected: list[Parameter] = field(default_factory=list)

    cases: list[Configuration] = field(default_factory=list)