# String validator:
#   - checks is not empty
#   - checks starts with capital
#   - checks contains a single space surrounded by non-whitespace
#
# Parse don't validate => parseNonEmpty gives the caller access to the
# information it learned, while validateNonEmpty just throws it away


def is_not_empty(data):
    result = data.strip() != ""
    return result, "" if result else "is empty"


def starts_with_capital(data):
    result = data and data[0].isupper()
    return result, "" if result else "does not start with capital"


def has_single_space(data):
    result = data.strip().count(" ") == 1
    return result, "" if result else "does not have single space"


class Validator:
    def __init__(self, validator):
        self.validators = [validator]

    def __call__(self, data):
        reasons = []
        for validator in self.validators:
            result, reason = validator(data)
            if not result:
                reasons.append(reason)
        return len(reasons) == 0, reasons

    def where(self, validator):
        self.validators.append(validator)
        return self


class TestNotEmpty:
    def test_is_not_empty_passes_validation(self):
        result, reason = is_not_empty("hello")
        assert result
        assert not reason

    def test_is_empty_fails_validation(self):
        result, reason = is_not_empty("")
        assert not result
        assert reason

    def test_string_of_whitespace_fails_validation(self):
        result, reason = is_not_empty("   ")
        assert not result
        assert reason


class TestStartsWithCapital:
    def test_not_starting_with_capital_fails_validation(self):
        result, reason = starts_with_capital("hello")
        assert not result
        assert reason

    def test_starting_with_capital_passes_validation(self):
        result, reason = starts_with_capital("Hello")
        assert result
        assert not reason

    def test_empty_string_fails_capital_validation(self):
        result, reason = starts_with_capital("")
        assert not result
        assert reason


class TestSingleSpace:
    def test_not_containing_whitespace_fails_validation(self):
        result, reason = has_single_space("hello")
        assert not result
        assert reason

    def test_all_whitespace_fails_validation(self):
        result, reason = has_single_space("   ")
        assert not result
        assert reason

    def test_multiple_whitespace_in_middle_fails_validation(self):
        result, reason = has_single_space("a b c")
        assert not result
        assert reason

    def test_single_whitespace_in_middle_passes_validation(self):
        result, reason = has_single_space("a b")
        assert result
        assert not reason


def create_validator(*validators):
    validator_chain = Validator(validators[0])
    for i in range(1, len(validators)):
        validator_chain.where(validators[i])
    return validator_chain


class TestValidator:
    def test_can_combine_two_validators_that_pass_for_valid_data(self):
        validator = create_validator(starts_with_capital, has_single_space)
        assert validator("Hel lo")

    def test_can_combine_three_validators_that_pass_for_valid_data(self):
        validator = create_validator(
            starts_with_capital, has_single_space, is_not_empty
        )
        assert validator("Hel lo")

    def test_combine_two_validators_that_fail_on_second_for_invalid_data(self):
        validator = create_validator(starts_with_capital, has_single_space)
        result, reason = validator("Hello")
        assert not result

    def test_combine_two_validators_that_fail_on_first_for_invalid_data(self):
        validator = create_validator(starts_with_capital, has_single_space)
        result, reason = validator("hel lo")
        assert not result

    def test_can_get_reason_for_single_fail(self):
        validator = create_validator(starts_with_capital, has_single_space)
        result, reason = validator("Hello")
        assert reason == ["does not have single space"]

    def test_can_get_reasons_for_all_fails(self):
        validator = create_validator(starts_with_capital, has_single_space)
        result, reason = validator("hello")
        assert reason == ["does not start with capital", "does not have single space"]

    def test_reason_is_empty_on_pass(self):
        validator = create_validator(starts_with_capital, has_single_space)
        result, reason = validator("Hel lo")
        assert reason == []
