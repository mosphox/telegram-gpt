from typing import Any


class Validators:
    @staticmethod
    def _validate_instance(instance: Any, value: Any) -> bool:
        """
        Check if the given value is an instance of the specified type.

        Args:
            instance (Any): The type to check against.
            value (Any): The value to validate.

        Returns:
            bool: True if value is an instance of the given type, False otherwise.
        """
        return isinstance(value, instance)

    @staticmethod
    def validate_str(value: Any) -> bool:
        """
        Validate that the value is a string.

        Args:
            value (Any): The value to check.

        Returns:
            bool: True if the value is a string, False otherwise.
        """
        return Validators._validate_instance(str, value)

    @staticmethod
    def validate_numeric(value: Any) -> bool:
        """
        Check if the value can be converted to a float (i.e., is numeric).

        Args:
            value (Any): The value to test.

        Returns:
            bool: True if the value is numeric, False otherwise.
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_range(margins: tuple[int | float, int | float], value: Any) -> bool:
        """
        Check if a numeric value falls within a given inclusive range.

        Args:
            margins (tuple[int | float, int | float]): A tuple representing (min, max) bounds.
            value (Any): The value to test.

        Returns:
            bool: True if the value is numeric and falls within the given range, False otherwise.
        """
        if Validators.validate_numeric(value):
            bottom_margin, top_margin = margins
            return bottom_margin <= float(value) <= top_margin

        return False
