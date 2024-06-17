from enum import Enum


class ClassificationStatus(str, Enum):
    RETIRED = 'R'
    DISQUALIFIED = 'D'
    EXCLUDED = 'E'
    WITHDRAWN = 'W'
    FAILED_TO_QUALIFY = 'F'
    NOT_CLASSIFIED = 'N'