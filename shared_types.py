from typing import Callable, List, Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
  from propagating_formula import PropagatingFormula

  DecisionLevel = int
  Literal = int
  Value = Union[int, float]
  Variable = int

  Brancher = Callable[[PropagatingFormula], Tuple[Variable, Value]]
  ConflictAnalyzer = Callable[[PropagatingFormula], Tuple[DecisionLevel, List[List[Literal]]]]