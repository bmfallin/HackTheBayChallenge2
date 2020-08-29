from enum import IntEnum

class Properties(IntEnum):
    UNKNOWN = 0
    AIR_TEMPERATURE = 1
    ALKALINITY = 2
    AMMONIA_NITROGEN = 3
    CHLOROPHYLL = 4
    CONDUCTIVITY = 5
    DISSOLVED_OXYGEN = 6
    E_COLI = 7
    ENTEROCOCCUS = 8
    NITRATE_NITROGEN = 9
    ORTHOPHOSPHATE = 10
    PH = 11
    PHOSPHORUS = 12
    SALINITY = 13
    TOTAL_DEPTH = 14
    TOTAL_DISSOLVED_SOLIDS = 15
    TOTAL_NITROGEN = 16
    TOTAL_SUSPENDED_SOLIDS = 17
    TURBIDITY = 18
    WATER_TEMPERATURE  = 19

    def __str__(self):
        if self == Properties.E_COLI:
            return "E.Coli"

        if self == Properties.PH:
            return "pH"

        return self.name.replace("_", " ").title()


class Organization(IntEnum):
    UNKNOWN = 0
    CMC = 1
    CBP = 2


class DateRangeType(IntEnum):
    UNKNOWN = 0
    BETWEEN_DATE_RANGE = 1
    OVERLAPPING_DATE_RANGE = 2

    def __str__(self):
        return self.name.replace("_", " ").capitalize()