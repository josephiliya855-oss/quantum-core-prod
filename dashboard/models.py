from django.db import models

class XauUsdCandle(models.Model):
    timestamp = models.DateTimeField(unique=True)
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    high_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_price = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.IntegerField()

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"XAUUSD @ {self.timestamp.isoformat()}"

class AccountState(models.Model):
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=100000.00)
    equity = models.DecimalField(max_digits=15, decimal_places=2, default=100000.00)
    initial_capital = models.DecimalField(max_digits=15, decimal_places=2, default=100000.00)
    is_locked = models.BooleanField(default=False)

    def __str__(self):
        return f"AccountState(id={self.id}, balance={self.balance})"

class LedgerHistory(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    # Backwards-compatible nullable action field (some scripts still write action)
    action = models.CharField(max_length=20, null=True, blank=True)
    delta = models.DecimalField(max_digits=12, decimal_places=2)
    resulting_balance = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp} {self.action or ''} {self.delta:+} -> {self.resulting_balance}"
