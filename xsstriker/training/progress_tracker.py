import time

class ProgressTracker:
    """Layer 4: Tracks progress and performance metrics during target training."""
    def __init__(self):
        self.start_time = time.time()
        self.requests_count = 0
        self.success_count = 0
        self.failures_count = 0
        self.false_positives = 0
        self.history = []

    def update(self, result):
        """Update tracker based on the result of an XSS attempt."""
        self.requests_count += 1
        if result == "success":
            self.success_count += 1
        elif result == "failure":
            self.failures_count += 1
        elif result == "false_positive":
            self.false_positives += 1

        self.history.append({
            "timestamp": time.time() - self.start_time,
            "requests": self.requests_count,
            "success_rate": self.success_rate()
        })

    def success_rate(self):
        """Returns the current success rate (percentage)."""
        if self.requests_count == 0:
            return 0
        return (self.success_count / self.requests_count) * 100

    def requests_per_second(self):
        """Returns the current processing speed."""
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0
        return self.requests_count / elapsed

    def display_stats(self):
        """Display live statistics (rich format placeholder)."""
        print(f"[*] Progress - Requests: {self.requests_count}, "
              f"Success Rate: {self.success_rate():.2f}%, "
              f"Requests/sec: {self.requests_per_second():.2f}")

if __name__ == "__main__":
    tracker = ProgressTracker()
    tracker.update("success")
    tracker.update("failure")
    tracker.display_stats()
