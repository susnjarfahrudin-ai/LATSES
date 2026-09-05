class ChangeDetector:
    def compare(self, old: object, new: object) -> dict[str, bool]:
        return {"changed": old != new}
