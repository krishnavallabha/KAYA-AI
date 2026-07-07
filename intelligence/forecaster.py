"""
FlowSense Role 2 - Fabrication-to-Delivery Forecaster

Bypasses static vendor promises with a probabilistic model. Treats the
true delivery date as a latent Normal random variable and does
sequential Bayesian (Normal-Normal conjugate) updating as new evidence
arrives: fabrication stage signals, the Material Tracker's reconciled
ETA, and external disruption flags. Each source of evidence enters as a
noisy observation with its own variance, so a low-confidence email nudges
the posterior less than a high-confidence Bill of Lading.

Why conjugate Normal-Normal instead of pulling in Prophet/PyMC as a hard
dependency: with one evolving order (not a long historical time series
per SKU) a full time-series model is overkill and brittle to stand up in
a demo. The math below - precision-weighted combination of prior and
likelihood - IS Bayesian updating, just the closed-form case, which is
also exactly what Prophet's changepoint model and a PyMC linear-Gaussian
model reduce to for a single latent date. Swapping in Prophet for
per-vendor historical time series (once real multi-shipment history
exists) is a natural v2, and this module's public interface
(`forecast()` returning mean/CI/delay probability) would not need to
change.

Output: forecast date, a confidence interval, and an explicit delay
probability - the three things Problem 2 asks for.
"""

import math
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scipy.stats import norm

# Baseline days-of-uncertainty for a hypothetically perfectly reliable
# vendor (reliability score = 1.0). Less reliable vendors scale this up.
BASE_PRIOR_STD_DAYS = 3.0
UNRELIABILITY_STD_SCALE = 10.0

# Mean-shift (days) and observation-std implied by each fabrication stage,
# reflecting how much schedule risk remains at that stage of production.
FABRICATION_STAGE_SIGNAL = {
    "not_started":          {"shift_days": 9.0,  "obs_std": 6.0},
    "in_fabrication":       {"shift_days": 2.0,  "obs_std": 4.0},
    "fabrication_complete": {"shift_days": -2.0, "obs_std": 2.5},
    "shipped":              {"shift_days": -5.0, "obs_std": 1.5},
    "in_transit":           {"shift_days": -3.0, "obs_std": 1.5},
    "delivered":            {"shift_days": -30.0, "obs_std": 0.5},
}

# A tracker-reconciled ETA observation's implied std shrinks as tracker
# confidence rises (a highly-confident reconciled signal is more precise).
def tracker_eta_obs_std(tracker_confidence: float) -> float:
    return max(1.0, 2.0 + (1.0 - tracker_confidence) * 8.0)

DISRUPTION_SHIFT_DAYS = {
    "weather": 4.0,
    "port_congestion": 6.0,
    "customs_delay": 5.0,
    "carrier_shortage": 3.0,
}


def _to_ordinal(date_str: str) -> int:
    return datetime.strptime(date_str, "%Y-%m-%d").toordinal()


def _from_ordinal(ordinal: float) -> str:
    return datetime.fromordinal(round(ordinal)).strftime("%Y-%m-%d")


