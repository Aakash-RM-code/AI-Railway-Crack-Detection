class StatisticsManager:

    def __init__(self):

        self.small = 0
        self.medium = 0
        self.large = 0
        self.broken = 0
        self.total = 0

    def update(self, class_name):

        self.total += 1

        # YOLO model names use spaces ("small crack"); some older callers used
        # underscores. Normalize so counters always increment.
        name = (class_name or "").strip().lower().replace("_", " ")

        if name == "small crack":
            self.small += 1

        elif name == "medium crack":
            self.medium += 1

        elif name == "large crack":
            self.large += 1

        elif name == "broken chain":
            self.broken += 1

    def get_stats(self):

        return {
            "total": self.total,
            "small": self.small,
            "medium": self.medium,
            "large": self.large,
            "broken": self.broken
        }
    def reset(self):

        self.small = 0
        self.medium = 0
        self.large = 0
        self.broken = 0
        self.total = 0