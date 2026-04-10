"""Betriebsratsumlage yearly handling."""

from dataclasses import dataclass, field


@dataclass
class Betriebsratsumlage:
    """Betriebsratsumlage yearly handling."""

    months: dict[int | str, float] = field(init=False, default_factory=dict)

    def __len__(self) -> int:
        """Number of months with recorded Betriebsratsumlage values.

        :return: number of months
        """
        return len(self.months)

    def add(self, month: int | str, value: float) -> None:
        """Record a Betriebsratsumlage value for a given month.

        :param month: month identifier
        :param value: Betriebsratsumlage value
        """
        self.months[month] = value

    @property
    def sum(self) -> float:
        """Calculate sum of all recorded Betriebsratsumlage values.

        :return: Betriebsratsumlage sum
        """
        return sum(self.months.values())
