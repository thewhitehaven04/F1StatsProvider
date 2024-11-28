
from enum import StrEnum


class ClassificationStatus(StrEnum):
    RETIRED = 'R'
    DISQUALIFIED = 'D'
    EXCLUDED = 'E'
    WITHDRAWN = 'W'
    FAILED_TO_QUALIFY = 'F'
    NOT_CLASSIFIED = 'N'
