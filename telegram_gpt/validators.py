class Validators:
    @staticmethod
    def _validate_instance(instance: Any, value: Any) -> bool:
        return isinstance(value, instance)

    @staticmethod
    def validate_str(value: Any) -> bool:
        return Validators._validate_instance(str, value)

    @staticmethod
    def validate_numeric(value: Any) -> bool:
        return Validators._validate_instance(int, value) or Validators._validate_instance(float, value)

    @staticmethod
    def validate_range(margins: tuple[int | float, int | float], value: Any) -> bool:
        if Validators.validate_numeric(value):
            bottom_margin, top_margin = margin

            if value > bottom_margin and value < top_margin:
                return True

        return False
