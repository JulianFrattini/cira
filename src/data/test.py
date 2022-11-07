from dataclasses import dataclass, field, asdict
from tabulate import tabulate


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

    def to_dict(self) -> dict:
        """Convert a dataclass object into a simple dictionary

        returns: test suite as a dictionary"""
        return asdict(self)

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

    def __repr__(self):
        """Represent the test suite as a string table.

        returns: test suite as a string table that is printed via tabulated"""
        # arrange the header of the table containing the 'id' column, the variables of the conditions, and the variables of the expected outcomes
        headers = ['id'] + [param.variable for param in self.conditions] + [param.variable for param in self.expected]
        # define the index where the conditions end and the expected outcomes begin
        index_expected = len(self.conditions)+1
        # insert pipes (representing vertical lines) between the index column, the condition columns, and the expected outcomes columns
        headers[1] = '| '+headers[1]
        headers[index_expected] = '| '+headers[index_expected]

        # convert each test case into a string representing the row
        data = [([index+1] + get_conditions(case, self.conditions+self.expected, index_expected-1)) for index, case in enumerate(self.cases)]

        return tabulate(data, headers=headers)

def get_conditions(configuration: dict, parameters: list[Parameter], expected_index: int) -> list[str]:
    """Converts a test case into a list of strings containing the condition of each parameter with the respective boolean prefix (i.e., 'not <condition>' if that parameter is False in the given configuration.

    parameters:
        configuration -- dictionary mapping each parameter id to a boolean value
        parameters -- list of both input and output parameters
        expected_index -- number of condition parameters +1

    returns: list of parameter conditions in the configuration"""
    # concatenate the conditions of the condition parameters and the outcome parameters
    row = [('' if configuration[param.id] else 'not ') + param.condition for param in parameters]
    # add pipes in the beginnning (to represent the vertical line between the id column and all other columns) as well as between conditions and expected columns
    row[0] = '| '+row[0]
    row[expected_index] = '| '+row[expected_index]
    return row


def from_dict(dict_suite: dict) -> Suite:
    """Convert a test suite into an actual Suite object. This will mainly parse the conditions and expected parameters into actual Parameter objects.

    parameters:
        dict_suite -- test suite as a dictionary

    returnst test suite as a Suite"""
    conditions = [Parameter(id=c['id'], variable=c['variable'], condition=c['condition']) for c in dict_suite['conditions']]
    expected = [Parameter(id=c['id'], variable=c['variable'], condition=c['condition']) for c in dict_suite['expected']]

    return Suite(conditions=conditions, expected=expected, cases=dict_suite['cases'])
