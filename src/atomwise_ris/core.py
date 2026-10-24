"""Convenience exports; scientific implementations live in named modules."""
from .utils.provenance import write_json,sha256,source_versions
from .responses.model import ResponseModel
from .data.scenario import Scenario
from .channels.precoding import precoder,C0
from .evaluation.evaluator import Evaluator
