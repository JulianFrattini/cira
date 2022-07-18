from dataclasses import dataclass, field

@dataclass
class Parameter:
    id: str
    variable: str = None
    condition: str = None

    def __eq__(self, other: 'Parameter') -> bool:
        return self.variable == other.variable and self.condition == other.condition

@dataclass
class Suite:
    conditions: list[Parameter] = field(default_factory=list)
    expected: list[Parameter] = field(default_factory=list)

    cases: list[dict] = field(default_factory=list)

    def __eq__(self, other: 'Suite') -> bool:
        # maintain a map which associates the parameters of one test suite to another
        eq_map = {}

        # check that both the list of conditions and expected parameters are equal in this and the other object
        for param_list in ["conditions", "expected"]:
            if len(getattr(self, param_list)) != len(getattr(other, param_list)):
                return False

            for param in getattr(self, param_list):
                equivalent = [candidate for candidate in getattr(other, param_list) if candidate == param]

                if len(equivalent) != 1:
                    return False
                else:
                    eq_map[equivalent[0].id] = param.id

        # check that the list of test case configurations is equal in this and the other object
        if len(self.cases) != len(other.cases):
            return False
        # map the test cases of the other suite to the same ids of this test suite
        mapped_cases = [{eq_map[param_id]: tc[param_id] for param_id in tc} for tc in other.cases]
        for case in self.cases:
            equivalent = [candidate for candidate in mapped_cases if case == candidate]

            if len(equivalent) != 1:
                return False

        return True