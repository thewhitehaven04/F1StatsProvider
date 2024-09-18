from enum import StrEnum


class SessionIdentifier(StrEnum):
    RACE = 'Race'
    QUALIFYING = 'Qualifying'
    SPRINT = 'Sprint'
    SPRINT_QUALIFYING = 'Sprint Qualifying'
    SHOOTOUT = 'Sprint Shootout'
    FP1 = 'Practice 1'
    FP2 = 'Practice 2'
    FP3 = 'Practice 3'