class DeliveryForecaster:
    def __init__(self):
        # order_id -> {"mean": ordinal_float, "var": float, "trace": [...]}
        self._posterior = {}

    def _get_or_init_prior(self, order: dict) -> dict:
        if order["order_id"] in self._posterior:
            return self._posterior[order["order_id"]]

        promised_ordinal = _to_ordinal(order["promised_date"])
        reliability = order.get("vendor_reliability", 0.75)
        prior_std = BASE_PRIOR_STD_DAYS + (1 - reliability) * UNRELIABILITY_STD_SCALE
        state = {
            "mean": float(promised_ordinal),
            "var": prior_std ** 2,
            "trace": [
                f"Prior: vendor '{order.get('vendor', '?')}' reliability={reliability:.2f} "
                f"-> prior std={prior_std:.1f} days centered on promised date "
                f"{order['promised_date']}."
            ],
        }
        self._posterior[order["order_id"]] = state
        return state

    @staticmethod
    def _bayes_update(prior_mean, prior_var, obs_mean, obs_var):
        """Closed-form Normal-Normal Bayesian update (precision-weighted
        average). This is the textbook Bayesian updating step: posterior
        precision = sum of precisions, posterior mean = precision-weighted
        mean."""
        prior_precision = 1.0 / prior_var
        obs_precision = 1.0 / obs_var
        post_precision = prior_precision + obs_precision
        post_var = 1.0 / post_precision
        post_mean = (prior_mean * prior_precision + obs_mean * obs_precision) * post_var
        return post_mean, post_var

    def update_with_fabrication_signal(self, order: dict):
        state = self._get_or_init_prior(order)
        stage = order.get("fabrication_stage", "in_fabrication")
        signal = FABRICATION_STAGE_SIGNAL.get(stage, FABRICATION_STAGE_SIGNAL["in_fabrication"])

        promised_ordinal = _to_ordinal(order["promised_date"])
        obs_mean = promised_ordinal + signal["shift_days"]
        obs_var = signal["obs_std"] ** 2

        state["mean"], state["var"] = self._bayes_update(
            state["mean"], state["var"], obs_mean, obs_var
        )
        state["trace"].append(
            f"Fabrication signal '{stage}' observed -> implied date "
            f"{_from_ordinal(obs_mean)} (obs std={signal['obs_std']:.1f}d). "
            f"Posterior updated to {_from_ordinal(state['mean'])} "
            f"(std={math.sqrt(state['var']):.1f}d)."
        )

    def update_with_tracker_record(self, order_id: str, tracker_record: dict):
        if not tracker_record or not tracker_record.get("eta_estimate"):
            return
        state = self._posterior.get(order_id)
        if state is None:
            return
        try:
            obs_mean = _to_ordinal(tracker_record["eta_estimate"])
        except ValueError:
            return
        obs_var = tracker_eta_obs_std(tracker_record.get("confidence", 0.5)) ** 2

        state["mean"], state["var"] = self._bayes_update(
            state["mean"], state["var"], obs_mean, obs_var
        )
        state["trace"].append(
            f"Material Tracker reconciled ETA {tracker_record['eta_estimate']} "
            f"(tracker confidence={tracker_record.get('confidence', 0.5):.2f}) "
            f"-> posterior updated to {_from_ordinal(state['mean'])} "
            f"(std={math.sqrt(state['var']):.1f}d)."
        )

    def update_with_disruption(self, order_id: str, disruption_type: str):
        state = self._posterior.get(order_id)
        if state is None or disruption_type not in DISRUPTION_SHIFT_DAYS:
            return
        shift = DISRUPTION_SHIFT_DAYS[disruption_type]
        obs_mean = state["mean"] + shift
        obs_var = (shift) ** 2 / 2  # moderately confident this disruption applies

        state["mean"], state["var"] = self._bayes_update(
            state["mean"], state["var"], obs_mean, obs_var
        )
        state["trace"].append(
            f"External disruption flag '{disruption_type}' (+{shift:.0f}d risk) "
            f"-> posterior updated to {_from_ordinal(state['mean'])} "
            f"(std={math.sqrt(state['var']):.1f}d)."
        )

    def forecast(self, order: dict, tracker_record: dict = None,
                 disruption_flags: list = None) -> dict:
        """Runs the full sequential Bayesian update for one order and
        returns forecast date, 90% confidence interval, and delay
        probability against the originally promised date."""
        self._get_or_init_prior(order)
        self.update_with_fabrication_signal(order)
        if tracker_record:
            self.update_with_tracker_record(order["order_id"], tracker_record)
        for flag in (disruption_flags or []):
            self.update_with_disruption(order["order_id"], flag)

        state = self._posterior[order["order_id"]]
        mean, std = state["mean"], math.sqrt(state["var"])
        promised_ordinal = _to_ordinal(order["promised_date"])

        # P(true delivery date > promised date) under the posterior Normal.
        delay_probability = 1 - norm.cdf(promised_ordinal, loc=mean, scale=std)

        ci_low = mean - 1.645 * std   # 90% CI (one-sided 5%/95%)
        ci_high = mean + 1.645 * std
        days_at_risk = max(0.0, mean - promised_ordinal)

        return {
            "order_id": order["order_id"],
            "forecast_date": _from_ordinal(mean),
            "confidence_interval_90": [_from_ordinal(ci_low), _from_ordinal(ci_high)],
            "delay_probability": round(float(delay_probability), 3),
            "days_at_risk": round(days_at_risk, 1),
            "posterior_std_days": round(std, 2),
            "promised_date": order["promised_date"],
            "reasoning_trace": list(state["trace"]),
        }
