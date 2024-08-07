from dataclasses import dataclass


@dataclass(init=False)
class Balance:
    amount: int
    denom: str

    def __init__(self, amount, denom):
        self.amount = int(amount)
        self.denom = denom

    @property
    def value(self):
        return float(self.amount / 1000000 if self.denom == 'utia' else self.amount)
