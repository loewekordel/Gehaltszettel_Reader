"""
Betriebsratsumlage yearly handling
"""

from dataclasses import dataclass, field
import re


class ValueNotFoundError(Exception):
    """Error for Betriebsratsumlage value not found in text"""


@dataclass
class Betriebsratsumlage:
    """
    Betriebsratsumlage yearly handling
    """

    months: dict[int | str, float] = field(init=False, default_factory=dict)

    def __len__(self):
        return len(self.months)

    def get_value_from_text(self, month: int | str, text: str) -> float:
        """
        get Betriebsumlage value from text
        :param month: month of corresponding Betriebsumlage value
        :param text: text to be parsed for Betriebsumlage value
        :return: Betriebsumlage value
        """
        match = re.findall(r"841 [a-zA-Z. ]+ (\d+,\d+)", text)
        if not match:
            raise ValueNotFoundError("Betriebsumlage value not found")
        self.months[month] = sum((float(v.replace(",", ".")) for v in match))
        return self.months[month]

    @property
    def sum(self) -> float:
        """"
        calculate sum of all values of Betriebsratsumlage
        :return: Betriebsratsumlage sum
        """
        return sum(self.months.values())
