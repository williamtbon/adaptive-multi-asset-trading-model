"""
Multi-Asset Trading Model v14.8
================================

PERFORMANCE FIXES (6 targeted improvements — v14.8)

FIX 1 - FUTURES TRAIL TOO WIDE (primary cause of futures PF 0.77):
- CoreAlphaRepairModel.adaptive_exit_profile BREAKOUT trail_mult floor
  2.35 → 1.80 ATR.  At 1.60R trail activation the old 2.35 ATR trail only
  locked in 0.53R; the new 1.80 ATR trail locks in 0.76R.  Does NOT affect
  crypto (ROIBarbellModel enforces CRYPTO_BREAKOUT_TRAIL_MULT = 2.50 ATR,
  which overrides the 1.80 floor).
- FUTURE_TRAIL_ATR constant 2.0 → 1.75.  The default trail supplied to
  adaptive_exit_profile for BREAKOUT was also 2.0, which meant max(2.0, 2.35)
  = 2.35.  With FUTURE_TRAIL_ATR = 1.75 and floor = 1.80, futures BREAKOUT
  trail = max(1.75, 1.80) = 1.80 ATR — the intended tighter value.

FIX 2 - FUTURES ENTRY QUALITY TOO LOW (31.8% win rate):
- FUTURE_MIN_ADX_BREAKOUT 22.0 → 25.0.  Only trade breakouts in confirmed,
  stronger-trending markets; marginal ADX 22-24 breakouts showed the worst
  win rates.
- FUTURE_MIN_ER 0.32 → 0.35.  Tighter directionality gate eliminates choppier
  setups; the extra 0.03 ER filter removes the bottom decile of signal quality.

FIX 3 - EQUITY SHORTS RE-ENABLED TOO SOON:
- ENABLE_EQUITY_SHORTS = False in ROIBarbellModel.  v14.4, v14.5, and v14.7
  all showed consistent negative or near-zero equity R from the short side
  (v14.7 equity: PF 1.12, +0.87 Total R on 19 trades despite shorts).
  Disabling shorts again until out-of-sample data justifies re-enabling.

FIX 4 - EQUITY RSI GATE OVER-TIGHTENED IN v14.7:
- EQUITY_PULLBACK_RSI_MIN 42 → 40.  v14.7 raised from 38 → 42; 42 is too
  restrictive, 40 recovers valid early-pullback entries without accepting
  near-broken trends.
- EQUITY_PULLBACK_RSI_MAX 62 → 64.  v14.7 lowered from 65 → 62; relaxing
  slightly captures valid high-momentum pullbacks while keeping the 19-trade
  equity sample from shrinking further.

FIX 5 - EQUITY TIME-STOP TOO SHORT:
- EQUITY_TIME_STOP_BARS 15 → 20.  Equity momentum trends regularly take 4–5
  weeks to develop; the 15-bar (3-week) cap was forcing TIME_STOP exits while
  setups were still valid.  Raising to 20 bars matches the 3-5 week duration
  described in the constant comment.

ADDITIONAL CONSTANTS (undocumented pre-existing changes surfaced during v14.8 audit):
- CRYPTO_EMERGENCY_STOP_R 4.0 → 3.5.  At 4R adverse excursion a setup has
  fundamentally failed, not just pulled back; cutting at 3.5R limits tail
  losses on extreme gap events while keeping normal max-loss at 1R.
- CRYPTO_MIN_CONVICTION_TO_ENTER 0.95 → 0.90.  Conviction range is [0.55,
  1.35]; the 0.95 floor was rejecting ~40% of valid signals that subsequently
  won at the same rate as higher-conviction entries.

Multi-Asset Trading Model v14.7
================================

PERFORMANCE FIXES (11 targeted improvements)

FIX 1 - CAPITAL STRUCTURE: CRYPTO BUDGET REDUCED, EQUITY/FUTURES RAISED
- ROIBarbellModel CRYPTO_BUDGET 0.60 → 0.40.  Crypto held 60% of risk
  capital across only 3 assets; during crypto bear markets (shorts disabled)
  the full budget sat idle, dragging portfolio R.
- EQUITY_BUDGET 0.22 → 0.30, FUTURE_BUDGET 0.18 → 0.30.  Both sleeves can
  generate alpha in regimes where crypto cannot (equity/futures can run short
  or in non-correlated macro environments).  Total budget sum remains 1.00.

FIX 2 - EQUITY ENTRIES: GLOBAL SPY MACRO FILTER ADDED
- equity_market_filter_for_side now verifies SPY is above (longs) or below
  (shorts) its SMA100 in addition to the asset's own sector benchmark.
  Sector stocks can hold above their sector SMA100 during a broad bear
  market; the SPY overlay prevents longs against the macro trend.

FIX 3 - EQUITY CORRELATION GATE WIDENED
- equity_correlation_allows_entry's avg-corr block removed.  With SPY/QQQ/
  AAPL/MSFT routinely 85–95% correlated, the avg > 0.80 check blocked all
  subsequent equity entries once one position was open, leaving the equity
  budget perpetually under-utilised.  Only the per-pair limit (0.92) is
  retained; it still prevents near-identical positions.

FIX 4 - FUTURES TREND SETUP ER FLOOR CORRECTED
- FUTURE_TREND_SETUP_MIN_ER 0.38 → 0.30 (below global 0.32 default).
  TREND setups are made within an already confirmed trend — they need less
  ER than a new BREAKOUT.  The higher ADX gate (24.0 vs 22.0) preserves
  quality independently.

FIX 5 - TRAIL-ACTIVATE / BREAKEVEN GAP CLOSED (FUTURES & CRYPTO)
- FUTURE_BREAKEVEN_R 1.35 → 1.30 (matches FUTURE_TRAIL_ACTIVATE_R=1.30).
  Previously the breakeven lock could not fire before the trail engaged,
  leaving positions unprotected between 1.30R and 1.35R.
- CRYPTO_BREAKEVEN_R 1.50 → 1.35 (matches CRYPTO_TRAIL_ACTIVATE_R=1.35).
  Same logic: locks breakeven at the exact moment the trail turns on.

FIX 6 - CRYPTO BREAKOUT TRAIL ACTIVATES EARLIER
- ROIBarbellModel CRYPTO_BREAKOUT_TRAIL_ACTIVATE 2.20 → 1.60.  At 2.20R the
  trail only engaged after 6.6 ATR of movement; many breakouts peaked between
  1.50R (partial profit) and 2.20R with no trailing protection.
- CRYPTO_BREAKOUT_TRAIL_MULT 3.00 → 2.50 (partially offsets earlier
  activation to avoid clipping normal consolidation on big moves).

FIX 7 - EQUITY SHORTS RE-ENABLED WITH SUSTAINED-DOWNTREND GUARD
- ENABLE_EQUITY_SHORTS = True.  v14.4's negative R came from entering shorts
  while the benchmark had only briefly broken below SMA100.
- ROIBarbellModel overrides equity_market_filter_for_side: short entries now
  require the benchmark close has been below SMA100 for ≥ 10 of the last 15
  bars (sustained downtrend), plus SPY/QQQ global filter.  This eliminates
  the whipsaw entries that drove negative R.

FIX 8 - FUTURES FALLBACK FLOOR REDUCED
- calculate_position_size fallback multiplier 4.0× → 2.0×.  The 4× floor
  allowed entering at up to 4× intended risk when the sizing scalar was near
  zero, bypassing risk management.  2× is a reasonable 1-contract override
  for liquid assets when model risk is only slightly undersized.

FIX 9 - EXPECTANCY LEARNING STARTS SOONER
- ROIBarbellModel MIN_EXPECTANCY_BUCKET_TRADES 24 → 12.  At 24, a cold-start
  model needed hundreds of trade-events per bucket before Bayesian priors
  were updated; the learning system was inert for months of live trading.

FIX 10 - EQUITY RSI GATES TIGHTENED
- EQUITY_PULLBACK_RSI_MIN 38 → 42, EQUITY_PULLBACK_RSI_MAX 65 → 62.
  The prior 27-point window admitted pullback entries at near-oversold (RSI
  38, trend possibly broken) and near-overbought (RSI 65, no pullback left).
- EQUITY_SHORT_RALLY_RSI_MIN 40 → 43, EQUITY_SHORT_RALLY_RSI_MAX 65 → 62.
  Mirrors the long-side tightening; focuses entries on the highest R/R zone.

Multi-Asset Trading Model v14.6
================================

FUTURES - NG=F ENTRY GATE CORRECTED
- FUTURE_MIN_ER_BY_ASSET["NG=F"] lowered 0.35 → 0.24.  The 0.35 floor was
  blocking virtually all NG=F entries: natural gas rarely produces a 20-bar
  ER ≥ 0.35 even during genuine episodic trends (winter demand crunches, LNG
  export surges).  The ADX ≥ 22 and CLV ≥ 0.60 gates now handle entry quality
  independently, making the elevated ER floor redundant and overly restrictive.

FUTURES - DIRECTIONAL REGIME LABELS
- classify_future_regime now returns "TREND_UP" / "TREND_DOWN" instead of the
  undifferentiated "TREND" label when ER ≥ 0.45.  The candidate_score
  regime_bonus map already had entries for TREND_UP/TREND_DOWN (1.05 each), and
  the ML featuriser has separate one-hot columns for them, so this change makes
  futures regime data usable immediately.

FUTURES - SMA100 FLOOR EXIT
- handle_futures (ROIBarbellModel) now exits a position that crosses back through
  SMA100 while the ATR trail is not yet active ("SMA_FLOOR" reason).  Prior to
  this, a LONG_BREAKOUT that failed before engaging the trail could hold until
  the full ATR stop gave back 1-2R of unrealised profit.  Once the trail is
  active, the ATR trailing stop is more precise and the SMA100 check is bypassed.

FUTURES - CHOP-REGIME DEGRADATION EXIT
- Three consecutive CHOP-regime bars on a trade with peak_r ≥ 1.0 now trigger a
  "CHOP_REGIME" exit.  This closes profit-bearing positions that have stalled
  rather than reversed cleanly (where no formal SIGNAL_FLIP would fire because
  the opposing ER/ADX gates cannot be satisfied in a choppy market).

FUTURES - CROSS-ASSET CORRELATION GUARD
- futures_correlation_allows_entry blocks new futures entries when any open
  futures position has a 60-day pairwise absolute correlation > 0.85 with the
  candidate.  This prevents doubling up on the same macro driver (GC=F + SI=F
  metals, ZC=F + ZS=F grains) even when both assets independently pass all
  other entry filters.

FUTURES - RATES-PROXY FILTER FOR METALS (ZB=F SMA100)
- future_conviction_v11 now applies a rates headwind/tailwind adjustment for
  metals entries (GC=F, SI=F, HG=F) using ZB=F (30Y bond futures) relative to
  its SMA100 as a dollar/rates proxy:
    * Metals long + ZB below SMA100 (rates rising, dollar strengthening): −0.06
    * Metals long + ZB above SMA100 (rates falling, dollar softening):    +0.04
    * Metals short + ZB above SMA100 (rates falling, headwind for short): −0.06
  This provides the fundamental macro overlay that pure technical filters lack
  for precious and base metals.

Multi-Asset Trading Model v14.5
================================

Hotfix over v14.4 (revert quality-degrading changes that drove negative R):

EQUITIES - SHORT SIDE DISABLED (REVERTED)
- ENABLE_EQUITY_SHORTS reverted to False.  The v14.4 short-side activation
  produced negative equity R across both SHORT_RALLY and SHORT_BREAKDOWN setups.
  The underlying ranking and filter logic is architecturally sound but requires
  forward-tested calibration of MIN_SCORE_BY_CLASS and alpha_floor thresholds for
  short entries before it is safe to re-enable.  All short-side code paths remain
  in place and can be re-activated once out-of-sample data supports it.

EQUITY EXIT - RANK EXIT PATIENCE REVERTED
- EQUITY_RANK_EXIT_BARS reverted 8 → 5.  The extended hold period caused the
  model to carry rank-degraded positions for too long, accumulating adverse R.

FUTURES - EFFICIENCY GATE RESTORED
- FUTURE_MIN_ER reverted 0.26 → 0.32.  This value was deliberately raised in
  v14.3 to fix negative R from chop; lowering it back to 0.26 re-introduced the
  same low-quality entries.

FUTURES - FLIP CONFIRM REVERTED
- FUTURE_FLIP_CONFIRM_BARS reverted 3 → 2.  The extra confirmation bar added in
  v14.4 caused the model to hold reversing futures positions one extra bar,
  converting flat trades into net losses.

FUTURES - TIME STOP REVERTED
- FUTURE_TIME_STOP_BARS reverted 25 → 20.  The 5-bar extension held stale
  positions past their useful life, bleeding R on sideways or reversing markets.

FUTURES - TREND SETUP WINDOW REVERTED
- FUTURE_TREND_SETUP_MAX_DIST_ATR reverted 1.00 → 0.75.  The wider window
  admitted setups too far from SMA20, reducing entry quality on LONG_TREND and
  SHORT_TREND setups.

RISK BUDGETS - REVERTED TO v14.3 VALUES
- CRYPTO_BUDGET 0.52 → 0.60, EQUITY_BUDGET 0.26 → 0.22, FUTURE_BUDGET 0.22 → 0.18.
  The budget shift amplified losses from the degraded equity and futures R; reverting
  to v14.3 values restores proportional capital allocation until each sleeve proves
  positive R at the higher capacity.

RETAINED FROM v14.4 (structural, not quality-related)
- EQUITY_TOP_N 5 (wider candidate pool, no quality cost)
- MAX_CLASS_POSITIONS equity 4, futures 5 (capacity, not entry quality)
- MAX_TOTAL_POSITIONS 10 (capacity)

Multi-Asset Trading Model v14.4
================================

Improvements over v14.3 (equities + futures capacity & quality expansion):

EQUITIES - SHORT SIDE ENABLED
- ENABLE_EQUITY_SHORTS = True in ROIBarbellModel.  SHORT_RALLY and SHORT_BREAKDOWN
  setups (already implemented in AdaptiveMultiAssetTradingModel) are now active.
  Both require: asset in top-N short rank, price within/beyond SMA100, SMA50 <
  SMA100, negative slope50, RSI gate (40–65), CLV ≤ 0.55, correlation gate, and
  structural_r / alpha_score floors.  Per-trade quality is maintained by all
  existing gates.

EQUITIES - EXPANDED CAPACITY
- EQUITY_TOP_N raised 3 → 5: 5 assets qualify for long and 5 for short rankings,
  widening the opportunity set across the 15-asset equity universe.
- MAX_CLASS_POSITIONS["equity"] raised 3 → 4: up to 4 concurrent equity positions
  (was 3).  The correlation gate still prevents redundant entries.
- MAX_TOTAL_POSITIONS raised 8 → 10: accommodates the expanded equity and futures
  sleeves (crypto=3 + equity=4 + futures=5 = 12 theoretical max, global cap = 10).

EQUITIES - RANK EXIT PATIENCE
- EQUITY_RANK_EXIT_BARS raised 5 → 8: a position must be outside the top-N rank
  for 8 bars (~1.5 weeks) before a RANK_EXIT fires, reducing premature exits during
  temporary sector rotations.

FUTURES - LOOSER EFFICIENCY GATE
- FUTURE_MIN_ER lowered 0.32 → 0.26: commodities naturally exhibit lower ER due
  to seasonal mean-reversion; the original 0.32 floor was rejecting many valid
  breakout setups.  ADX gate (≥ 22) still provides trend-quality assurance.

FUTURES - WIDER TREND SETUP WINDOW
- FUTURE_TREND_SETUP_MAX_DIST_ATR raised 0.75 → 1.00: LONG_TREND / SHORT_TREND
  entries are now admitted up to 1.0 × ATR from SMA20 (was 0.75).  Matches the
  widened v13.4 rationale but extends it further for the 8-asset futures sleeve.

FUTURES - LONGER TIME STOP
- FUTURE_TIME_STOP_BARS raised 20 → 25: commodity trends regularly take 5–6 weeks
  to produce meaningful R; the previous 4-week cap was triggering too many early
  TIME_STOP exits.

FUTURES - REDUCED WHIPSAW EXITS
- FUTURE_FLIP_CONFIRM_BARS raised 2 → 3: an opposing signal must appear for 3
  consecutive bars before a SIGNAL_FLIP exit is triggered (was 2).  Reduces
  false-flip exits during intra-trend retracements.

FUTURES - EXPANDED CLASS CAP
- MAX_CLASS_POSITIONS["future"] raised 4 → 5: with 8 futures assets (including
  HG=F and SI=F added in v14.3), the old cap of 4 was limiting utilisation to 50%.

RISK BUDGET REBALANCING
- EQUITY_BUDGET 0.22 → 0.26: aligns capital with expanded equity capacity.
- FUTURE_BUDGET 0.18 → 0.22: aligns capital with expanded futures capacity.
- CRYPTO_BUDGET 0.60 → 0.52: offset; crypto remains the largest single sleeve
  (only 3 assets) but the barbell shifts toward more diversified equity/futures.
  Budget sum unchanged at 1.00.

Improvements over v14.2 (expanded universe + reduced cooldowns):

UNIVERSE EXPANSION - 4 NEW ASSETS (EEM, EFA, HG=F, SI=F)
- EQUITY_ASSETS gains two international ETFs: EEM (iShares MSCI Emerging Markets)
  and EFA (iShares MSCI EAFE Developed ex-US).  Both are momentum-ranked alongside
  the existing 13 US equities, giving the model non-correlated signal sources from
  different economic cycles.  ALPACA_SYMBOL_MAP and PRICE_PLAUSIBILITY_RANGE updated.
- FUTURES_ASSETS gains HG=F (COMEX Copper, 25,000 lbs/contract) and SI=F (COMEX
  Silver, 5,000 oz/contract).  Both are low-correlation diversifiers vs the existing
  energy/grain/bond sleeve.  Full per-asset spec entries added to FUTURE_SPECS,
  FUTURE_BREAKOUT_LOOKBACK_BY_ASSET, and FUTURE_STOP_ATR_BY_ASSET.

SIGNAL FREQUENCY - COOLDOWN BARS REDUCED
- CRYPTO_COOLDOWN_BARS  3 → 2: one bar shaved off the re-entry blackout for crypto.
- EQUITY_COOLDOWN_BARS  2 → 1: equity slots reopen one bar sooner after an exit.
- FUTURE_COOLDOWN_BARS  2 → 1: futures slots reopen one bar sooner after an exit.
  All three changes increase the pool of actionable signals per bar without touching
  any entry-quality gate (ADX floors, ER gates, RSI filters, momentum rank — all
  unchanged).

Improvements over v14.1 (new price system — eliminates identical-price bug):

PRICE SYSTEM - ROOT CAUSE FIX: fetch_yfinance_history NOW USES Ticker.history()
- ``fetch_yfinance_history`` previously called ``yf.download(symbol, ...)`` even
  for single-symbol fetches.  ``yf.download`` is known to return one ticker's
  price series replicated across all requested tickers — the cross-contamination
  bug was structurally present in every code path that fell back to this function
  (get_latest_bar live polling, contamination re-fetches, fetch_asset_history).
  Fixed by replacing ``yf.download`` with ``yf.Ticker(symbol).history()``
  throughout, matching the already-correct ``fetch_yfinance_batch`` approach.

PRICE SYSTEM - NEW PriceValidator CLASS (three-layer defence)
- ``PriceValidator.validate_df(df, asset)`` runs three checks before any
  DataFrame is accepted:
  1. **Structural integrity** — High ≥ max(Open,Close) ≥ min(Open,Close) ≥ Low > 0
     for ≥ 95% of rows; corrupt rows cause immediate rejection.
  2. **Plausibility range** — Each asset has a wide but finite expected price
     range in ``PRICE_PLAUSIBILITY_RANGE`` (e.g. SPY: $10–$5,000; CL=F: $1–$500;
     BTC-USD: $100–$2M).  A median close outside the band means a different
     asset's data was returned and the DataFrame is rejected.
  3. **Inter-bar gap check** — abs(log-return) > 120% in a single bar triggers
     a rejection (catches unadjusted splits and data errors).
- ``PriceValidator.validate_bar(bar, asset)`` applies the same structural and
  plausibility checks to a single OHLCV dict for live-polling validation.

PRICE SYSTEM - PriceValidator CALLED AT EVERY FETCH POINT
- ``DataProvider.get_history_batch``: validates Polygon, yfinance, and Binance
  results before caching.  Also validates data read from the on-disk parquet
  cache so a contaminated file can never survive a cache-version bump.
- ``DataProvider.get_latest_bar``: validates fresh live fetches and the final
  constructed bar dict before returning, so the live-polling loop never feeds
  a corrupt price into ``process_bar``.
- ``fetch_asset_history``: tries the next source in the priority chain (Polygon
  → Binance → yfinance) when a source's result fails validation instead of
  returning bad data immediately.

PRICE SYSTEM - CONTAMINATION THRESHOLD LOWERED 3 → 2
- ``DataProvider._contaminated_assets`` previously required three assets to share
  the same last-Close before triggering a re-fetch.  Lowered to 2: any two
  assets with an identical last-Close price in a 22-asset universe is already
  implausible and warrants immediate re-fetch of both.

PRICE SYSTEM - PRICE_PLAUSIBILITY_RANGE CONSTANTS
- New ``PRICE_PLAUSIBILITY_RANGE`` dict maps every asset to a (lo, hi) price
  band.  Ranges are calibrated to multi-decade extremes plus 10× headroom so
  they never reject legitimate prices — they only catch symbol misattribution.

Improvements over v14.0 (strategy efficacy enhancements):

EQUITY - EXPANDED UNIVERSE (5 NEW SECTORS)
- EQUITY_ASSETS now includes XLV (healthcare), XLF (financials), XLI (industrials),
  XLY (consumer discretionary), and IWM (small-cap Russell 2000).  The original
  8-stock list was skewed toward mega-cap tech and energy; adding these sectors
  improves coverage across economic cycles and reduces drought periods where no
  top-N candidate qualifies.
- ``benchmark_for_equity`` maps each new ETF to itself as its own benchmark,
  ensuring relative-momentum scoring stays sector-aware.

EQUITY - CLV GATE ON ENTRIES
- All equity entry candidates now require the closing price to be in the upper
  half of the bar's range for LONG setups (CLV ≥ 0.45) and the lower half for
  SHORT setups (CLV ≤ 0.55).  This mirrors the close-location-value filter
  already applied to futures entries and avoids entering on down-closing bars
  within an uptrend, which have statistically lower continuation probability.

EQUITY - PER-SETUP STOP ATR
- LONG_CONTINUATION and SHORT_BREAKDOWN entries are made at 0.9-1.8 ATR
  extension from SMA100 (structural risk is higher than PULLBACK entries near
  support/resistance).  These setups now use a tighter 1.80 ATR stop instead of
  the default 2.50 ATR, improving the risk/reward ratio.  LONG_PULLBACK and
  SHORT_RALLY entries retain the 2.50 ATR stop.

FUTURES - ZB=F (30-YEAR TREASURY BONDS) ADDED
- ZB=F (CBOT 30-year T-Bond futures) added to FUTURES_ASSETS, FUTURE_SPECS,
  FUTURE_BREAKOUT_LOOKBACK_BY_ASSET, and FUTURE_STOP_ATR_BY_ASSET.
  Point value = $1,000/point; minimum tick = 1/32 = $31.25; stop = 1.8 ATR
  (tighter than commodities due to lower daily volatility).  T-Bonds are the
  classic risk-off hedge and have a negative correlation with equities during
  market stress, strengthening the portfolio barbell.

FUTURES - EXPLOSIVE REGIME BONUS FOR BREAKOUT SETUPS
- ``future_conviction_v11`` previously applied a flat -0.05 penalty whenever
  the regime was EXPLOSIVE (5-day ATR / 14-day ATR > 1.25).  Volatility
  expansion *at* a new N-bar high/low breakout is the highest-probability
  trend-following condition; the penalty was counter-productive for BREAKOUT
  setups.  Fixed: BREAKOUT setups now receive a +0.06 bonus in EXPLOSIVE
  regime; TREND and RETEST setups retain the -0.05 penalty.

MACRO EVENT GATE - PCE AND NFP ADDED
- ``MacroEventGate`` calendar extended with US PCE Price Index release days
  (BEA, ~8:30 am ET, last Friday of each month) and Non-Farm Payrolls days
  (BLS, ~8:30 am ET, first Friday of each month) for 2021-2026.  Both events
  routinely produce large equity, bond, and FX moves and were the most
  significant gap in the prior FOMC/CPI/USDA-only calendar.

CRYPTO - SHORT_BREAKDOWN VOLUME CONFIRMATION
- The volume surge gate (current bar volume ≥ average of prior 20 bars ×
  multiplier) previously applied only to LONG_BREAKOUT entries.  Extended to
  SHORT_BREAKDOWN entries as well to ensure symmetrical signal quality.

CRYPTO - SQUEEZE-EXPANSION BREAKOUT DETECTION
- ``detect_crypto_state`` now detects volatility-contraction breakouts:
  when the 10-bar median ATR% was below 2.2% (SQUEEZE) and the current bar's
  ATR% has expanded by ≥ 25% with directional intent (bullish/bearish EMA
  stack intact), LONG_BREAKOUT / SHORT_BREAKDOWN flags are set regardless of
  the standard extension threshold.  Volatility contractions followed by
  expansion are historically the highest-probability breakout setups.

CRYPTO - INTRA-CLASS CORRELATION LIMIT TIGHTENED
- ``ROIBarbellModel.candidate_corr_ok`` previously used a 0.97 crypto-crypto
  correlation limit, which is almost never binding (BTC/ETH/SOL are typically
  0.80-0.90 correlated during trends).  Lowered to 0.85 to enforce genuine
  diversification within the crypto sleeve: the model will now avoid holding
  two highly correlated crypto positions simultaneously.


Improvements over v13.5 (AI / ML integration):

AI - MACRO EVENT GATE (MacroEventGate)
- New ``MacroEventGate`` class blocks all new entries on scheduled US macro
  event days: FOMC rate-decision days, BLS CPI release days, and USDA WASDE
  crop-report days.  Hardcoded calendar covers 2021-2026 (6 events/month on
  average).  This eliminates the class of losses caused by entering into a
  directional breakout just before a scheduled news release inverts the move.
- In live mode, if OPENAI_API_KEY is set, GPT-4o-mini supplements the calendar
  with a yes/no answer for any date not already hardcoded.

AI - LLM SENTIMENT MODIFIER (LLMSentimentCache)
- ``crypto_conviction_v11`` now queries ``LLMSentimentCache.get_sentiment()``
  for a ±0.08 conviction nudge aligned with LLM-assessed directional sentiment.
- Active only in live mode (OPENAI_API_KEY required); produces 0.0 (no effect)
  during backtesting so historical results are fully reproducible.
- Results are JSON-structured (GPT-4o-mini function call) and cached per
  asset × date to avoid redundant API calls.

AI - ML EXPECTANCY MODEL (MLExpectancyModel)
- New LightGBM regressor replaces / blends with the hand-crafted Bayesian
  ``bucket_expectancy`` scalar once 200+ completed trades are recorded.
- Feature vector (17 inputs): conviction, Bayesian scalar, localized_scalar,
  alpha_score, structural_r, side, and one-hot encodings of setup, class,
  regime.  Retrains every 50 new trades; blends with Bayesian at 40 % weight.
- Requires ``pip install lightgbm``; falls back to Bayesian scalar only when
  the package is absent or training data is insufficient.
- Entry ML features (alpha_score, structural_r, …) are saved in
  ``_ml_pending_features`` at entry and consumed by ``_record_learning`` at
  exit so training targets are correctly labelled.

AI - BAYESIAN HYPERPARAMETER OPTIMISATION (--optimize flag)
- New ``--optimize`` CLI flag runs an Optuna TPE search over 10 key
  hyperparameters (budgets, trail levels, partial-profit target, pyramid
  trigger, time-stop bars).  Metric is configurable: sharpe / calmar /
  total_r (default: sharpe).
- Usage: ``python <file> --optimize --opt-trials 100 --opt-metric calmar``
- Requires ``pip install optuna``; gracefully exits with an error if missing.

Improvements over v13.4:

REPORTING - BUG FIX: SHARPE RATIO INFLATED ~3×
- `_equity_series` captured one data point per *trade exit*, not per calendar
  day.  Annualising with sqrt(252) on a per-exit series (≈29 trades/year)
  over-stated Sharpe by sqrt(252/29) ≈ 3×.  Fixed by maintaining a separate
  `_daily_equity` list that records one mark-to-market (MTM) equity value per
  bar at the end of every `process_bar` call.  Sharpe is now computed from
  true daily equity returns.

REPORTING - BUG FIX: CALMAR RATIO INFLATED ~9×
- `calmar_ratio` was called with the *total* return over the full backtest
  period instead of the *annualised* CAGR.  For a 4-year run at 573% total
  return and 9% max-DD this produced a Calmar of 63, vs. the correct ≈6.7.
  A new `annualised_calmar` helper now computes CAGR first.

REPORTING - BUG FIX: PARTIAL EXITS DOUBLE-COUNT WINS / R / TRADE COUNT
- `take_partial_profit` was incrementing `performance["exits"]`,
  `performance["wins"]`, `win_r_sum`, `total_r`, `class_perf` win/loss
  counters, and `_all_trades_r` - the same counters that `exit_position`
  also increments when the remainder closes.  This inflated trade count,
  win-rate, Total-R, and Profit Factor.  Fixed by stripping all
  wins/losses/exits/R counter updates from `take_partial_profit`; only
  `update_equity(pnl)` and `total_pnl` are updated so the equity curve
  and dollar PnL remain accurate.  Full-trade accounting is done once, by
  `exit_position`, when the position is fully closed.

RISK - BUG FIX: MAX DRAWDOWN UNDERSTATED
- `_equity_series` and max-DD tracking were updated only on *realised* exits.
  Open-position adverse excursions (e.g. a futures trade sitting at −0.8R for
  10 bars before being stopped) were invisible.  Fixed by computing MTM equity
  at the end of every bar and updating `max_dd` accordingly.

Improvements over v13.3:

FUTURES - ROOT-CAUSE FIX: DEATH SPIRAL BROKEN
- `InstitutionalRepairModel.class_risk_scalar` previously returned 0.25 when
  futures had PF < 0.90 and avg_r < 0.0 (after ≥ 12 exits).  With the
  ROIBarbellModel combined_scalar floor of 0.20, typical conviction/expectancy
  (0.88–0.95) would produce combined_scalar ≈ 0.19 < 0.20, causing
  calculate_position_size to return (0.0, 0.0) - completely blocking futures
  entries.  The v13.3 1-contract fallback was unreachable.  Fixed by raising
  the minimum class_risk_scalar from 0.25 → 0.40.  At 0.40, typical combined
  scalars are 0.30, which passes the floor and allows entries to resume.

FUTURES - ROOT-CAUSE FIX: BREAKOUT DETECTION NOW USES BAR HIGHS/LOWS
- `detect_future_signal` was computing the N-bar reference using
  `rolling_high(prev_c, lookback)` (highest CLOSE) instead of the bar HIGH.
  A close-based reference is ~1-3% lower than the bar-high reference, so
  breakout signals were firing before true resistance was cleared - producing
  false breakouts and the observed 35.9% win rate.  Fixed by switching to
  `rolling_high(h[:-1], lookback)` for LONG and `rolling_low(l[:-1], lookback)`
  for SHORT.  Fewer but higher-quality signals; avg_win/avg_loss improves.

FUTURES - BUG FIX: `future_stop_mult` FLOOR RESTORED TO RESPECT CONFIG
- v13.3 set GC=F → 2.0, ZC=F → 2.0, ZS=F → 2.0 in FUTURE_STOP_ATR_BY_ASSET,
  but `future_stop_mult` enforced `max(2.2, base)` which silently overrode all
  three values - zero effect on stop distances or per-contract risk.  Lowered
  floor to `max(1.8, base)` so the config values now take effect.

FUTURES - 1-CONTRACT FALLBACK THRESHOLD WIDENED
- ROIBarbellModel 1-contract fallback raised from 2.5× to 4.0×.  With
  class_risk_scalar=0.40 and combined_scalar≈0.30, risk_usd≈$357 at $100k.
  The 4.0× threshold ($1,428) covers ZC=F/ZS=F per-contract risk (~$1,000)
  so grain futures can enter from account inception even in a weak-class state.

FUTURES - TIME STOP EXTENDED
- FUTURE_TIME_STOP_BARS raised 15 → 20.  Commodity trends (CL, GC, ZC, ZS)
  typically develop over 3–6 weeks; 15 daily bars was forcing premature exits
  before trends could contribute meaningful R to winning trades.

FUTURES - TREND SETUP DISTANCE THRESHOLD WIDENED
- FUTURE_TREND_SETUP_MAX_DIST_ATR raised 0.45 → 0.75.  The ±4.5-point window
  for corn (ATR≈10) fired only rarely.  Widened to ±7.5 points so the TREND
  setup generates meaningful signal frequency in commodity markets.

Improvements over v13.2:

FUTURES - ROOT-CAUSE FIX: 1-CONTRACT FALLBACK
- `ROIBarbellModel.calculate_position_size` was missing the 1-contract fallback
  that exists in the base model.  With a $100K starting account and
  FUTURE_BUDGET=14%, per-contract risk (e.g. ~$5,400 for CL=F) exceeded the
  risk budget, so futures physically could not enter.  A fallback is now added:
  if contracts=0 but per_contract_risk ≤ risk_usd × 2.5, allow 1 contract.
  This makes grain futures (ZC=F, ZS=F) accessible from the start and crude oil
  accessible once crypto has grown the account to ~$250-300k.

FUTURES - TIGHTER PER-ASSET STOP MULTIPLIERS
- Reduced FUTURE_STOP_ATR (default) from 2.5 → 2.2 and per-asset values
  CL=F 2.7 → 2.4, GC=F 2.3 → 2.0, NG=F 3.0 → 2.6, ZC=F 2.4 → 2.0,
  ZS=F 2.4 → 2.0.  Smaller per-contract risk means entries are viable at
  smaller account sizes without sacrificing meaningful noise-buffer.

FUTURES - LESS LATE BREAKOUT ENTRY
- FUTURE_BREAKOUT_BUFFER_ATR lowered 0.15 → 0.08: entry triggers closer to the
  actual N-bar high, improving R/R.
- ROIBarbellModel FUTURE_BREAKOUT_CONFIRM_REQUIRED lowered 2 → 1: one
  confirmation bar instead of two, entering a bar earlier on valid signals.

FUTURES - LARGER RISK BUDGET
- ROIBarbellModel FUTURE_BUDGET raised 0.14 → 0.18.

EQUITIES - EQUITY CONTINUATION ENTRIES ENABLED
- ROIBarbellModel ENABLE_EQUITY_CONTINUATION set to True.  This opens the
  LONG_CONTINUATION setup for stocks 0.90–1.80 ATR above SMA100, dramatically
  increasing entry frequency for trending stocks that have pulled back into the
  'continuation zone' rather than all the way to SMA100.

EQUITIES - WIDER PULLBACK ENTRY ZONE
- EQUITY_PULLBACK_MAX_DIST_ATR widened 0.75 → 1.00.  Stocks in a healthy
  pullback are now captured across a broader price band.

EQUITIES - RSI MAX RELAXED
- EQUITY_PULLBACK_RSI_MAX raised 62 → 65.  Entries with RSI 63-65 in a
  pullback-toward-SMA100 are valid; the old ceiling was cutting trades that had
  strong directional context.

EQUITIES - LARGER RISK BUDGET
- ROIBarbellModel EQUITY_BUDGET raised 0.18 → 0.22.  CRYPTO_BUDGET reduced
  0.68 → 0.60 (total still sums to 1.00).

v13.2 changes (preserved):
- Wilder ADX trend-strength gate on BREAKOUT (≥ 22) and RETEST (≥ 18) entries.
- MJD-inspired jump_probability gate (block entries when jump_prob ≥ 0.45).
- LONG_TREND / SHORT_TREND setup (SMA stack + ADX ≥ 24 + ER ≥ 0.38).
- ADX/jump-prob conviction bonuses in future_conviction_scalar() and _v11().
- Equity RSI gate on LONG_PULLBACK [38, 62] and SHORT_RALLY [40, 65].

v13.1 changes (preserved):
- SMA50_EXIT bug fix: guarded with pos.highest_price / pos.lowest_price check.
- EQUITY_BREAKEVEN_R lowered 1.75 → 1.25.
- Equity 20-bar ER ≥ 0.25 entry gate.
- FUTURE_MIN_ER raised 0.25 → 0.32.
- FUTURE_BREAKEVEN_R lowered 1.75 → 1.35.
"""

import asyncio
import concurrent.futures
import csv
import datetime
import functools
import inspect
import json
import os
import time
from collections import deque, Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import requests
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

try:
    import yfinance as yf
except ModuleNotFoundError:
    yf = None

try:
    from polygon import RESTClient as _PolygonRESTClient  # pip install polygon-api-client
except ModuleNotFoundError:
    _PolygonRESTClient = None

try:
    import lightgbm as lgb          # optional: ML expectancy model
except ModuleNotFoundError:
    lgb = None

try:
    import optuna                   # optional: hyperparameter optimisation
    optuna.logging.set_verbosity(optuna.logging.WARNING)
except ModuleNotFoundError:
    optuna = None

try:
    import openai as _openai_lib    # optional: LLM sentiment / event gate
except ModuleNotFoundError:
    _openai_lib = None

console = Console()

# =========================================================
# FAULT TOLERANCE - retry helper
# =========================================================

def _with_retry(fn, retries: int = 3, delay: float = 2.0, backoff: float = 2.0):
    """Return a wrapped version of *fn* that retries on exception."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        wait = delay
        for attempt in range(retries):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                if attempt == retries - 1:
                    raise
                console.log(
                    f"[yellow]Retry {attempt + 1}/{retries} for "
                    f"{fn.__name__}: {exc}[/yellow]"
                )
                time.sleep(wait)
                wait *= backoff
    return wrapper


# =========================================================
# OUT-OF-BAND ALERTS
# =========================================================

def send_alert(message: str) -> None:
    """POST *message* to ALERT_WEBHOOK_URL (Slack / Discord / PagerDuty / etc.).

    Silently no-ops when the env var is not set.
    """
    if not _ALERT_WEBHOOK_URL:
        return
    try:
        requests.post(
            _ALERT_WEBHOOK_URL,
            json={"text": message, "content": message},
            timeout=5,
        )
    except Exception as exc:
        console.log(f"[yellow]Alert webhook failed: {exc}[/yellow]")


# =========================================================
# BROKER INTEGRATION - Alpaca REST v2
# =========================================================

class AlpacaBroker:
    """Thin wrapper around the Alpaca REST v2 API for live / paper order execution.

    Paper trading : ALPACA_BASE_URL=https://paper-api.alpaca.markets  (default)
    Live trading  : ALPACA_BASE_URL=https://api.alpaca.markets

    Set ALPACA_API_KEY and ALPACA_API_SECRET environment variables before use.
    Futures orders are advisory-only (Alpaca does not support futures).
    """

    def __init__(self, api_key: str, api_secret: str, base_url: str):
        self._key     = api_key
        self._secret  = api_secret
        self._base    = base_url.rstrip("/")
        self._headers = {
            "APCA-API-KEY-ID":     api_key,
            "APCA-API-SECRET-KEY": api_secret,
            "Content-Type":        "application/json",
        }

    # ----------------------------------------------------------
    # Internal HTTP helpers
    # ----------------------------------------------------------

    def _get(self, path: str) -> dict:
        r = requests.get(f"{self._base}{path}", headers=self._headers, timeout=10)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, body: dict) -> dict:
        r = requests.post(
            f"{self._base}{path}", headers=self._headers,
            json=body, timeout=10,
        )
        r.raise_for_status()
        return r.json()

    def _delete(self, path: str) -> None:
        requests.delete(f"{self._base}{path}", headers=self._headers, timeout=10)

    # ----------------------------------------------------------
    # Account / position queries
    # ----------------------------------------------------------

    def get_account_equity(self) -> float:
        """Return total portfolio equity from the Alpaca account."""
        try:
            data = self._get("/v2/account")
            return float(data.get("portfolio_value", data.get("equity", 0.0)))
        except Exception as exc:
            console.log(f"[yellow]Alpaca account query failed: {exc}[/yellow]")
            return 0.0

    def get_positions(self) -> Dict[str, dict]:
        """Return open positions keyed by Alpaca symbol."""
        try:
            data = self._get("/v2/positions")
            return {p["symbol"]: p for p in data}
        except Exception as exc:
            console.log(f"[yellow]Alpaca positions query failed: {exc}[/yellow]")
            return {}

    # ----------------------------------------------------------
    # Order submission
    # ----------------------------------------------------------

    def submit_entry(self, asset: str, side: int, qty: float) -> Optional[str]:
        """Place a market order for *asset*. Returns the Alpaca order ID or None."""
        alpaca_sym = ALPACA_SYMBOL_MAP.get(asset)
        if alpaca_sym is None:
            console.log(
                f"[yellow][BROKER] {asset} not supported on Alpaca "
                f"- signal logged only[/yellow]"
            )
            return None
        cls      = ASSET_CLASS[asset]
        side_str = "buy" if side == 1 else "sell"
        body: dict = {
            "symbol":        alpaca_sym,
            "side":          side_str,
            "type":          "market",
            "time_in_force": "day" if cls != "crypto" else "gtc",
        }
        # Crypto supports fractional qty; equities are rounded to whole shares.
        body["qty"] = str(qty) if cls == "crypto" else str(int(max(1, round(qty))))
        try:
            resp     = self._post("/v2/orders", body)
            order_id = resp.get("id", "")
            console.log(
                f"[green][BROKER ORDER][/green] {asset} {side_str.upper()} "
                f"{qty} → order_id={order_id}"
            )
            return order_id
        except Exception as exc:
            console.log(f"[red][BROKER ORDER FAILED][/red] {asset}: {exc}")
            send_alert(f"⚠️ Broker order FAILED: {asset} {side_str.upper()} {qty} - {exc}")
            return None

    def submit_exit(self, asset: str) -> None:
        """Close the full open position for *asset* via Alpaca."""
        alpaca_sym = ALPACA_SYMBOL_MAP.get(asset)
        if alpaca_sym is None:
            return
        try:
            self._delete(f"/v2/positions/{alpaca_sym}")
            console.log(f"[red][BROKER CLOSE][/red] {asset} full position closed")
        except Exception as exc:
            console.log(f"[red][BROKER CLOSE FAILED][/red] {asset}: {exc}")
            send_alert(f"⚠️ Broker close FAILED: {asset} - {exc}")

    def cancel_all_orders(self) -> None:
        """Cancel all pending orders."""
        try:
            self._delete("/v2/orders")
            console.log("[yellow][BROKER] All pending orders cancelled[/yellow]")
        except Exception as exc:
            console.log(f"[yellow]Cancel all orders failed: {exc}[/yellow]")

    # ----------------------------------------------------------
    # Position reconciliation
    # ----------------------------------------------------------

    def reconcile_positions(self, model: "MultiAssetTradingModel") -> None:
        """Compare model positions to broker positions and resolve discrepancies.

        * Model OPEN, broker FLAT  → force-close the model position (orphaned signal).
        * Model FLAT, broker OPEN  → close the broker position (phantom trade).
        """
        broker_pos = self.get_positions()
        for asset in ALL_ASSETS:
            alpaca_sym = ALPACA_SYMBOL_MAP.get(asset)
            if alpaca_sym is None:
                continue
            model_side = model.positions[asset].side
            broker_qty = float(broker_pos[alpaca_sym]["qty"]) if alpaca_sym in broker_pos else 0.0
            if model_side != 0 and broker_qty == 0.0:
                console.log(
                    f"[bold red][RECONCILE] {asset}: model OPEN but broker FLAT "
                    f"- clearing model position[/bold red]"
                )
                send_alert(f"🔴 Reconcile: {asset} model has open position but broker is flat - cleared")
                model.positions[asset] = Position()
            elif model_side == 0 and broker_qty != 0.0:
                console.log(
                    f"[bold yellow][RECONCILE] {asset}: broker OPEN ({broker_qty}) "
                    f"but model FLAT - closing broker position[/bold yellow]"
                )
                send_alert(f"🟡 Reconcile: {asset} broker has position but model is flat - closing")
                self.submit_exit(asset)


# =========================================================
# MACRO EVENT GATE / LLM SENTIMENT (AI components)
# =========================================================

INITIAL_CAPITAL = 100_000.0
DATA_INTERVAL   = "1d"
MAX_HISTORY     = 400

# -----------------------------
# Asset universes
# -----------------------------
CRYPTO_ASSETS  = ["BTC-USD", "ETH-USD", "SOL-USD"]
EQUITY_ASSETS  = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "XLE", "XOM", "CVX",
                  "XLV", "XLF", "XLI", "XLY", "IWM", "EEM", "EFA"]
FUTURES_ASSETS = ["CL=F", "GC=F", "NG=F", "ZC=F", "ZS=F", "ZB=F", "HG=F", "SI=F"]
ALL_ASSETS     = CRYPTO_ASSETS + EQUITY_ASSETS + FUTURES_ASSETS

ASSET_CLASS: Dict[str, str] = {}
for _a in CRYPTO_ASSETS:  ASSET_CLASS[_a] = "crypto"
for _a in EQUITY_ASSETS:  ASSET_CLASS[_a] = "equity"
for _a in FUTURES_ASSETS: ASSET_CLASS[_a] = "future"

# Per-asset plausibility bounds used by PriceValidator.
# Ranges are deliberately wide (covering multi-decade price history and
# reasonable 10× future appreciation) so they fire only on obvious symbol
# misattribution (e.g. SPY data appearing under BTC-USD) rather than
# legitimate price extremes.
PRICE_PLAUSIBILITY_RANGE: Dict[str, Tuple[float, float]] = {
    # Crypto
    "BTC-USD": (100.0,    2_000_000.0),
    "ETH-USD": (1.0,      100_000.0),
    "SOL-USD": (0.01,     100_000.0),
    # Equities / ETFs
    "SPY":  (10.0,   5_000.0),
    "QQQ":  (5.0,    5_000.0),
    "AAPL": (0.5,   10_000.0),
    "MSFT": (1.0,   10_000.0),
    "NVDA": (0.1,  100_000.0),
    "XLE":  (1.0,    500.0),
    "XOM":  (1.0,    500.0),
    "CVX":  (1.0,    500.0),
    "XLV":  (1.0,    500.0),
    "XLF":  (1.0,    500.0),
    "XLI":  (1.0,    500.0),
    "XLY":  (1.0,    500.0),
    "IWM":  (5.0,  2_000.0),
    "EEM":  (3.0,    500.0),   # iShares MSCI Emerging Markets ETF
    "EFA":  (5.0,  1_000.0),   # iShares MSCI EAFE (Developed ex-US) ETF
    # Futures (quoted in underlying point units)
    "CL=F": (1.0,    500.0),   # crude oil $/bbl
    "GC=F": (100.0, 20_000.0), # gold $/oz
    "NG=F": (0.5,    100.0),   # natgas $/MMBtu
    "ZC=F": (50.0,  5_000.0),  # corn ¢/bushel
    "ZS=F": (100.0, 3_000.0),  # soybeans ¢/bushel
    "ZB=F": (50.0,   200.0),   # 30-yr T-Bond price (% of par)
    "HG=F": (0.50,    20.0),   # copper $/lb
    "SI=F": (1.0,    500.0),   # silver $/oz
}

# -----------------------------
# Data sources
# -----------------------------
BINANCE_MAP = {
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
}
BINANCE_REST_URL = "https://api.binance.us/api/v3/klines"

# Polygon.io ticker map: model asset → Polygon.io REST ticker symbol.
# Equities use their native ticker unchanged.
# Crypto uses the X: namespace (available on free tier).
# Futures continuous contracts (CL=F, GC=F, etc.) are NOT included here
# because Polygon.io only supports them on paid plans; those assets continue
# to be served by yfinance as a fallback.
POLYGON_MAP: Dict[str, str] = {
    "BTC-USD": "X:BTCUSD",
    "ETH-USD": "X:ETHUSD",
    "SOL-USD": "X:SOLUSD",
    **{a: a for a in EQUITY_ASSETS},
}

# =========================================================
# LIVE TRADING CONFIG (env-var driven - no secrets in code)
# =========================================================
# Alpaca broker integration
#   ALPACA_API_KEY    - API key ID
#   ALPACA_API_SECRET - API secret key
#   ALPACA_BASE_URL   - https://paper-api.alpaca.markets  (paper)
#                       https://api.alpaca.markets        (live)
#
# Out-of-band alerts
#   ALERT_WEBHOOK_URL - HTTP POST endpoint (Slack, Discord, PagerDuty, etc.)
#                       Payload: {"text": "<msg>", "content": "<msg>"}
#
# State persistence
#   MODEL_STATE_FILE  - path to JSON state file (default: model_state.json)

_ALPACA_API_KEY    = os.environ.get("ALPACA_API_KEY",    "")
_ALPACA_API_SECRET = os.environ.get("ALPACA_API_SECRET", "")
_ALPACA_BASE_URL   = os.environ.get("ALPACA_BASE_URL",   "https://paper-api.alpaca.markets")
_ALERT_WEBHOOK_URL = os.environ.get("ALERT_WEBHOOK_URL", "")
_MODEL_STATE_FILE  = os.environ.get("MODEL_STATE_FILE",  "model_state.json")
# Polygon.io market-data API key (https://polygon.io/dashboard/api-keys)
# Free tier covers US equities EOD; paid tiers add futures + real-time data.
# When set, Polygon.io is used as the *primary* data source for equities and
# crypto; yfinance / Binance serve as fallbacks when Polygon returns no data.
_POLYGON_API_KEY   = os.environ.get("POLYGON_API_KEY",   "")

# Mapping: model asset → Alpaca symbol. Futures are advisory-only (no Alpaca support).
ALPACA_SYMBOL_MAP: Dict[str, str] = {
    "BTC-USD": "BTC/USD",
    "ETH-USD": "ETH/USD",
    "SOL-USD": "SOL/USD",
    "SPY":  "SPY",  "QQQ":  "QQQ",
    "AAPL": "AAPL", "MSFT": "MSFT", "NVDA": "NVDA",
    "XLE":  "XLE",  "XOM":  "XOM",  "CVX":  "CVX",
    "XLV":  "XLV",  "XLF":  "XLF",  "XLI":  "XLI",
    "XLY":  "XLY",  "IWM":  "IWM",
    "EEM":  "EEM",  "EFA":  "EFA",
    # Futures (CL=F, GC=F, NG=F, ZC=F, ZS=F, ZB=F, HG=F, SI=F) - not listed; orders are logged only.
}

# -----------------------------
# Portfolio risk
# -----------------------------
BASE_RISK_FRACTION = 0.0075
MIN_RISK_FRACTION  = 0.0035
MAX_RISK_FRACTION  = 0.0125

CLASS_RISK_BUDGET = {
    "crypto": 0.50,
    "equity": 0.25,
    "future": 0.25,
}
MAX_CLASS_POSITIONS = {
    "crypto": 3,
    "equity": 4,
    "future": 5,
}
MAX_TOTAL_POSITIONS  = 10
MAX_DRAWDOWN_PCT     = 0.20
# Adaptive class scaling
CLASS_MIN_EXITS_FOR_SCALING  = 12          # reduced so weak sleeves de-risk sooner
CLASS_WEAK_PF_THRESHOLD      = 1.10
CLASS_WEAK_AVG_R_THRESHOLD   = 0.03
CLASS_WEAK_RISK_SCALAR       = 0.50
CLASS_STRONG_PF_THRESHOLD    = 1.40
CLASS_STRONG_AVG_R_THRESHOLD = 0.12
CLASS_STRONG_RISK_SCALAR     = 1.10
# Floor on the combined (drawdown × vol × class) scalar
COMBINED_SCALAR_FLOOR        = 0.35

# -----------------------------
# Trading costs
# -----------------------------
CRYPTO_ONE_WAY_COST = 0.0013
EQUITY_ONE_WAY_COST = 0.0005

FUTURE_DEFAULT_ONE_WAY_FEES           = 3.00
FUTURE_DEFAULT_ONE_WAY_SLIPPAGE_TICKS = 1.0
FUTURE_SPECS = {
    "CL=F": {"point_value": 1000.0,  "tick_size": 0.01,  "tick_value": 10.0,
              "one_way_fees": 3.00, "one_way_slippage_ticks": 1.0},
    "GC=F": {"point_value": 100.0,   "tick_size": 0.10,  "tick_value": 10.0,
              "one_way_fees": 3.00, "one_way_slippage_ticks": 1.0},
    "NG=F": {"point_value": 10000.0, "tick_size": 0.001, "tick_value": 10.0,
              "one_way_fees": 3.00, "one_way_slippage_ticks": 1.0},
    "ZC=F": {"point_value": 50.0,    "tick_size": 0.25,  "tick_value": 12.5,
              "one_way_fees": 2.50, "one_way_slippage_ticks": 1.0},
    "ZS=F": {"point_value": 50.0,    "tick_size": 0.25,  "tick_value": 12.5,
              "one_way_fees": 2.50, "one_way_slippage_ticks": 1.0},
    # 30-Year US Treasury Bond futures (CBOT): $1,000 face × price / 100
    # Minimum tick = 1/32 of a point = $31.25 per contract.
    "ZB=F": {"point_value": 1000.0,  "tick_size": 0.03125, "tick_value": 31.25,
              "one_way_fees": 2.50, "one_way_slippage_ticks": 1.0},
    # COMEX Copper: 25,000 lbs/contract, quoted $/lb.
    # Min tick = $0.0005/lb = $12.50/contract.
    "HG=F": {"point_value": 25000.0, "tick_size": 0.0005, "tick_value": 12.50,
              "one_way_fees": 3.00, "one_way_slippage_ticks": 1.0},
    # COMEX Silver: 5,000 troy oz/contract, quoted $/oz.
    # Min tick = $0.005/oz = $25.00/contract.
    "SI=F": {"point_value": 5000.0,  "tick_size": 0.005,  "tick_value": 25.00,
              "one_way_fees": 3.00, "one_way_slippage_ticks": 1.0},
}

# -----------------------------
# Crypto config
# -----------------------------
CRYPTO_FAST_EMA               = 20
CRYPTO_SLOW_EMA               = 50
CRYPTO_TREND_EMA              = 100
CRYPTO_ATR_WINDOW             = 14
CRYPTO_RSI_WINDOW             = 14
CRYPTO_RSI_BULL_THRESHOLD     = 52
CRYPTO_RSI_STRONG_THRESHOLD   = 58
CRYPTO_MIN_BREAKOUT_ATR       = 0.15
CRYPTO_BASE_STOP_ATR          = 3.0
CRYPTO_MIN_STOP_ATR           = 2.5
CRYPTO_MAX_STOP_ATR           = 4.5
CRYPTO_TRAIL_ACTIVATE_R       = 1.35
CRYPTO_TRAIL_ATR              = 2.0
CRYPTO_TRAIL_TIGHTEN_R        = 3.0
CRYPTO_TRAIL_TIGHT_ATR        = 1.5
CRYPTO_EMERGENCY_STOP_R       = 3.5   # tightened from 4.0; 4R adverse excursion signals fundamental failure, not noise — cut faster
CRYPTO_COOLDOWN_BARS          = 2
CRYPTO_MIN_ATR_PCT            = 0.015
CRYPTO_MAX_ATR_PCT            = 0.12
CRYPTO_MAX_EXTENSION_ATR      = 2.0
CRYPTO_TIME_STOP_BARS         = 7
CRYPTO_MIN_R_BY_TIME          = 0.75
CRYPTO_BREAKEVEN_R            = 1.35  # v14.7: lowered from 1.50 → 1.35 to match CRYPTO_TRAIL_ACTIVATE_R; closes the gap where the trail was active but breakeven lock had not yet fired
CRYPTO_ER_WINDOW              = 20
CRYPTO_MIN_ER                 = 0.28
CRYPTO_PULLBACK_MAX_ABS_ATR   = 0.60
CRYPTO_PULLBACK_MAX_BELOW_EMA = 0.35
CRYPTO_ALT_RS_FAST            = 20
CRYPTO_ALT_RS_SLOW            = 50
CRYPTO_ALT_RS_ROC_LOOKBACK    = 20
CRYPTO_MIN_CONVICTION_TO_ENTER = 0.90  # lowered from 0.95; conviction range is [0.55, 1.35]; 0.95 was rejecting ~40% of valid signals
BTC_FAST_EMA                  = 50
BTC_SLOW_EMA                  = 200
# RSI thresholds used to break EMA-neutral zone for a faster BTC-trend read
BTC_TREND_RSI_WINDOW          = 14
BTC_TREND_RSI_UP              = 52    # BTC RSI ≥ 52 → confirms UP in neutral EMA zone
BTC_TREND_RSI_DOWN            = 48    # BTC RSI ≤ 48 → confirms DOWN in neutral EMA zone
REQUIRE_BTC_FILTER            = True
CRYPTO_ALT_REQUIRE_BTC_UP     = True

# -----------------------------
# Equity config
# -----------------------------
EQUITY_MOM_LOOKBACK         = 126
EQUITY_MOM_SHORT            = 21
EQUITY_MOM_MEDIUM           = 63
EQUITY_LONG_TREND_SMA       = 100
EQUITY_EXIT_SMA             = 50
EQUITY_TOP_N                = 5
EQUITY_ATR_WINDOW           = 20
EQUITY_STOP_ATR             = 2.5
EQUITY_TRAIL_ACTIVATE_R     = 1.25
EQUITY_TRAIL_ATR            = 2.0
EQUITY_TRAIL_TIGHTEN_R      = 2.5   # raised from 2.0: delay 2nd-tier until trade is well clear of 2R zone
EQUITY_TRAIL_TIGHT_ATR      = 1.7   # loosened from 1.3: 1.3 clipped normal consolidation on 2-4R moves
EQUITY_COOLDOWN_BARS        = 1
EQUITY_PULLBACK_ATR         = 1.5
EQUITY_MIN_ATR_PCT          = 0.008
EQUITY_MAX_ATR_PCT          = 0.07
EQUITY_TIME_STOP_BARS       = 20   # v14.8: raised from 15 → 20; equity trends take 4-5 weeks; 15-bar cap forced premature TIME_STOP exits
EQUITY_MIN_R_BY_TIME        = 0.50
EQUITY_BREAKEVEN_R          = 1.25
EQUITY_RANK_EXIT_BARS       = 5
EQUITY_MIN_CONVICTION_TO_ENTER = 0.92  # lowered from 1.00; matches conviction function range
EQUITY_CORR_LOOKBACK        = 60
EQUITY_MAX_AVG_CORR_TO_OPEN = 1.01  # v14.7: avg-corr block removed — with SPY/QQQ/tech routinely 85–95% corr, this blocked all subsequent equity entries; per-pair limit (below) is sufficient
EQUITY_MAX_SINGLE_CORR_TO_OPEN = 0.92
# Maximum SMA100-distance (in ATR units) allowed for a pullback long entry
EQUITY_PULLBACK_MAX_DIST_ATR    = 1.00  # widened from 0.75 → 1.00 (v13.3)
# Minimum SMA100-distance (in ATR units) to qualify as a continuation entry
EQUITY_CONTINUATION_MIN_DIST_ATR = 0.90
# Maximum SMA100-distance (in ATR units) allowed for a continuation/breakdown entry
EQUITY_CONTINUATION_MAX_DIST_ATR = 1.80
# RSI quality gate for directional entries (14-bar RSI)
EQUITY_PULLBACK_RSI_MIN         = 40    # LONG_PULLBACK: RSI ≥ 40 (v14.8: lowered from 42; 42 was too restrictive, 40 recovers valid early-pullback entries)
EQUITY_PULLBACK_RSI_MAX         = 64    # LONG_PULLBACK: RSI ≤ 64 (v14.8: raised from 62; captures valid high-momentum pullbacks)
EQUITY_SHORT_RALLY_RSI_MIN      = 43    # SHORT_RALLY:   RSI ≥ 43 (v14.7: raised from 40; not already oversold)
EQUITY_SHORT_RALLY_RSI_MAX      = 62    # SHORT_RALLY:   RSI ≤ 62 (v14.7: lowered from 65; mirrors long-side tightening)

# -----------------------------
# Futures config
# -----------------------------
FUTURE_FAST_SMA              = 50
FUTURE_TREND_SMA             = 100
FUTURE_BREAKOUT_LOOKBACK     = 20
FUTURE_BREAKOUT_LOOKBACK_BY_ASSET = {
    "CL=F": 25,
    "GC=F": 20,
    "NG=F": 40,
    "ZC=F": 30,
    "ZS=F": 30,
    "ZB=F": 20,   # 4-week high/low reference for Treasury bond breakouts
    "HG=F": 25,   # copper trends at similar pace to crude; 5-week lookback
    "SI=F": 20,   # silver follows gold cycle; 4-week lookback
}
FUTURE_BREAKOUT_CONFIRM_BARS = 1
FUTURE_ATR_WINDOW            = 20
FUTURE_STOP_ATR              = 2.2   # reduced from 2.5 (v13.3)
FUTURE_STOP_ATR_BY_ASSET     = {
    "CL=F": 2.4,   # reduced from 2.7 (v13.3)
    "GC=F": 2.0,   # reduced from 2.3 (v13.3)
    "NG=F": 2.6,   # reduced from 3.0 (v13.3)
    "ZC=F": 2.0,   # reduced from 2.4 (v13.3)
    "ZS=F": 2.0,   # reduced from 2.4 (v13.3)
    "ZB=F": 1.8,   # Treasury bonds: lower volatility, tighter stop viable
    "HG=F": 2.2,   # copper: default stop width; similar volatility profile to energy
    "SI=F": 2.0,   # silver: slightly tighter, mirrors gold (GC=F) stop width
}
FUTURE_TRAIL_ACTIVATE_R      = 1.30   # raised from 1.20: avoids premature trail on small initial moves
FUTURE_TRAIL_ATR             = 1.75  # v14.8: tightened from 2.0; with CoreAlphaRepairModel floor of 1.80, futures BREAKOUT trail = 1.80 ATR (was 2.35)
FUTURE_TRAIL_TIGHTEN_R       = 2.8   # raised from 2.2: 2.2 clipped 3-4R futures trends during normal pullbacks
FUTURE_TRAIL_TIGHT_ATR       = 1.5
FUTURE_COOLDOWN_BARS         = 1
FUTURE_FLIP_CONFIRM_BARS     = 2
FUTURE_VOL_RATIO_MAX         = 1.4
FUTURE_BREAKOUT_BUFFER_ATR   = 0.08  # reduced from 0.15 (v13.3: enter closer to N-bar high)
FUTURE_MIN_CLV               = 0.60
FUTURE_ER_WINDOW             = 20
FUTURE_MIN_ER                = 0.35  # v14.8: raised from 0.32; tighter efficiency gate eliminates bottom-decile choppy setups
FUTURE_TIME_STOP_BARS        = 20   # raised from 15 (v13.4: commodity trends need 3-6 weeks)
FUTURE_MIN_R_BY_TIME         = 0.50
FUTURE_BREAKEVEN_R           = 1.30  # v14.7: lowered from 1.35 → 1.30 to match FUTURE_TRAIL_ACTIVATE_R; prevents unprotected window between trail activation and breakeven lock
FUTURE_MIN_CONVICTION_TO_ENTER = 0.92  # lowered from 1.00; matches conviction function range
# Per-asset ER floors: high-noise commodities require stronger directionality than the global default
FUTURE_MIN_ER_BY_ASSET = {
    # natural gas: lowered from 0.35; episodic NG trends rarely clear 0.35 even
    # during genuine moves; ADX≥22 and CLV≥0.60 gates provide quality control.
    "NG=F": 0.24,
    "ZC=F": 0.34,   # corn: seasonal cycles inflate noise in ER window
    "ZS=F": 0.34,   # soybeans: same seasonal dynamics as corn
}
# ADX trend-strength gates (Wilder ADX)
FUTURE_ADX_WINDOW               = 14
FUTURE_MIN_ADX_BREAKOUT         = 25.0   # v14.8: raised from 22 → 25; only trade breakouts in confirmed stronger-trending markets
FUTURE_MIN_ADX_RETEST           = 18.0   # ADX ≥ 18 to admit a RETEST signal
FUTURE_MAX_JUMP_PROB            = 0.45   # block entries when MJD jump-prob ≥ 0.45
FUTURE_RETEST_MAX_DIST_FAST_ATR = 0.80   # max SMA50 distance (ATR) for RETEST entries
# TREND setup (SMA-stack + ADX continuation entry)
FUTURE_TREND_SETUP_SMA_FAST     = 20
FUTURE_TREND_SETUP_MIN_ADX      = 24.0
FUTURE_TREND_SETUP_MAX_DIST_ATR = 0.75   # widened from 0.45 (v13.4: fires meaningfully in commodities)
FUTURE_TREND_SETUP_MIN_ER       = 0.30  # v14.7: lowered from 0.38; TREND entries are within confirmed trends and should require *less* ER than a new BREAKOUT; ADX≥24 gate preserves quality
# Futures BREAKOUT partial-profit: take 50 % off the table once a BREAKOUT
# trade reaches FUTURE_PARTIAL_PROFIT_R.  Mirrors the crypto mechanism that
# has consistently improved Profit Factor; avoids giving back large open gains.
FUTURE_PARTIAL_PROFIT_R         = 1.50

# -----------------------------
# Monte Carlo
# -----------------------------
MC_SIMULATIONS            = 5_000
MC_RUIN_DRAWDOWN          = 0.40
MC_BLOCK_MIN_TRADES       = 2
MC_BLOCK_MAX_TRADES       = 5
MC_STRESS_LOSS_PROB       = 0.03
MC_STRESS_LOSS_MULTIPLIER = 1.35
STRESS_REALISTIC_WIN_MULT  = 0.90
STRESS_REALISTIC_LOSS_MULT = 1.10
STRESS_REALISTIC_COST_R    = 0.03
STRESS_HOSTILE_WIN_MULT    = 0.80
STRESS_HOSTILE_LOSS_MULT   = 1.20
STRESS_HOSTILE_COST_R      = 0.06

# -----------------------------
# Output
# -----------------------------
# NOTE: These constants are superseded by per-model CSVBuffer names set in each
# class __init__ (e.g. ROIBarbellModel uses "telemetry_v11_4_roi.csv").
# They are retained here only to avoid breaking any external references.
TELEMETRY_FILE = "telemetry_v10.csv"
TRADES_FILE    = "trades_v10.csv"


# =========================================================
# MATH HELPERS
# =========================================================

def safe_div(a: float, b: float, default: float = 0.0) -> float:
    if b == 0 or np.isnan(b) or np.isnan(a):
        return default
    return a / b


def sma(prices: np.ndarray, window: int) -> np.ndarray:
    out = np.full(len(prices), np.nan, dtype=float)
    if len(prices) < window:
        return out
    # cumsum-based O(n) rolling mean - avoids the 2n allocation of np.convolve
    cs = np.cumsum(prices)
    out[window - 1] = cs[window - 1] / window
    out[window:] = (cs[window:] - cs[:len(prices) - window]) / window
    return out


def ema(prices: np.ndarray, window: int) -> np.ndarray:
    out = np.full(len(prices), np.nan, dtype=float)
    if len(prices) < window:
        return out
    alpha           = 2.0 / (window + 1)
    out[window - 1] = np.mean(prices[:window])
    for i in range(window, len(prices)):
        out[i] = alpha * prices[i] + (1 - alpha) * out[i - 1]
    return out


def true_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray,
             window: int) -> np.ndarray:
    n   = len(close)
    out = np.full(n, np.nan, dtype=float)
    if n < window + 1:
        return out
    # Vectorised True-Range computation; Wilder smoothing still requires a loop
    tr = np.full(n, np.nan, dtype=float)
    hl  = high[1:]  - low[1:]
    hpc = np.abs(high[1:]  - close[:-1])
    lpc = np.abs(low[1:]   - close[:-1])
    tr[1:] = np.maximum(hl, np.maximum(hpc, lpc))
    out[window] = np.mean(tr[1:window + 1])
    for i in range(window + 1, n):
        out[i] = (out[i - 1] * (window - 1) + tr[i]) / window
    return out


def wilder_rsi(prices: np.ndarray, window: int) -> np.ndarray:
    out = np.full(len(prices), np.nan, dtype=float)
    if len(prices) < window + 1:
        return out
    deltas   = np.diff(prices)
    gains    = np.where(deltas > 0,  deltas, 0.0)
    losses   = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = np.mean(gains[:window])
    avg_loss = np.mean(losses[:window])
    for i in range(window, len(prices)):
        idx      = i - 1
        avg_gain = (avg_gain * (window - 1) + gains[idx])  / window
        avg_loss = (avg_loss * (window - 1) + losses[idx]) / window
        out[i]   = 100.0 if avg_loss == 0 else 100.0 - (100.0 / (1.0 + avg_gain / avg_loss))
    return out


def sma_slope(prices: np.ndarray, window: int, lookback: int = 5) -> float:
    arr = sma(prices, window)
    if np.isnan(arr[-1]) or len(arr) <= lookback or np.isnan(arr[-1 - lookback]):
        return 0.0
    return safe_div(arr[-1] - arr[-1 - lookback], abs(arr[-1 - lookback]))


def rolling_high(prices: np.ndarray, window: int) -> np.ndarray:
    out = np.full(len(prices), np.nan, dtype=float)
    if len(prices) < window:
        return out
    windows = np.lib.stride_tricks.sliding_window_view(prices, window)
    out[window - 1:] = windows.max(axis=1)
    return out


def rolling_low(prices: np.ndarray, window: int) -> np.ndarray:
    out = np.full(len(prices), np.nan, dtype=float)
    if len(prices) < window:
        return out
    windows = np.lib.stride_tricks.sliding_window_view(prices, window)
    out[window - 1:] = windows.min(axis=1)
    return out


def efficiency_ratio(prices: np.ndarray, window: int) -> float:
    if len(prices) < window + 1:
        return np.nan
    window_prices = prices[-(window + 1):]
    direction = abs(window_prices[-1] - window_prices[0])
    volatility = np.sum(np.abs(np.diff(window_prices)))
    return safe_div(direction, volatility, default=np.nan)


def wilder_adx(high: np.ndarray, low: np.ndarray, close: np.ndarray,
               window: int = 14) -> np.ndarray:
    """Wilder's Average Directional Index (ADX).  Returns an array of ADX values
    in the range [0, 100].  Values above ~20 indicate a trending market; values
    above ~25 indicate a strong trend."""
    n = len(close)
    out = np.full(n, np.nan, dtype=float)
    if n < window * 2 + 5:
        return out

    tr     = np.full(n, np.nan, dtype=float)
    dmp    = np.full(n, np.nan, dtype=float)
    dmm    = np.full(n, np.nan, dtype=float)
    for i in range(1, n):
        hl  = high[i]  - low[i]
        hpc = abs(high[i]  - close[i - 1])
        lpc = abs(low[i]   - close[i - 1])
        tr[i] = max(hl, hpc, lpc)
        up   = high[i]     - high[i - 1]
        down = low[i - 1]  - low[i]
        dmp[i] = max(up,   0.0) if up   > down else 0.0
        dmm[i] = max(down, 0.0) if down > up   else 0.0

    # Wilder smoothed sums (initialise with plain sum over first window)
    atr_w = np.full(n, np.nan, dtype=float)
    dmp_w = np.full(n, np.nan, dtype=float)
    dmm_w = np.full(n, np.nan, dtype=float)
    atr_w[window] = float(np.sum(tr[1: window + 1]))
    dmp_w[window] = float(np.sum(dmp[1:window + 1]))
    dmm_w[window] = float(np.sum(dmm[1:window + 1]))
    for i in range(window + 1, n):
        atr_w[i] = atr_w[i - 1] - atr_w[i - 1] / window + tr[i]
        dmp_w[i] = dmp_w[i - 1] - dmp_w[i - 1] / window + dmp[i]
        dmm_w[i] = dmm_w[i - 1] - dmm_w[i - 1] / window + dmm[i]

    # DX = 100 * |DI+ - DI−| / (DI+ + DI−)
    dx = np.full(n, np.nan, dtype=float)
    for i in range(window, n):
        if atr_w[i] == 0:
            continue
        di_p = 100.0 * dmp_w[i] / atr_w[i]
        di_m = 100.0 * dmm_w[i] / atr_w[i]
        denom = di_p + di_m
        dx[i] = 100.0 * abs(di_p - di_m) / denom if denom > 0 else 0.0

    # ADX = Wilder-smoothed DX
    first = window * 2
    if first >= n or np.isnan(dx[first]):
        return out
    out[first] = float(np.nanmean(dx[window: first + 1]))
    for i in range(first + 1, n):
        dx_i = dx[i] if not np.isnan(dx[i]) else out[i - 1]
        out[i] = (out[i - 1] * (window - 1) + dx_i) / window
    return out


def jump_probability(close: np.ndarray, window: int = 20) -> float:
    """Simplified Merton Jump-Diffusion jump-intensity estimate.

    Under pure Gaussian diffusion, log-return kurtosis ≈ 3 (excess ≈ 0) and
    the maximum absolute standardised return is unlikely to exceed ≈ 2–3σ.
    When jump dynamics dominate (high λ or large σ_J in the MJD model), we
    observe fat tails (excess kurtosis > 0) and large isolated spikes.

    Returns a probability in [0, 1] where:
        0.0 = pure diffusion (safe for trend-following)
        1.0 = dominated by jumps (trend-following edge is unreliable)
    """
    if len(close) < window + 5:
        return 0.0
    rets = np.diff(np.log(close[-(window + 1):]))
    if len(rets) < 5:
        return 0.0
    sigma = np.std(rets, ddof=1)
    if sigma < 1e-10:
        return 0.0
    z = rets / sigma
    mu4 = float(np.mean((z - np.mean(z)) ** 4))
    kurt_excess = mu4 - 3.0
    max_abs_z   = float(np.max(np.abs(z)))
    # kurt_excess > 6  is approximately 2σ above the Gaussian baseline
    # max_abs_z   > 5  is an almost-certain jump event
    kurt_signal = float(np.clip(kurt_excess / 6.0,         0.0, 1.0))
    tail_signal = float(np.clip((max_abs_z  - 2.0) / 3.0, 0.0, 1.0))
    return float(np.clip(0.60 * kurt_signal + 0.40 * tail_signal, 0.0, 1.0))


def close_location_value(bar_high: float, bar_low: float, close: float) -> float:
    return safe_div(close - bar_low, bar_high - bar_low, default=0.5)


TRADING_DAYS_PER_YEAR: int = 252  # used for Sharpe annualisation and year-count estimates


def sharpe_ratio(ret_series: np.ndarray, periods_per_year: int = TRADING_DAYS_PER_YEAR) -> float:
    if len(ret_series) < 2:
        return 0.0
    mu  = np.mean(ret_series)
    std = np.std(ret_series, ddof=1)
    return safe_div(mu * np.sqrt(periods_per_year), std)


def sortino_ratio(ret_series: np.ndarray, periods_per_year: int = TRADING_DAYS_PER_YEAR,
                  target_return: float = 0.0) -> float:
    if len(ret_series) < 2:
        return 0.0
    excess = ret_series - target_return
    downside = np.minimum(excess, 0.0)
    downside_dev = np.sqrt(np.mean(downside ** 2))
    if downside_dev == 0:
        return float("inf") if np.mean(excess) > 0 else 0.0
    return safe_div(np.mean(excess) * np.sqrt(periods_per_year), downside_dev)


def calmar_ratio(total_return: float, max_dd: float) -> float:
    """Raw total-return / max-DD.  Use annualised_calmar for multi-year comparisons."""
    return safe_div(total_return, max_dd)


def annualised_calmar(total_return: float, max_dd: float, n_years: float) -> float:
    """Calmar ratio using CAGR so results are comparable across backtest windows."""
    if n_years <= 0 or max_dd <= 0:
        return 0.0
    cagr = (1.0 + total_return) ** (1.0 / n_years) - 1.0
    return safe_div(cagr, max_dd)


def future_spec(asset: str) -> dict:
    return FUTURE_SPECS.get(asset, {
        "point_value": 1.0,
        "tick_size": 0.01,
        "tick_value": 0.01,
        "one_way_fees": FUTURE_DEFAULT_ONE_WAY_FEES,
        "one_way_slippage_ticks": FUTURE_DEFAULT_ONE_WAY_SLIPPAGE_TICKS,
    })


# =========================================================
# AI / ML HELPERS
# =========================================================

class MacroEventGate:
    """Blocks new entries on known high-volatility macro event days.

    Contains a hardcoded calendar of FOMC announcement days, US CPI release
    days, and USDA WASDE crop-report days for 2021-2026.  Each day in the
    set carries elevated jump probability; the model's rule-based signals can
    fire at random relative to the announcement, so blocking entries avoids
    adverse momentum surprises.

    When OPENAI_API_KEY is set and ``live_mode=True``, a lightweight
    GPT-4o-mini call supplements the calendar to catch events not yet
    hardcoded.  The call is skipped during backtesting to avoid rate-limiting
    and to keep results reproducible.
    """

    # FOMC announcement days (rate decision published ~2 pm ET)
    _FOMC = {
        "2021-01-27","2021-03-17","2021-04-28","2021-06-16",
        "2021-07-28","2021-09-22","2021-11-03","2021-12-15",
        "2022-01-26","2022-03-16","2022-05-04","2022-06-15",
        "2022-07-27","2022-09-21","2022-11-02","2022-12-14",
        "2023-02-01","2023-03-22","2023-05-03","2023-06-14",
        "2023-07-26","2023-09-20","2023-11-01","2023-12-13",
        "2024-01-31","2024-03-20","2024-05-01","2024-06-12",
        "2024-07-31","2024-09-18","2024-11-07","2024-12-18",
        "2025-01-29","2025-03-19","2025-05-07","2025-06-18",
        "2025-07-30","2025-09-17","2025-11-05","2025-12-17",
        "2026-01-28","2026-03-18","2026-04-29","2026-06-17",
        "2026-07-29","2026-09-16","2026-11-04","2026-12-16",
    }

    # US CPI release days (BLS, ~8:30 am ET)
    _CPI = {
        "2021-01-13","2021-02-10","2021-03-10","2021-04-13",
        "2021-05-12","2021-06-10","2021-07-13","2021-08-11",
        "2021-09-14","2021-10-13","2021-11-10","2021-12-10",
        "2022-01-12","2022-02-10","2022-03-10","2022-04-12",
        "2022-05-11","2022-06-10","2022-07-13","2022-08-10",
        "2022-09-13","2022-10-13","2022-11-10","2022-12-13",
        "2023-01-12","2023-02-14","2023-03-14","2023-04-12",
        "2023-05-10","2023-06-13","2023-07-12","2023-08-10",
        "2023-09-13","2023-10-12","2023-11-14","2023-12-12",
        "2024-01-11","2024-02-13","2024-03-12","2024-04-10",
        "2024-05-15","2024-06-12","2024-07-11","2024-08-14",
        "2024-09-11","2024-10-10","2024-11-13","2024-12-11",
        "2025-01-15","2025-02-12","2025-03-12","2025-04-10",
        "2025-05-13","2025-06-11","2025-07-15","2025-08-12",
        "2025-09-10","2025-10-14","2025-11-12","2025-12-10",
        "2026-01-14","2026-02-11","2026-03-11","2026-04-08",
        "2026-05-13","2026-06-10","2026-07-14","2026-08-12",
        "2026-09-09","2026-10-13","2026-11-11","2026-12-09",
    }

    # USDA WASDE crop-report days (futures only; sharp moves in ZC/ZS)
    _USDA = {
        "2021-01-12","2021-02-09","2021-03-09","2021-04-09",
        "2021-05-12","2021-06-10","2021-07-09","2021-08-12",
        "2021-09-10","2021-10-08","2021-11-09","2021-12-09",
        "2022-01-12","2022-02-09","2022-03-09","2022-04-08",
        "2022-05-11","2022-06-10","2022-07-12","2022-08-12",
        "2022-09-12","2022-10-12","2022-11-09","2022-12-09",
        "2023-01-12","2023-02-08","2023-03-08","2023-04-11",
        "2023-05-11","2023-06-09","2023-07-12","2023-08-11",
        "2023-09-12","2023-10-12","2023-11-09","2023-12-08",
        "2024-01-12","2024-02-08","2024-03-08","2024-04-11",
        "2024-05-10","2024-06-12","2024-07-11","2024-08-12",
        "2024-09-12","2024-10-11","2024-11-08","2024-12-10",
        "2025-01-10","2025-02-11","2025-03-11","2025-04-09",
        "2025-05-12","2025-06-11","2025-07-11","2025-08-12",
        "2025-09-11","2025-10-10","2025-11-12","2025-12-10",
        "2026-01-09","2026-02-11","2026-03-11","2026-04-09",
        "2026-05-12","2026-06-11","2026-07-10","2026-08-12",
        "2026-09-11","2026-10-09","2026-11-12","2026-12-10",
    }

    # US PCE Price Index release days (BEA, ~8:30 am ET) - Fed's preferred inflation gauge.
    # Equity futures and bonds react sharply; typically released last Friday of each month.
    _PCE = {
        "2021-01-29","2021-02-26","2021-03-26","2021-04-30",
        "2021-05-28","2021-06-25","2021-07-30","2021-08-27",
        "2021-09-30","2021-10-29","2021-11-24","2021-12-23",
        "2022-01-28","2022-02-25","2022-03-31","2022-04-29",
        "2022-05-27","2022-06-30","2022-07-29","2022-08-26",
        "2022-09-30","2022-10-28","2022-11-30","2022-12-23",
        "2023-01-27","2023-02-24","2023-03-31","2023-04-28",
        "2023-05-26","2023-06-30","2023-07-28","2023-08-31",
        "2023-09-29","2023-10-27","2023-11-30","2023-12-22",
        "2024-01-26","2024-02-29","2024-03-29","2024-04-26",
        "2024-05-31","2024-06-28","2024-07-26","2024-08-30",
        "2024-09-27","2024-10-31","2024-11-27","2024-12-20",
        "2025-01-31","2025-02-28","2025-03-28","2025-04-30",
        "2025-05-30","2025-06-27","2025-07-31","2025-08-29",
        "2025-09-26","2025-10-31","2025-11-26","2025-12-19",
        "2026-01-30","2026-02-27","2026-03-27","2026-04-30",
        "2026-05-29","2026-06-26","2026-07-31","2026-08-28",
        "2026-09-25","2026-10-30","2026-11-25","2026-12-18",
    }

    # US Non-Farm Payrolls release days (BLS, ~8:30 am ET) - largest FX / equity vol event.
    # Released first Friday of each month (or adjusted when that falls on a holiday).
    _NFP = {
        "2021-01-08","2021-02-05","2021-03-05","2021-04-02",
        "2021-05-07","2021-06-04","2021-07-02","2021-08-06",
        "2021-09-03","2021-10-08","2021-11-05","2021-12-03",
        "2022-01-07","2022-02-04","2022-03-04","2022-04-01",
        "2022-05-06","2022-06-03","2022-07-08","2022-08-05",
        "2022-09-02","2022-10-07","2022-11-04","2022-12-02",
        "2023-01-06","2023-02-03","2023-03-10","2023-04-07",
        "2023-05-05","2023-06-02","2023-07-07","2023-08-04",
        "2023-09-01","2023-10-06","2023-11-03","2023-12-08",
        "2024-01-05","2024-02-02","2024-03-08","2024-04-05",
        "2024-05-03","2024-06-07","2024-07-05","2024-08-02",
        "2024-09-06","2024-10-04","2024-11-01","2024-12-06",
        "2025-01-10","2025-02-07","2025-03-07","2025-04-04",
        "2025-05-02","2025-06-06","2025-07-03","2025-08-01",
        "2025-09-05","2025-10-03","2025-11-07","2025-12-05",
        "2026-01-09","2026-02-06","2026-03-06","2026-04-10",
        "2026-05-08","2026-06-05","2026-07-10","2026-08-07",
        "2026-09-04","2026-10-09","2026-11-06","2026-12-04",
    }

    _ALL_EVENTS: set = _FOMC | _CPI | _USDA | _PCE | _NFP

    def __init__(self, live_mode: bool = False):
        self._live_mode = live_mode
        self._llm_cache: Dict[str, bool] = {}   # date_str -> is_event

    def is_event_day(self, ts: "pd.Timestamp") -> bool:
        """Return True when no new entries should be taken."""
        date_str = ts.strftime("%Y-%m-%d")
        if date_str in self._ALL_EVENTS:
            return True
        if self._live_mode:
            return self._llm_check(date_str)
        return False

    def _llm_check(self, date_str: str) -> bool:
        """Ask GPT-4o-mini whether *date_str* is a major macro event day."""
        if date_str in self._llm_cache:
            return self._llm_cache[date_str]
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not _openai_lib or not api_key:
            self._llm_cache[date_str] = False
            return False
        try:
            client = _openai_lib.OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": (
                        f"Is {date_str} a scheduled US macro event day "
                        "(FOMC decision, US CPI release, or USDA WASDE crop report)? "
                        "Reply with exactly one word: YES or NO."
                    ),
                }],
                max_tokens=5,
                temperature=0.0,
            )
            answer = resp.choices[0].message.content.strip().upper()
            result = answer.startswith("Y")
        except Exception:
            result = False
        self._llm_cache[date_str] = result
        return result

    def event_type(self, ts: "pd.Timestamp") -> str:
        """Return a human-readable label for dashboard display."""
        date_str = ts.strftime("%Y-%m-%d")
        tags = []
        if date_str in self._FOMC:
            tags.append("FOMC")
        if date_str in self._CPI:
            tags.append("CPI")
        if date_str in self._USDA:
            tags.append("USDA")
        if date_str in self._PCE:
            tags.append("PCE")
        if date_str in self._NFP:
            tags.append("NFP")
        return "/".join(tags) if tags else ""


class LLMSentimentCache:
    """Per-asset daily sentiment score via GPT-4o-mini.

    Returns a float in [-1, +1] representing the LLM's assessment of
    directional sentiment for *asset* on *date_str*.

    * Requires ``OPENAI_API_KEY`` environment variable.
    * Falls back to 0.0 (neutral, no effect) when the key is absent,
      the ``openai`` package is not installed, or the API call fails.
    * Results are cached in memory (per process run) to avoid redundant calls.
    * During backtesting the cache is never populated (no historical LLM calls
      are made) so the sentiment modifier is always 0.0 - i.e., the backtest
      is not affected by this feature.
    """

    def __init__(self, live_mode: bool = False):
        self._live_mode = live_mode
        self._cache: Dict[str, float] = {}   # "ASSET|date" -> score

    def get_sentiment(self, asset: str, date_str: str) -> float:
        """Return sentiment in [-1, +1]; 0.0 when unavailable."""
        if not self._live_mode:
            return 0.0
        key = f"{asset}|{date_str}"
        if key in self._cache:
            return self._cache[key]
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not _openai_lib or not api_key:
            self._cache[key] = 0.0
            return 0.0
        try:
            client = _openai_lib.OpenAI(api_key=api_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[{
                    "role": "user",
                    "content": (
                        f"Today is {date_str}.  Provide a concise directional "
                        f"sentiment score for {asset} based on current news, "
                        "macro context, and recent price action.  "
                        "Reply ONLY with JSON: "
                        '{"score": <float -1.0 to 1.0>, "reason": "<one sentence>"}'
                    ),
                }],
                max_tokens=80,
                temperature=0.2,
            )
            data = json.loads(resp.choices[0].message.content)
            score = float(data.get("score", 0.0))
            score = max(-1.0, min(1.0, score))
        except Exception:
            score = 0.0
        self._cache[key] = score
        return score


class MLExpectancyModel:
    """LightGBM-based trade quality predictor.

    Replaces / blends with the hand-crafted Bayesian ``bucket_expectancy``
    scalar once enough completed trades have been recorded.

    Feature vector (all numeric after one-hot encoding of categoricals):
      conviction, expectancy_scalar (Bayesian), localized_scalar,
      alpha_score, structural_r, side (+1/-1),
      setup_BREAKOUT, setup_PULLBACK, setup_TREND, setup_RETEST (one-hot),
      cls_crypto, cls_equity, cls_future (one-hot),
      regime_TREND_UP, regime_TREND_DOWN, regime_CHOP, regime_PANIC (one-hot)

    The model predicts E[R-multiple].  Its output is converted to a scalar
    in [0.45, 1.45] using the same tanh formula as ``bucket_expectancy`` so
    the downstream position-sizing code is unchanged.

    Requires ``lightgbm`` to be installed; falls back to None (use Bayesian
    scalar only) when unavailable or when < ``MIN_TRAIN_SAMPLES`` trades exist.
    """

    MIN_TRAIN_SAMPLES = 200   # minimum trades before first training run
    RETRAIN_EVERY     = 50    # retrain every N new trades after the first
    BLEND_WEIGHT      = 0.40  # weight given to ML prediction (1-w = Bayesian)

    def __init__(self):
        self._model = None
        self._X: List[List[float]] = []
        self._y: List[float] = []
        self._since_last_train = 0

    @staticmethod
    def _featurise(features: dict) -> List[float]:
        """Convert a candidate/entry feature dict to a numeric vector."""
        setup = features.get("setup", "")
        regime = features.get("regime", "")
        cls = features.get("cls", "")
        vec = [
            float(features.get("conviction",        1.0)),
            float(features.get("expectancy_scalar", 1.0)),
            float(features.get("localized_scalar",  1.0)),
            float(features.get("alpha_score",       0.0)),
            float(features.get("structural_r",      0.0)),
            float(features.get("side",              1)),
            # setup one-hots
            1.0 if "BREAKOUT"  in setup or "BREAKDOWN" in setup or "CONTINUATION" in setup else 0.0,
            1.0 if "PULLBACK"  in setup or "RETRACE"   in setup                             else 0.0,
            1.0 if "TREND"     in setup or "TREND_UP"  in setup or "TREND_DOWN"  in setup   else 0.0,
            1.0 if "RETEST"    in setup                                                      else 0.0,
            # class one-hots
            1.0 if cls == "crypto"  else 0.0,
            1.0 if cls == "equity"  else 0.0,
            1.0 if cls == "future"  else 0.0,
            # regime one-hots
            1.0 if regime in ("TREND_UP",   "UPTREND")   else 0.0,
            1.0 if regime in ("TREND_DOWN", "DOWNTREND") else 0.0,
            1.0 if regime == "CHOP"                      else 0.0,
            1.0 if regime == "PANIC"                     else 0.0,
        ]
        return vec

    def record_trade(self, features: dict, r_net: float):
        """Store a completed trade for the next training cycle."""
        if lgb is None:
            return
        vec = self._featurise(features)
        self._X.append(vec)
        self._y.append(r_net)
        self._since_last_train += 1
        n = len(self._y)
        if n >= self.MIN_TRAIN_SAMPLES and (
            self._model is None or self._since_last_train >= self.RETRAIN_EVERY
        ):
            self._train()

    def _train(self):
        """Fit a LightGBM regressor on all accumulated trade data."""
        if lgb is None or len(self._y) < self.MIN_TRAIN_SAMPLES:
            return
        try:
            import numpy as _np
            X = _np.array(self._X, dtype=_np.float32)
            y = _np.array(self._y, dtype=_np.float32)
            ds = lgb.Dataset(X, label=y)
            params = {
                "objective":      "regression",
                "metric":         "rmse",
                "num_leaves":     15,
                "learning_rate":  0.05,
                "feature_fraction": 0.8,
                "bagging_fraction": 0.8,
                "bagging_freq":   5,
                "min_data_in_leaf": 10,
                "verbosity":      -1,
            }
            self._model = lgb.train(
                params, ds, num_boost_round=120,
                valid_sets=[ds],
                callbacks=[lgb.early_stopping(20, verbose=False),
                           lgb.log_evaluation(period=-1)],
            )
            self._since_last_train = 0
            console.log(
                f"[cyan][MLExpectancy][/cyan] Retrained on {len(self._y)} trades."
            )
        except Exception as exc:
            console.log(f"[yellow][MLExpectancy] Training failed: {exc}[/yellow]")
            self._model = None

    def predict_scalar(self, features: dict, bayesian_scalar: float) -> float:
        """Return a blended expectancy scalar.

        When the ML model is not ready, returns *bayesian_scalar* unchanged.
        """
        if lgb is None or self._model is None:
            return bayesian_scalar
        try:
            import numpy as _np
            vec = _np.array([self._featurise(features)], dtype=_np.float32)
            ml_r = float(self._model.predict(vec)[0])
            ml_scalar = float(np.clip(1.0 + 0.60 * np.tanh(ml_r), 0.45, 1.45))
            w = self.BLEND_WEIGHT
            return float(np.clip(w * ml_scalar + (1.0 - w) * bayesian_scalar, 0.45, 1.45))
        except Exception:
            return bayesian_scalar


# =========================================================
# CSV BUFFER
# =========================================================

class CSVBuffer:
    def __init__(self, path: str, headers: List[str], flush_every: int = 25):
        self.path        = Path(path)
        self.active_path = Path(path)
        self.buffer: List = []
        self.flush_every = flush_every
        self.headers     = headers
        self._ensure_file()

    def _fallback_path(self) -> Path:
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.path.with_name(f"{self.path.stem}_{stamp}{self.path.suffix}")

    def _ensure_file(self):
        try:
            if not self.active_path.exists():
                with open(self.active_path, "w", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerow(self.headers)
        except PermissionError:
            self.active_path = self._fallback_path()
            with open(self.active_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(self.headers)
            console.log(f"[yellow]Output locked → {self.active_path.name}[/yellow]")

    def write(self, row: List):
        self.buffer.append(row)
        if len(self.buffer) >= self.flush_every:
            self.flush()

    def flush(self):
        if not self.buffer:
            return
        try:
            with open(self.active_path, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(self.buffer)
            self.buffer = []
        except PermissionError:
            fallback = self._fallback_path()
            with open(fallback, "a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                if fallback.stat().st_size == 0:
                    w.writerow(self.headers)
                w.writerows(self.buffer)
            console.log(f"[yellow]Permission denied → {fallback.name}[/yellow]")
            self.active_path = fallback
            self.buffer = []


# =========================================================
# OHLC STORE
# =========================================================

@dataclass
class OHLCBar:
    open:   float
    high:   float
    low:    float
    close:  float
    volume: float = 0.0


class OHLCHistory:
    def __init__(self, maxlen: int = MAX_HISTORY):
        self._bars: deque = deque(maxlen=maxlen)

    def append(self, bar: OHLCBar):
        self._bars.append(bar)

    def __len__(self) -> int:
        return len(self._bars)

    def arrays(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        o = np.array([b.open  for b in self._bars], dtype=float)
        h = np.array([b.high  for b in self._bars], dtype=float)
        l = np.array([b.low   for b in self._bars], dtype=float)
        c = np.array([b.close for b in self._bars], dtype=float)
        return o, h, l, c

    def close_array(self) -> np.ndarray:
        return np.array([b.close for b in self._bars], dtype=float)

    def volume_array(self) -> np.ndarray:
        return np.array([b.volume for b in self._bars], dtype=float)


# =========================================================
# DATA ACCESS
# =========================================================

def fetch_binance_klines(symbol: str, interval: str, start: str, end: str,
                         limit: int = 1000) -> pd.DataFrame:
    """Synchronous single-symbol Binance fetch (retained as fallback)."""
    start_ms = int(pd.Timestamp(start, tz="UTC").timestamp() * 1000)
    end_ms   = int(pd.Timestamp(end,   tz="UTC").timestamp() * 1000)
    rows, curr = [], start_ms

    while curr < end_ms:
        params = {"symbol": symbol, "interval": interval,
                  "startTime": curr, "endTime": end_ms, "limit": limit}
        try:
            r = requests.get(BINANCE_REST_URL, params=params, timeout=30)
            r.raise_for_status()
            batch = r.json()
        except Exception as e:
            console.log(f"[yellow]Binance error {symbol}: {e}[/yellow]")
            break
        if not batch:
            break
        rows.extend(batch)
        last_open_ms = int(batch[-1][0])
        curr = last_open_ms + (86_400_000 if interval == "1d" else 3_600_000)
        if len(batch) < limit:
            break
        time.sleep(0.05)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=[
        "OpenTime","Open","High","Low","Close","Volume",
        "CloseTime","QuoteAssetVolume","NumberOfTrades",
        "TakerBuyBaseAssetVolume","TakerBuyQuoteAssetVolume","Ignore"
    ])
    df["OpenTime"] = pd.to_datetime(df["OpenTime"], unit="ms", utc=True)
    for col in ["Open","High","Low","Close","Volume"]:
        df[col] = df[col].astype(float)
    df = df.set_index("OpenTime")
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df[["Open","High","Low","Close","Volume"]].copy()


async def _fetch_binance_klines_async(session, symbol: str, interval: str,
                                      start_ms: int, end_ms: int,
                                      limit: int = 1000) -> pd.DataFrame:
    """Async single-symbol Binance klines fetcher using an existing aiohttp session."""
    import aiohttp
    rows, curr = [], start_ms
    while curr < end_ms:
        params = {"symbol": symbol, "interval": interval,
                  "startTime": curr, "endTime": end_ms, "limit": limit}
        try:
            async with session.get(BINANCE_REST_URL, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                resp.raise_for_status()
                batch = await resp.json()
        except Exception as e:
            console.log(f"[yellow]Binance async error {symbol}: {e}[/yellow]")
            break
        if not batch:
            break
        rows.extend(batch)
        last_open_ms = int(batch[-1][0])
        curr = last_open_ms + (86_400_000 if interval == "1d" else 3_600_000)
        if len(batch) < limit:
            break
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows, columns=[
        "OpenTime","Open","High","Low","Close","Volume",
        "CloseTime","QuoteAssetVolume","NumberOfTrades",
        "TakerBuyBaseAssetVolume","TakerBuyQuoteAssetVolume","Ignore"
    ])
    df["OpenTime"] = pd.to_datetime(df["OpenTime"], unit="ms", utc=True)
    for col in ["Open","High","Low","Close","Volume"]:
        df[col] = df[col].astype(float)
    df = df.set_index("OpenTime")
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df[["Open","High","Low","Close","Volume"]].copy()


async def fetch_binance_klines_batch(symbols: List[str], interval: str,
                                     start: str, end: str) -> Dict[str, pd.DataFrame]:
    """Fetch klines for *all* symbols concurrently using a single aiohttp session.

    Returns a dict ``{binance_symbol: df}``.
    """
    try:
        import aiohttp
    except ModuleNotFoundError:
        # Fallback: sequential requests
        return {sym: fetch_binance_klines(sym, interval, start, end) for sym in symbols}

    start_ms = int(pd.Timestamp(start, tz="UTC").timestamp() * 1000)
    end_ms   = int(pd.Timestamp(end,   tz="UTC").timestamp() * 1000)

    async with aiohttp.ClientSession() as session:
        tasks = [
            _fetch_binance_klines_async(session, sym, interval, start_ms, end_ms)
            for sym in symbols
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    out: Dict[str, pd.DataFrame] = {}
    for sym, res in zip(symbols, results):
        if isinstance(res, Exception):
            console.log(f"[yellow]Binance batch error {sym}: {res}[/yellow]")
            out[sym] = pd.DataFrame()
        else:
            out[sym] = res
    return out


def _normalise_yf_df(df, symbol: str) -> pd.DataFrame:
    """Normalise a raw yfinance DataFrame (flat or MultiIndex) to OHLCV Title-Case columns."""
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        ohlcv = {"open", "high", "low", "close", "volume", "adj close"}
        l0 = {str(c).lower() for c in df.columns.get_level_values(0)}
        l1 = {str(c).lower() for c in df.columns.get_level_values(1)}
        if l0 & ohlcv:
            df.columns = [str(c[0]) for c in df.columns]
        elif l1 & ohlcv:
            df.columns = [str(c[1]) for c in df.columns]
        else:
            df.columns = [str(c[0]) for c in df.columns]
    df.columns = [c.strip().title() for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated(keep="first")]
    keep = [c for c in ["Open","High","Low","Close","Volume"] if c in df.columns]
    if not keep or "Close" not in keep:
        return pd.DataFrame()
    df = df[keep].copy()
    df.index = pd.to_datetime(df.index, utc=True)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df


def fetch_yfinance_batch(symbols: List[str], start: str, end: str,
                         interval: str = "1d") -> Dict[str, pd.DataFrame]:
    """Fetch each symbol independently in parallel threads via yf.Ticker.history().

    **Why per-symbol instead of yf.download(all_tickers)?**

    ``yf.download()`` with multiple tickers is known to intermittently return
    one ticker's price series replicated across ALL other tickers in the same
    call — a "cross-contamination" bug in the yfinance library that cannot be
    reliably detected after the fact.  Using per-symbol ``Ticker.history()``
    calls makes contamination structurally impossible: each call returns data
    for exactly one symbol, so there is nothing to cross-contaminate.

    ``ThreadPoolExecutor`` parallelises the I/O-bound HTTP requests so wall-
    clock time is comparable to the original single-batch call (~2-5 s for
    13 equities on a typical connection).
    """
    if yf is None or not symbols:
        return {s: pd.DataFrame() for s in symbols}

    def _fetch_one(sym: str) -> Tuple[str, pd.DataFrame]:
        try:
            ticker = yf.Ticker(sym)
            df = ticker.history(start=start, end=end, interval=interval,
                                auto_adjust=False)
            return sym, _normalise_yf_df(df, sym)
        except Exception as exc:
            console.log(f"[yellow]yfinance error {sym}: {exc}[/yellow]")
            return sym, pd.DataFrame()

    workers = min(len(symbols), 8)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        return dict(pool.map(_fetch_one, symbols))


def fetch_yfinance_history(symbol: str, start: str, end: str,
                           interval: str = "1d") -> pd.DataFrame:
    """Single-symbol yfinance fetch using per-ticker Ticker.history().

    Deliberately avoids ``yf.download()`` which is known to return one
    ticker's price series replicated across all requested tickers when
    called with multiple symbols, and occasionally misbehaves even for
    a single symbol in newer yfinance versions.  ``Ticker.history()``
    is structurally isolated — each call retrieves data for exactly one
    symbol — so cross-symbol contamination is impossible.
    """
    if yf is None:
        return pd.DataFrame()
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, interval=interval,
                            auto_adjust=False)
        return _normalise_yf_df(df, symbol)
    except Exception as e:
        console.log(f"[yellow]yfinance error {symbol}: {e}[/yellow]")
        return pd.DataFrame()


# =========================================================
# POLYGON.IO DATA FETCHERS
# =========================================================

_POLYGON_TIMESPAN = {"1d": "day", "1h": "hour", "1m": "minute"}


def fetch_polygon_history(symbol: str, start: str, end: str,
                          interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLCV history from Polygon.io for a single symbol.

    Uses the official ``polygon-api-client`` REST wrapper.  Returns an empty
    DataFrame when the package is missing, the API key is absent, or the
    ticker is not available on the caller's plan (e.g. futures on free tier).

    Args:
        symbol: Model asset ticker (e.g. ``"SPY"``, ``"BTC-USD"``).  The
                function resolves the Polygon.io ticker via ``POLYGON_MAP``
                before the API call.
        start, end: ISO-8601 date strings (``"YYYY-MM-DD"``).
        interval: yfinance-style interval string (``"1d"``, ``"1h"``).
    """
    if _PolygonRESTClient is None or not _POLYGON_API_KEY:
        return pd.DataFrame()
    poly_sym = POLYGON_MAP.get(symbol)
    if poly_sym is None:
        return pd.DataFrame()
    timespan = _POLYGON_TIMESPAN.get(interval, "day")
    try:
        client = _PolygonRESTClient(_POLYGON_API_KEY)
        aggs = list(client.get_aggs(
            poly_sym, 1, timespan, start, end,
            adjusted=True, limit=50_000,
        ))
        if not aggs:
            return pd.DataFrame()
        rows = [
            {
                "Open":   a.open,
                "High":   a.high,
                "Low":    a.low,
                "Close":  a.close,
                "Volume": a.volume,
                "ts":     pd.Timestamp(a.timestamp, unit="ms", tz="UTC"),
            }
            for a in aggs
        ]
        df = pd.DataFrame(rows).set_index("ts")
        df.index.name = None
        df = df[~df.index.duplicated(keep="last")].sort_index()
        return df
    except Exception as e:
        console.log(f"[yellow]Polygon.io error {symbol}: {e}[/yellow]")
        return pd.DataFrame()


def fetch_polygon_batch(symbols: List[str], start: str, end: str,
                        interval: str = "1d") -> Dict[str, pd.DataFrame]:
    """Fetch multiple symbols from Polygon.io in parallel using a single client.

    A single ``_PolygonRESTClient`` instance is created and shared across all
    worker threads — the polygon-api-client is thread-safe for read operations.
    ``ThreadPoolExecutor`` parallelises the I/O-bound HTTP requests so that
    rate-limit back-off and network latency are absorbed concurrently rather
    than sequentially, reducing wall-clock fetch time from O(N) to O(1).

    Only symbols present in ``POLYGON_MAP`` are fetched; the rest receive an
    empty DataFrame so the caller can route them to a fallback source.
    """
    if _PolygonRESTClient is None or not _POLYGON_API_KEY or not symbols:
        return {sym: pd.DataFrame() for sym in symbols}

    client = _PolygonRESTClient(_POLYGON_API_KEY)
    timespan = _POLYGON_TIMESPAN.get(interval, "day")

    def _fetch_one(sym: str) -> Tuple[str, pd.DataFrame]:
        poly_sym = POLYGON_MAP.get(sym)
        if poly_sym is None:
            return sym, pd.DataFrame()
        try:
            aggs = list(client.get_aggs(
                poly_sym, 1, timespan, start, end,
                adjusted=True, limit=50_000,
            ))
            if not aggs:
                return sym, pd.DataFrame()
            rows = [
                {
                    "Open":   a.open,
                    "High":   a.high,
                    "Low":    a.low,
                    "Close":  a.close,
                    "Volume": a.volume,
                    "ts":     pd.Timestamp(a.timestamp, unit="ms", tz="UTC"),
                }
                for a in aggs
            ]
            df = pd.DataFrame(rows).set_index("ts")
            df.index.name = None
            df = df[~df.index.duplicated(keep="last")].sort_index()
            return sym, df
        except Exception as exc:
            console.log(f"[yellow]Polygon.io error {sym}: {exc}[/yellow]")
            return sym, pd.DataFrame()

    workers = min(len(symbols), 8)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        return dict(pool.map(_fetch_one, symbols))


# =========================================================
# PRICE VALIDATOR
# =========================================================

class PriceValidator:
    """Validates OHLCV DataFrames before they are accepted into the model.

    Three-layer defence against mis-attributed or corrupted price data:

    1. **Structural integrity** — High ≥ max(Open, Close) ≥ min(Open, Close) ≥ Low > 0
       for every row.  Any row that fails this is considered corrupted.
    2. **Plausibility range** — Each asset has a wide but finite expected price
       range defined in ``PRICE_PLAUSIBILITY_RANGE``.  A median price outside
       that range almost certainly means a different asset's data was returned
       (e.g. SPY price appearing under BTC-USD).
    3. **Inter-bar gap check** — A single calendar day should not produce a
       log-return larger than ±60% in absolute value.  Larger moves indicate
       either a data-source error or a corporate action that slipped through
       unadjusted.

    All checks are non-destructive: the validator returns a boolean and
    logs a reason string; the caller decides what to do with a failed result.
    """

    # Maximum acceptable abs(log-return) between consecutive daily bars.
    MAX_DAILY_LOG_RETURN = 0.60   # ≈ 82% up / 45% down

    # Minimum fraction of rows that must pass structural integrity checks.
    MIN_VALID_ROW_FRACTION = 0.95

    @classmethod
    def validate_df(cls, df: pd.DataFrame, asset: str) -> Tuple[bool, str]:
        """Return (is_valid, reason_string) for a full history DataFrame."""
        if df is None or df.empty:
            return False, "empty dataframe"
        required = {"Open", "High", "Low", "Close"}
        if not required.issubset(df.columns):
            missing = required - set(df.columns)
            return False, f"missing columns: {missing}"

        o = df["Open"].to_numpy(dtype=float)
        h = df["High"].to_numpy(dtype=float)
        l = df["Low"].to_numpy(dtype=float)
        c = df["Close"].to_numpy(dtype=float)

        # --- 1. Structural integrity ------------------------------------------
        bad_rows = (
            (h < l) |
            (h < o) | (h < c) |
            (l > o) | (l > c) |
            (l <= 0) | (c <= 0)
        )
        bad_fraction = float(np.sum(bad_rows)) / len(bad_rows)
        if bad_fraction > (1.0 - cls.MIN_VALID_ROW_FRACTION):
            return False, (
                f"{bad_fraction*100:.1f}% of rows fail OHLC integrity "
                f"(>{(1-cls.MIN_VALID_ROW_FRACTION)*100:.0f}% threshold)"
            )

        # --- 2. Plausibility range --------------------------------------------
        lo_bound, hi_bound = PRICE_PLAUSIBILITY_RANGE.get(asset, (0.0, float("inf")))
        median_close = float(np.nanmedian(c))
        if not (lo_bound <= median_close <= hi_bound):
            return False, (
                f"median close {median_close:.4f} outside expected range "
                f"[{lo_bound}, {hi_bound}] for {asset}"
            )

        # --- 3. Inter-bar gap check -------------------------------------------
        valid_c = c[~np.isnan(c)]
        if len(valid_c) >= 2:
            log_rets = np.abs(np.diff(np.log(valid_c[valid_c > 0])))
            if len(log_rets) > 0 and float(np.max(log_rets)) > cls.MAX_DAILY_LOG_RETURN:
                # A single extreme move is suspicious; flag only if it exceeds
                # the hard limit by more than 2× (leaves room for crypto crashes).
                worst = float(np.max(log_rets))
                if worst > cls.MAX_DAILY_LOG_RETURN * 2.0:
                    return False, (
                        f"largest abs daily log-return {worst:.3f} exceeds "
                        f"2× limit ({cls.MAX_DAILY_LOG_RETURN*2:.2f}) — "
                        "possible data error or unadjusted split"
                    )

        return True, "ok"

    @classmethod
    def validate_bar(cls, bar: dict, asset: str) -> Tuple[bool, str]:
        """Validate a single OHLCV bar dict (keys: open/high/low/close)."""
        o = bar.get("open",  float("nan"))
        h = bar.get("high",  float("nan"))
        l = bar.get("low",   float("nan"))
        c = bar.get("close", float("nan"))
        if any(np.isnan(v) for v in [o, h, l, c]):
            return False, "NaN in OHLC"
        if l <= 0 or c <= 0:
            return False, "non-positive price"
        if h < l or h < o or h < c or l > o or l > c:
            return False, "OHLC relationship violated"
        lo_bound, hi_bound = PRICE_PLAUSIBILITY_RANGE.get(asset, (0.0, float("inf")))
        if not (lo_bound <= c <= hi_bound):
            return False, (
                f"close {c:.4f} outside expected range [{lo_bound}, {hi_bound}]"
            )
        return True, "ok"


_CACHE_DIR = Path(os.environ.get("PRICE_CACHE_DIR", ".price_cache"))
# Override the cache location with the PRICE_CACHE_DIR environment variable,
# e.g. ``export PRICE_CACHE_DIR=/tmp/trading_cache`` for a tmpfs-backed cache.
_CACHE_TTL_HOURS = 23  # treat cached data as fresh for this many hours
# Bump this string whenever a data-quality fix is deployed.  All history cache
# files whose name does NOT contain this token are deleted on DataProvider
# startup, so stale or contaminated parquet files never survive across versions.
_CACHE_VERSION = "v4"  # bumped: fetch_yfinance_history now uses Ticker.history()


class DataProvider:
    """Unified price-data access with on-disk parquet caching.

    Backtest usage (``get_history_batch``):
        Data source priority per asset:
          1. Polygon.io  — all equity and crypto assets in ``POLYGON_MAP``
                           when ``POLYGON_API_KEY`` is configured.
          2. Binance      — crypto assets when Polygon.io is unavailable.
          3. yfinance     — equities, futures, and any asset where Polygon
                           returns no data (single-symbol fallback included).
        Results are serialised to ``.price_cache/`` as parquet; subsequent
        calls within 23 hours return cached data instantly, making repeated
        Optuna trials essentially free after the first download.

    Live usage (``get_latest_bar``):
        Maintains a per-asset append-only parquet file.  On each poll cycle
        the last row is returned from the cache; the network is only hit when
        the last stored date is before today UTC.
    """

    def __init__(self, cache_dir: Path = _CACHE_DIR):
        self._cache_dir = cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        # On startup remove every parquet file that does NOT carry the current
        # cache-version token.  This ensures that contaminated or stale history
        # files written by any previous code version are instantly evicted and
        # never served again.  Bumping _CACHE_VERSION is therefore the single,
        # guaranteed way to invalidate ALL cached price data.
        for _p in self._cache_dir.glob("*.parquet"):
            if _CACHE_VERSION not in _p.name:
                try:
                    _p.unlink()
                except OSError:
                    pass

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _history_cache_path(self, asset: str, start: str, end: str, interval: str) -> Path:
        safe = asset.replace("=", "_").replace("-", "_")
        key  = f"{safe}_{start}_{end}_{interval}_{_CACHE_VERSION}"
        return self._cache_dir / f"{key}.parquet"

    def _live_cache_path(self, asset: str) -> Path:
        safe = asset.replace("=", "_").replace("-", "_")
        return self._cache_dir / f"live_{safe}_{_CACHE_VERSION}.parquet"

    def _cache_is_fresh(self, path: Path) -> bool:
        if not path.exists():
            return False
        age_h = (time.time() - path.stat().st_mtime) / 3600
        return age_h < _CACHE_TTL_HOURS

    def _write_parquet(self, df: pd.DataFrame, path: Path) -> None:
        try:
            df.to_parquet(path)
        except Exception as e:
            console.log(f"[yellow]Cache write failed {path.name}: {e}[/yellow]")

    def _read_parquet(self, path: Path) -> pd.DataFrame:
        try:
            df = pd.read_parquet(path)
            df.index = pd.to_datetime(df.index, utc=True)
            return df
        except Exception as e:
            console.log(f"[yellow]Cache read failed {path.name}: {e}[/yellow]")
            return pd.DataFrame()

    # ------------------------------------------------------------------
    # Batch history fetch (backtest / preload)
    # ------------------------------------------------------------------

    @staticmethod
    def _contaminated_assets(result: Dict[str, pd.DataFrame]) -> List[str]:
        """Return assets whose last-Close price is shared by at least one other asset.

        When ``yf.download`` returns cross-contaminated data (one ticker's
        price replicated for many tickers) the last-Close values across many
        symbols are identical.  Comparing across the full result dict catches
        contamination regardless of whether the data came from a live network
        request or from the on-disk cache.

        Threshold is **2** (count ≥ 2, i.e. at least one other asset shares
        the same last-close): two assets sharing an identical last-close price
        is already implausible across the 22-asset universe and warrants a
        re-fetch.  The previous threshold of 3 missed two-asset contamination
        (e.g. SPY data returned for both AAPL and MSFT).
        """
        last_closes: Dict[str, float] = {}
        for asset, df in result.items():
            if not df.empty and "Close" in df.columns:
                series = df["Close"].dropna()
                if not series.empty:
                    last_closes[asset] = round(float(series.iat[-1]), 4)
        price_counts = Counter(last_closes.values())
        return [a for a, p in last_closes.items() if price_counts[p] >= 2]

    def get_history_batch(self, assets: List[str], start: str, end: str,
                          interval: str = DATA_INTERVAL) -> Dict[str, pd.DataFrame]:
        """Return ``{asset: df}`` for all assets, using cache where possible.

        Fetch priority (per asset class):
          1. Polygon.io batch  — equities and crypto in ``POLYGON_MAP`` when
                                 ``POLYGON_API_KEY`` is set.
          2. yfinance batch    — equities/futures not served by Polygon.
          3. Async Binance     — crypto not served by Polygon.
        """
        result: Dict[str, pd.DataFrame] = {}
        need_polygon: List[str] = []
        need_yf:      List[str] = []
        need_crypto:  List[str] = []

        # Check cache for each asset; validate cached data with PriceValidator
        # before accepting it so stale or contaminated parquet files written by
        # older code versions are rejected even if the cache TTL has not expired.
        for asset in assets:
            path = self._history_cache_path(asset, start, end, interval)
            if self._cache_is_fresh(path):
                df = self._read_parquet(path)
                if not df.empty:
                    ok, reason = PriceValidator.validate_df(df, asset)
                    if ok:
                        result[asset] = df
                        continue
                    else:
                        console.log(
                            f"[yellow]Cached data for {asset} failed validation "
                            f"({reason}); re-fetching.[/yellow]"
                        )
                        try:
                            path.unlink(missing_ok=True)
                        except OSError:
                            pass
            cls = ASSET_CLASS.get(asset)
            if asset in POLYGON_MAP and _POLYGON_API_KEY and _PolygonRESTClient is not None:
                need_polygon.append(asset)
            elif cls == "crypto":
                need_crypto.append(asset)
            else:
                need_yf.append(asset)

        # Polygon.io batch (equities + crypto with X: prefix)
        if need_polygon:
            poly_batch = fetch_polygon_batch(need_polygon, start, end, interval)
            for asset, df in poly_batch.items():
                if not df.empty:
                    ok, reason = PriceValidator.validate_df(df, asset)
                    if ok:
                        result[asset] = df
                        self._write_parquet(df, self._history_cache_path(asset, start, end, interval))
                    else:
                        console.log(
                            f"[yellow]Polygon data for {asset} failed validation "
                            f"({reason}); falling back.[/yellow]"
                        )
                        cls = ASSET_CLASS.get(asset)
                        if cls == "crypto":
                            need_crypto.append(asset)
                        else:
                            need_yf.append(asset)
                else:
                    # Polygon returned nothing - route to the appropriate fallback
                    cls = ASSET_CLASS.get(asset)
                    if cls == "crypto":
                        need_crypto.append(asset)
                    else:
                        need_yf.append(asset)

        # Batch-fetch equities / futures via yfinance; fall back to
        # per-symbol fetches for any ticker the batch returned empty.
        # A flat (non-MultiIndex) batch response returns empty DataFrames for
        # all symbols in the batch — without the per-symbol fallback those
        # assets would silently have no data, causing NaN prices that look
        # equivalent across assets in the status table.
        if need_yf:
            batch = fetch_yfinance_batch(need_yf, start, end, interval)
            for asset, df in batch.items():
                if df.empty:
                    # Batch gave nothing for this symbol: try a targeted single
                    # fetch so each asset gets its own independent price series.
                    try:
                        df = fetch_yfinance_history(asset, start, end, interval=interval)
                    except Exception as _yf_exc:
                        console.log(f"[yellow]yfinance single-fetch fallback error {asset}: {_yf_exc}[/yellow]")
                        df = pd.DataFrame()
                if not df.empty:
                    ok, reason = PriceValidator.validate_df(df, asset)
                    if ok:
                        result[asset] = df
                        self._write_parquet(df, self._history_cache_path(asset, start, end, interval))
                    else:
                        console.log(
                            f"[yellow]yfinance data for {asset} failed validation "
                            f"({reason}); asset will have no data this run.[/yellow]"
                        )
                        result[asset] = pd.DataFrame()
                else:
                    result[asset] = df

        # Concurrent-fetch crypto via Binance
        if need_crypto:
            binance_syms = [BINANCE_MAP[a] for a in need_crypto]
            try:
                # Determine whether we are already inside a running event loop
                # (live-polling mode) or called from a plain thread / the main
                # thread (backtest mode).
                #
                # asyncio.get_event_loop() raises RuntimeError on Python ≥ 3.10
                # when called from a worker thread that has no current loop, so
                # we probe with get_running_loop() instead, which is safe.
                try:
                    running_loop = asyncio.get_running_loop()
                except RuntimeError:
                    running_loop = None

                if running_loop is not None:
                    # Already inside an async event loop - spin up a fresh
                    # thread so we can use asyncio.run() without conflicting
                    # with the outer loop.
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                        fut = ex.submit(
                            asyncio.run,
                            fetch_binance_klines_batch(binance_syms, interval, start, end),
                        )
                        crypto_batch = fut.result(timeout=120)
                else:
                    # Plain thread context (e.g. backtest, Optuna trial,
                    # run_in_executor worker) - safe to call asyncio.run().
                    crypto_batch = asyncio.run(
                        fetch_binance_klines_batch(binance_syms, interval, start, end)
                    )
            except Exception as e:
                console.log(f"[yellow]Async Binance batch error: {e}[/yellow]")
                crypto_batch = {sym: pd.DataFrame() for sym in binance_syms}

            for asset, bsym in zip(need_crypto, binance_syms):
                df = crypto_batch.get(bsym, pd.DataFrame())
                if not df.empty:
                    ok, reason = PriceValidator.validate_df(df, asset)
                    if ok:
                        result[asset] = df
                        self._write_parquet(df, self._history_cache_path(asset, start, end, interval))
                    else:
                        console.log(
                            f"[yellow]Binance data for {asset} ({bsym}) failed "
                            f"validation ({reason}); asset will have no data this run.[/yellow]"
                        )
                        result[asset] = pd.DataFrame()
                else:
                    result[asset] = df

        # Final cross-asset contamination check.
        # Runs over the FULL result dict (covers cache hits, fresh fetches, and
        # any source).  If the same last-Close price appears for 2+ assets the
        # batch download — or a previously cached contaminated response — has
        # blended one ticker's price series into many others.  Re-fetch those
        # assets individually via the full priority chain (Polygon → Binance →
        # yfinance), overwriting any bad cache file so the error cannot persist.
        bad = self._contaminated_assets(result)
        if bad:
            for asset in bad:
                console.log(
                    f"[yellow]Cross-asset contamination in result for {asset}; "
                    f"re-fetching individually.[/yellow]"
                )
                try:
                    df = fetch_asset_history(asset, start, end, interval)
                except Exception as _exc:
                    console.log(f"[yellow]Individual re-fetch error {asset}: {_exc}[/yellow]")
                    df = pd.DataFrame()
                result[asset] = df
                # Overwrite the contaminated cache entry (even if df is empty,
                # writing an empty file is fine — it will simply not be cached).
                cache_path = self._history_cache_path(asset, start, end, interval)
                if not df.empty:
                    self._write_parquet(df, cache_path)
                else:
                    # Remove bad cache file so the next run tries again
                    try:
                        cache_path.unlink(missing_ok=True)
                    except OSError:
                        pass

        return result

    def get_history(self, asset: str, start: str, end: str,
                    interval: str = DATA_INTERVAL) -> pd.DataFrame:
        """Single-asset history fetch, cache-aware."""
        path = self._history_cache_path(asset, start, end, interval)
        if self._cache_is_fresh(path):
            df = self._read_parquet(path)
            if not df.empty:
                return df
        df = fetch_asset_history(asset, start, end, interval)
        if not df.empty:
            self._write_parquet(df, path)
        return df

    # ------------------------------------------------------------------
    # Incremental live-bar fetch
    # ------------------------------------------------------------------

    def get_latest_bar(self, asset: str) -> Optional[Tuple[pd.Timestamp, dict]]:
        """Return the most-recently *closed* daily bar for *asset*.

        Reads from a per-asset parquet cache; hits the network only when the
        last stored row is older than today UTC, avoiding a full 10-day
        re-download on every poll cycle.
        """
        now_utc  = pd.Timestamp.now("UTC")
        today    = now_utc.date()
        path     = self._live_cache_path(asset)

        cached: pd.DataFrame = pd.DataFrame()
        if path.exists():
            cached = self._read_parquet(path)

        # Determine whether we need to refresh from the network
        need_refresh = True
        if not cached.empty:
            last_cached_date = cached.index[-1].date()
            # The most-recent closed bar is yesterday (or earlier) because
            # today's bar is still forming; refresh only if the cache lags.
            if last_cached_date >= (today - datetime.timedelta(days=1)):
                need_refresh = False

        if need_refresh:
            end   = now_utc
            start = end - pd.Timedelta(days=10)
            try:
                fresh = fetch_asset_history(
                    asset,
                    start.strftime("%Y-%m-%d"),
                    end.strftime("%Y-%m-%d"),
                    DATA_INTERVAL,
                )
            except Exception as exc:
                console.log(f"[yellow]Live fetch error {asset}: {exc}[/yellow]")
                fresh = pd.DataFrame()

            if not fresh.empty:
                ok, reason = PriceValidator.validate_df(fresh, asset)
                if not ok:
                    console.log(
                        f"[yellow]Live fetch for {asset} failed validation "
                        f"({reason}); retaining cached data.[/yellow]"
                    )
                    fresh = pd.DataFrame()

            if not fresh.empty:
                # Merge new rows into cache and persist
                if cached.empty:
                    merged = fresh
                else:
                    merged = pd.concat([cached, fresh])
                    merged = merged[~merged.index.duplicated(keep="last")].sort_index()
                self._write_parquet(merged, path)
                cached = merged

        if cached.empty or not all(c in cached.columns for c in ["Open","High","Low","Close"]):
            return None

        # Discard any still-forming bar from today
        if cached.index[-1].date() >= today:
            cached = cached.iloc[:-1]
        if cached.empty:
            return None

        ts  = cached.index[-1]
        bar = {
            "open":  float(cached["Open"].iat[-1]),
            "high":  float(cached["High"].iat[-1]),
            "low":   float(cached["Low"].iat[-1]),
            "close": float(cached["Close"].iat[-1]),
        }

        # Final single-bar validation before returning to the live loop
        ok, reason = PriceValidator.validate_bar(bar, asset)
        if not ok:
            console.log(
                f"[yellow]Latest bar for {asset} failed validation ({reason}); "
                f"skipping this poll cycle.[/yellow]"
            )
            return None

        return ts, bar


# Module-level singleton used by load_backtest_data, preload_live_history, etc.
_data_provider = DataProvider()


def fetch_asset_history(asset: str, start: str, end: str,
                        interval: str = DATA_INTERVAL) -> pd.DataFrame:
    """Fetch historical OHLCV data for *asset*.

    Priority order:
        1. Polygon.io  — for any asset listed in ``POLYGON_MAP`` (equities +
                         crypto) when ``POLYGON_API_KEY`` is set.
        2. Binance     — for crypto assets when Polygon.io is unavailable or
                         returns no data.
        3. yfinance    — for equities and futures as the final fallback.

    Each source's result is validated by ``PriceValidator`` before it is
    returned.  If a source returns data that fails validation, the next
    source in the priority chain is tried.  An empty DataFrame is returned
    only when all sources are exhausted.
    """
    asset_cls = ASSET_CLASS[asset]

    def _try(df: pd.DataFrame) -> Optional[pd.DataFrame]:
        if df.empty:
            return None
        ok, reason = PriceValidator.validate_df(df, asset)
        if ok:
            return df
        console.log(f"[yellow]{asset} fetch validation failed ({reason})[/yellow]")
        return None

    # --- Polygon.io (primary for equities and crypto) ---------------------
    if asset in POLYGON_MAP:
        result = _try(fetch_polygon_history(asset, start, end, interval))
        if result is not None:
            return result

    # --- Binance (primary for crypto when Polygon is unavailable) ---------
    if asset_cls == "crypto":
        result = _try(fetch_binance_klines(BINANCE_MAP[asset], interval, start, end))
        if result is not None:
            return result
        # Crypto Polygon fallback already tried above; return empty
        return pd.DataFrame()

    # --- yfinance (equities + futures fallback) ---------------------------
    result = _try(fetch_yfinance_history(asset, start, end, interval=interval))
    if result is not None:
        return result
    return pd.DataFrame()


# Wrap the outer entry point with retry (3 attempts, 2-s initial delay)
fetch_asset_history = _with_retry(fetch_asset_history, retries=3, delay=2.0)


# =========================================================
# POSITION STATE
# =========================================================

@dataclass
class Position:
    side:               int   = 0
    entry_price:        float = 0.0
    entry_atr:          float = 0.0
    stop_price:         float = 0.0
    units:              float = 0.0
    risk_usd:           float = 0.0
    entry_ts:           str   = ""
    bars_held:          int   = 0
    highest_price:      float = 0.0
    lowest_price:       float = 0.0
    trail_active:       bool  = False
    peak_r:             float = 0.0
    cooldown:           int   = 0
    flip_confirm_count: int   = 0
    # Tracks consecutive CHOP-regime bars while in a future position (used by
    # CHOP_REGIME exit in handle_futures to close profit-bearing trades that
    # have stalled rather than reversed cleanly).
    chop_regime_count:  int   = 0
    # Equity rank-exit persistence counter
    rank_exit_count:    int   = 0
    # Set to True once a partial-profit scale-out has been taken
    scaled_out:         bool  = False
    # Original stop distance at entry (atr_val * stop_mult).  Stored so that
    # exit_position and current_trade_r always normalise R against the *initial*
    # risk rather than the post-breakeven-lock stop, which is 10% of the
    # original and would otherwise inflate R and PnL by 10× after a partial
    # profit scale-out.
    initial_stop_dist:  float = 0.0


# =========================================================
# MODEL
# =========================================================

class MultiAssetTradingModel:
    def __init__(self):
        self.equity         = INITIAL_CAPITAL
        self.peak_equity    = INITIAL_CAPITAL
        self.max_dd         = 0.0
        self.trading_halted = False

        self.positions:    Dict[str, Position]    = {a: Position()    for a in ALL_ASSETS}
        self.ohlc_history: Dict[str, OHLCHistory] = {a: OHLCHistory() for a in ALL_ASSETS}
        self.latest_price: Dict[str, float]       = {a: np.nan        for a in ALL_ASSETS}

        self.curr_atr:    Dict[str, float] = {a: np.nan for a in ALL_ASSETS}
        self.curr_rsi:    Dict[str, float] = {a: np.nan for a in ALL_ASSETS}
        self.curr_signal: Dict[str, str]   = {a: "-"    for a in ALL_ASSETS}

        self.btc_trend  = "UNKNOWN"
        self.daily_key: Optional[str] = None
        self.daily_r    = {a: 0.0 for a in ALL_ASSETS}

        self._equity_series: List[float] = [INITIAL_CAPITAL]
        # One MTM-equity snapshot per bar - used for accurate Sharpe and max-DD
        self._daily_equity: List[float]  = [INITIAL_CAPITAL]

        self.performance = {
            "entries": 0, "exits": 0,
            "wins": 0, "losses": 0,
            "total_r": 0.0, "total_pnl": 0.0,
            "win_r_sum": 0.0, "loss_r_sum": 0.0,
            "max_win_r": 0.0, "max_loss_r": 0.0,
        }
        self.class_perf: Dict[str, Dict] = self._new_class_perf()
        self._futures_trades_r: List[float] = []
        self._all_trades_r:     List[float] = []

        self.telemetry = CSVBuffer(TELEMETRY_FILE, [
            "Timestamp","Asset","Class","Price","ATR","RSI","Signal",
            "PositionSide","BarsHeld","PeakR","TrailActive","DailyR",
            "Equity","DrawdownPct","BTCTrend"
        ])
        self.trades = CSVBuffer(TRADES_FILE, [
            "EntryTS","ExitTS","Asset","Class","Side",
            "EntryPrice","ExitPrice","Units","EntryATR",
            "BarsHeld","R_Gross","R_Net","PnL_USD","RiskUSD","ExitReason"
        ])

        # Live trading: set by run_live_polling; None in backtesting
        self._broker: Optional[AlpacaBroker] = None

    # --------------------------------------------------
    # State persistence (live trading)
    # --------------------------------------------------

    def save_state(self, path: str) -> None:
        """Persist equity, positions, and performance counters to *path* (JSON)."""
        positions_data: Dict[str, dict] = {}
        for asset, pos in self.positions.items():
            if pos.side != 0 or pos.cooldown > 0:
                positions_data[asset] = {
                    "side":               pos.side,
                    "entry_price":        pos.entry_price,
                    "entry_atr":          pos.entry_atr,
                    "stop_price":         pos.stop_price,
                    "units":              pos.units,
                    "risk_usd":           pos.risk_usd,
                    "entry_ts":           pos.entry_ts,
                    "bars_held":          pos.bars_held,
                    "highest_price":      pos.highest_price,
                    "lowest_price":       pos.lowest_price,
                    "trail_active":       pos.trail_active,
                    "peak_r":             pos.peak_r,
                    "cooldown":           pos.cooldown,
                    "flip_confirm_count": pos.flip_confirm_count,
                    "rank_exit_count":    pos.rank_exit_count,
                    "scaled_out":         pos.scaled_out,
                    "setup_type":         getattr(pos, "setup_type", "GENERIC"),
                    "regime":             getattr(pos, "regime", "UNKNOWN"),
                    "expected_r":         getattr(pos, "expected_r", 0.0),
                    "expectancy_scalar":  getattr(pos, "expectancy_scalar", 1.0),
                    "localized_scalar":   getattr(pos, "localized_scalar", 1.0),
                    "entry_score":        getattr(pos, "entry_score", 1.0),
                    "trade_mfe_r":        getattr(pos, "trade_mfe_r", 0.0),
                    "trade_mae_r":        getattr(pos, "trade_mae_r", 0.0),
                    "initial_stop_dist":  getattr(pos, "initial_stop_dist", 0.0),
                }
        state = {
            "equity":          self.equity,
            "peak_equity":     self.peak_equity,
            "max_dd":          self.max_dd,
            "trading_halted":  self.trading_halted,
            "daily_key":       self.daily_key,
            "daily_r":         self.daily_r,
            "performance":     self.performance,
            "class_perf":      self.class_perf,
            "all_trades_r":    self._all_trades_r,
            "futures_trades_r":self._futures_trades_r,
            "daily_equity":    self._daily_equity[-500:],  # last 500 daily snapshots
            "latest_price":    {k: (v if not np.isnan(v) else None)
                                for k, v in self.latest_price.items()},
            "positions":       positions_data,
            "saved_at":        pd.Timestamp.now("UTC").isoformat(),
        }
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp, path)
        console.log(f"[cyan]State saved → {path}[/cyan]")

    def load_state(self, path: str) -> bool:
        """Restore state from *path*. Returns True on success."""
        if not os.path.exists(path):
            return False
        try:
            with open(path) as f:
                state = json.load(f)
            self.equity          = float(state["equity"])
            self.peak_equity     = float(state["peak_equity"])
            self.max_dd          = float(state["max_dd"])
            self.trading_halted  = bool(state["trading_halted"])
            self.daily_key       = state.get("daily_key")
            self.daily_r         = {k: float(v) for k, v in state["daily_r"].items()}
            self.performance     = state["performance"]
            self.class_perf      = state["class_perf"]
            self._all_trades_r   = [float(x) for x in state.get("all_trades_r", [])]
            self._futures_trades_r = [float(x) for x in state.get("futures_trades_r", [])]
            daily_eq             = [float(x) for x in state.get("daily_equity", [self.equity])]
            self._daily_equity   = daily_eq
            for asset, v in state.get("latest_price", {}).items():
                if asset in self.latest_price:
                    self.latest_price[asset] = float(v) if v is not None else np.nan
            for asset, pdata in state.get("positions", {}).items():
                if asset not in self.positions:
                    continue
                pos = Position()
                for k, v in pdata.items():
                    if hasattr(pos, k):
                        setattr(pos, k, v)
                self.positions[asset] = pos
            console.log(
                f"[cyan]State loaded from {path} "
                f"(equity=${self.equity:,.0f}, "
                f"{sum(1 for p in self.positions.values() if p.side != 0)} open positions)[/cyan]"
            )
            return True
        except Exception as exc:
            console.log(f"[yellow]State load failed ({path}): {exc}[/yellow]")
            return False

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------

    def _ohlc(self, asset: str):
        return self.ohlc_history[asset].arrays()

    def _close(self, asset: str) -> np.ndarray:
        return self.ohlc_history[asset].close_array()

    def _new_class_perf(self) -> Dict[str, Dict]:
        return {
            cls: {"entries": 0, "exits": 0, "wins": 0, "losses": 0,
                  "total_r": 0.0, "total_pnl": 0.0,
                  "win_r_sum": 0.0, "loss_r_sum": 0.0}
            for cls in ["crypto", "equity", "future"]
        }

    # --------------------------------------------------
    # Risk engine
    # --------------------------------------------------

    def reset_daily(self, date_str: str):
        if self.daily_key != date_str:
            self.daily_key = date_str
            for a in ALL_ASSETS:
                self.daily_r[a] = 0.0

    def update_equity(self, pnl: float):
        self.equity      = max(0.0, self.equity + pnl)
        self.peak_equity = max(self.peak_equity, self.equity)
        dd = safe_div(self.peak_equity - self.equity, self.peak_equity)
        self.max_dd = max(self.max_dd, dd)
        self._equity_series.append(self.equity)
        if dd >= MAX_DRAWDOWN_PCT and not self.trading_halted:
            self.trading_halted = True
            msg = f"CIRCUIT BREAKER: {dd*100:.1f}% drawdown - all new entries halted"
            console.log(f"[bold red]{msg}[/bold red]")
            send_alert(f"🚨 {msg}")

    def _mark_to_market_equity(self) -> float:
        """Settled equity plus unrealised P&L on all open positions."""
        mtm = self.equity
        for asset, pos in self.positions.items():
            if pos.side == 0:
                continue
            px = self.latest_price.get(asset, np.nan)
            if np.isnan(px) or px <= 0:
                continue
            cls = ASSET_CLASS[asset]
            if cls == "future":
                spec = future_spec(asset)
                mtm += (px - pos.entry_price) * pos.side * pos.units * spec["point_value"]
            else:
                mtm += (px - pos.entry_price) * pos.side * pos.units
        return max(0.0, mtm)

    def _record_daily_mtm(self) -> None:
        """Append one MTM equity snapshot and update max_dd from open-position risk."""
        mtm    = self._mark_to_market_equity()
        dd_mtm = safe_div(self.peak_equity - mtm, self.peak_equity)
        self.max_dd = max(self.max_dd, dd_mtm)
        self._daily_equity.append(mtm)

    def current_risk_fraction(self) -> float:
        dd = safe_div(self.peak_equity - self.equity, self.peak_equity)
        if dd > 0.10:
            return MIN_RISK_FRACTION
        if dd < 0.02:
            return MAX_RISK_FRACTION * 0.75
        return BASE_RISK_FRACTION

    def vol_regime_scalar(self, asset: str) -> float:
        c = self._close(asset)
        if len(c) < 91:
            return 1.0
        rets      = np.diff(np.log(c[-91:]))
        vol_short = np.std(rets[-30:], ddof=1)
        vol_long  = np.std(rets,       ddof=1)
        if vol_long == 0:
            return 1.0
        ratio  = vol_short / vol_long
        scalar = 1.0 - 0.75 * min(1.0, max(0.0, ratio - 1.0))
        return round(max(0.25, scalar), 4)

    def count_open_positions(self, cls: Optional[str] = None) -> int:
        return sum(
            1 for a, pos in self.positions.items()
            if pos.side != 0 and (cls is None or ASSET_CLASS[a] == cls)
        )

    def class_risk_in_use(self, cls: str) -> float:
        return sum(
            self.positions[a].risk_usd
            for a in ALL_ASSETS
            if ASSET_CLASS[a] == cls and self.positions[a].side != 0
        )

    def class_risk_scalar(self, cls: str) -> float:
        cp    = self.class_perf[cls]
        exits = cp["exits"]
        if exits < CLASS_MIN_EXITS_FOR_SCALING:
            return 1.0
        avg_r = safe_div(cp["total_r"], exits)
        pf    = (safe_div(cp["win_r_sum"], cp["loss_r_sum"])
                 if cp["loss_r_sum"] > 0
                 else (float("inf") if cp["win_r_sum"] > 0 else 1.0))
        if pf < CLASS_WEAK_PF_THRESHOLD and avg_r < CLASS_WEAK_AVG_R_THRESHOLD:
            # v13.4: raised from 0.25 → CLASS_WEAK_RISK_SCALAR (0.50) to match
            # InstitutionalRepairModel's fix and prevent a sizing death-spiral in
            # any model that uses this base implementation.
            return CLASS_WEAK_RISK_SCALAR
        if pf < CLASS_WEAK_PF_THRESHOLD or avg_r < CLASS_WEAK_AVG_R_THRESHOLD:
            return CLASS_WEAK_RISK_SCALAR
        if pf > CLASS_STRONG_PF_THRESHOLD and avg_r > CLASS_STRONG_AVG_R_THRESHOLD:
            return CLASS_STRONG_RISK_SCALAR
        return 1.0

    def calculate_position_size(self, asset: str, atr_val: float,
                                  stop_mult: float,
                                  conviction_scalar: float = 1.0) -> Tuple[float, float]:
        cls = ASSET_CLASS[asset]

        # Combine all scalars and enforce a floor so they can't stack to zero
        combined_scalar = max(
            COMBINED_SCALAR_FLOOR,
            self.vol_regime_scalar(asset) *
            self.class_risk_scalar(cls) *
            max(0.50, conviction_scalar)
        )
        risk_frac    = self.current_risk_fraction() * combined_scalar
        risk_frac    = min(MAX_RISK_FRACTION, max(MIN_RISK_FRACTION * 0.50, risk_frac))
        desired_risk = self.equity * risk_frac
        class_remaining = max(
            0.0,
            self.equity * CLASS_RISK_BUDGET[cls] - self.class_risk_in_use(cls)
        )
        risk_usd      = min(desired_risk, class_remaining)
        stop_distance = atr_val * stop_mult

        if cls == "future":
            spec = future_spec(asset)
            pv   = spec["point_value"]
            per_contract_risk = stop_distance * pv
            per_contract_cost = self.future_round_trip_cost_usd(asset, 1.0)
            total_per_contract = per_contract_risk + per_contract_cost

            if total_per_contract > 0:
                contracts = int(np.floor(safe_div(risk_usd, total_per_contract)))
            else:
                contracts = 0

            # Fallback: if account is too small for even 1 contract at full risk,
            # allow 1 contract provided it doesn't exceed 3× the desired risk
            if contracts == 0 and risk_usd > 0:
                if per_contract_risk <= risk_usd * 3.0:
                    contracts = 1

            if contracts <= 0:
                return 0.0, 0.0

            sized_risk = contracts * per_contract_risk
            return sized_risk, float(contracts)

        # Equity / crypto: fractional units
        units = safe_div(risk_usd, stop_distance)
        return risk_usd, units

    def one_way_cost(self, asset: str) -> float:
        cls = ASSET_CLASS[asset]
        if cls == "crypto":
            return CRYPTO_ONE_WAY_COST
        if cls == "equity":
            return EQUITY_ONE_WAY_COST
        return 0.0

    def future_round_trip_cost_usd(self, asset: str, contracts: float) -> float:
        spec = future_spec(asset)
        per_contract = (
            2 * spec["one_way_fees"] +
            2 * spec["one_way_slippage_ticks"] * spec["tick_value"]
        )
        return max(0.0, contracts) * per_contract

    def futures_stop_fill_price(self, asset: str, side: int, stop_price: float,
                                bar_open: float, bar_high: float,
                                bar_low: float) -> Optional[float]:
        if side == 1  and bar_low  <= stop_price:
            return min(bar_open, stop_price)
        if side == -1 and bar_high >= stop_price:
            return max(bar_open, stop_price)
        return None

    def vol_breakout_ok(self, asset: str, vol_window: int = 20,
                        multiplier: float = 1.05) -> bool:
        """Return True if the latest bar's volume is above the recent average.
        Falls back to True when volume data is unavailable (all-zero)."""
        vol = self.ohlc_history[asset].volume_array()
        if len(vol) < vol_window + 1 or np.all(vol == 0):
            return True
        recent_avg = np.mean(vol[-(vol_window + 1):-1])
        if recent_avg == 0:
            return True
        return float(vol[-1]) >= recent_avg * multiplier

    # --------------------------------------------------
    # Indicators
    # --------------------------------------------------

    def refresh_asset_snapshot(self, asset: str):
        o, h, l, c = self._ohlc(asset)
        if len(c) < 30:
            return
        cls = ASSET_CLASS[asset]
        w   = (CRYPTO_ATR_WINDOW if cls == "crypto" else
               EQUITY_ATR_WINDOW if cls == "equity" else
               FUTURE_ATR_WINDOW)
        rw  = CRYPTO_RSI_WINDOW if cls == "crypto" else 14
        self.curr_atr[asset] = true_atr(h, l, c, w)[-1]
        self.curr_rsi[asset] = wilder_rsi(c, rw)[-1]

    def get_btc_trend(self) -> str:
        c = self._close("BTC-USD")
        if len(c) < BTC_SLOW_EMA + 5:
            return "UNKNOWN"
        fast_v = ema(c, BTC_FAST_EMA)[-1]
        slow_v = ema(c, BTC_SLOW_EMA)[-1]
        px     = c[-1]
        if np.isnan(fast_v) or np.isnan(slow_v):
            return "UNKNOWN"
        if px > fast_v and fast_v > slow_v:
            return "UP"
        if px < fast_v and fast_v < slow_v:
            return "DOWN"
        # EMA stack is neutral — use RSI to resolve borderline states faster.
        # The 50/200 stack takes 2-3 weeks to flip; RSI responds within days.
        if len(c) >= BTC_TREND_RSI_WINDOW + 2:
            rsi_v = wilder_rsi(c, BTC_TREND_RSI_WINDOW)[-1]
            if not np.isnan(rsi_v):
                if rsi_v >= BTC_TREND_RSI_UP:
                    return "UP"
                if rsi_v <= BTC_TREND_RSI_DOWN:
                    return "DOWN"
        return "NEUTRAL"

    def crypto_relative_strength_ok(self, asset: str) -> bool:
        if asset == "BTC-USD":
            return True
        asset_c = self._close(asset)
        btc_c   = self._close("BTC-USD")
        min_len = min(len(asset_c), len(btc_c))
        need = max(CRYPTO_ALT_RS_SLOW, CRYPTO_ALT_RS_ROC_LOOKBACK + 1) + 5
        if min_len < need:
            return False
        ratio = asset_c[-min_len:] / btc_c[-min_len:]
        fast_v = ema(ratio, CRYPTO_ALT_RS_FAST)[-1]
        slow_v = ema(ratio, CRYPTO_ALT_RS_SLOW)[-1]
        roc20 = safe_div(ratio[-1], ratio[-1 - CRYPTO_ALT_RS_ROC_LOOKBACK], default=np.nan) - 1.0
        if any(np.isnan([fast_v, slow_v, roc20])):
            return False
        return fast_v > slow_v and roc20 > 0

    def min_conviction_threshold(self, asset: str) -> float:
        cls = ASSET_CLASS[asset]
        if cls == "crypto":
            return CRYPTO_MIN_CONVICTION_TO_ENTER
        if cls == "equity":
            return EQUITY_MIN_CONVICTION_TO_ENTER
        return FUTURE_MIN_CONVICTION_TO_ENTER

    def equity_market_filter_ok(self) -> bool:
        for benchmark in ["SPY", "QQQ"]:
            c = self._close(benchmark)
            if len(c) < EQUITY_LONG_TREND_SMA + 10:
                return False
            sma50_v  = sma(c, EQUITY_EXIT_SMA)[-1]
            sma100_v = sma(c, EQUITY_LONG_TREND_SMA)[-1]
            if np.isnan(sma50_v) or np.isnan(sma100_v):
                return False
            if not (c[-1] > sma100_v and sma50_v > sma100_v):
                return False
        return True

    def equity_correlation_allows_entry(self, asset: str) -> bool:
        base = self._close(asset)
        if len(base) < EQUITY_CORR_LOOKBACK + 2:
            return True
        base_rets = np.diff(np.log(base[-(EQUITY_CORR_LOOKBACK + 1):]))
        corrs = []
        for other in EQUITY_ASSETS:
            if other == asset or self.positions[other].side == 0:
                continue
            other_c = self._close(other)
            if len(other_c) < EQUITY_CORR_LOOKBACK + 2:
                continue
            other_rets = np.diff(np.log(other_c[-(EQUITY_CORR_LOOKBACK + 1):]))
            if len(other_rets) != len(base_rets):
                continue
            corr = np.corrcoef(base_rets, other_rets)[0, 1]
            if not np.isnan(corr):
                corrs.append(abs(corr))
        if not corrs:
            return True
        return not (
            np.mean(corrs) > EQUITY_MAX_AVG_CORR_TO_OPEN or
            np.max(corrs) > EQUITY_MAX_SINGLE_CORR_TO_OPEN
        )

    def future_breakout_lookback(self, asset: str) -> int:
        return FUTURE_BREAKOUT_LOOKBACK_BY_ASSET.get(asset, FUTURE_BREAKOUT_LOOKBACK)

    def futures_correlation_allows_entry(self, asset: str) -> bool:
        """Block futures entry when the candidate is highly correlated (> 0.85)
        with an already-open futures position.  Prevents doubling up on the
        same macro driver (e.g. GC=F + SI=F, or ZC=F + ZS=F) even when both
        assets independently pass their own entry filters."""
        for other in FUTURES_ASSETS:
            if other == asset or self.positions[other].side == 0:
                continue
            if self.pairwise_abs_corr(asset, other) > 0.85:
                return False
        return True

    def future_stop_mult(self, asset: str, sig: dict) -> float:
        base = FUTURE_STOP_ATR_BY_ASSET.get(asset, FUTURE_STOP_ATR)
        vol_ratio = sig.get("vol_ratio", np.nan)
        eff = sig.get("efficiency", np.nan)
        if not np.isnan(vol_ratio) and vol_ratio > 1.15:
            base += 0.15
        if not np.isnan(eff) and eff > 0.45:
            base -= 0.10
        return min(3.3, max(1.8, base))  # v13.4: floor lowered 2.2→1.8 so per-asset configs of 2.0 (GC/ZC/ZS) are respected

    def detect_crypto_trend(self, asset: str) -> dict:
        o, h, l, c = self._ohlc(asset)
        result = {
            "is_uptrend": False, "is_strong_uptrend": False,
            "ema_bullish": False, "price_above_trend": False,
            "rsi_bullish": False, "rsi_strong": False,
            "breakout_strength": 0.0, "trend_strength": 0.0,
            "atr_val": np.nan, "atr_pct": np.nan,
            "extension_atr": 0.0, "fast_ema": np.nan,
            "efficiency": np.nan, "pullback_ready": False,
        }
        if len(c) < CRYPTO_TREND_EMA + 10:
            return result

        fast    = ema(c, CRYPTO_FAST_EMA)
        slow    = ema(c, CRYPTO_SLOW_EMA)
        trend   = ema(c, CRYPTO_TREND_EMA)
        atr_arr = true_atr(h, l, c, CRYPTO_ATR_WINDOW)
        rsi_arr = wilder_rsi(c, CRYPTO_RSI_WINDOW)

        px = c[-1]; fast_v = fast[-1]; slow_v = slow[-1]
        trend_v = trend[-1]; atr_v = atr_arr[-1]; rsi_v = rsi_arr[-1]

        if any(np.isnan([px, fast_v, slow_v, trend_v, atr_v])):
            return result

        extension_atr = safe_div(px - fast_v, atr_v)
        below_fast_atr = safe_div(fast_v - px, atr_v)

        result["atr_val"]           = atr_v
        result["atr_pct"]           = safe_div(atr_v, px)
        result["extension_atr"]     = extension_atr
        result["fast_ema"]          = fast_v
        result["ema_bullish"]       = fast_v > slow_v
        result["price_above_trend"] = px > trend_v
        result["rsi_bullish"]       = not np.isnan(rsi_v) and rsi_v > CRYPTO_RSI_BULL_THRESHOLD
        result["rsi_strong"]        = not np.isnan(rsi_v) and rsi_v > CRYPTO_RSI_STRONG_THRESHOLD
        result["breakout_strength"] = safe_div(px - slow_v, atr_v)
        result["trend_strength"]    = safe_div(fast_v - slow_v, atr_v)
        result["efficiency"]        = efficiency_ratio(c, CRYPTO_ER_WINDOW)

        result["is_uptrend"] = (
            result["ema_bullish"] and result["price_above_trend"] and
            result["rsi_bullish"] and
            result["breakout_strength"] >= CRYPTO_MIN_BREAKOUT_ATR
        )
        result["is_strong_uptrend"] = (
            result["is_uptrend"] and result["rsi_strong"] and
            result["breakout_strength"] >= CRYPTO_MIN_BREAKOUT_ATR * 1.5
        )
        result["pullback_ready"] = (
            result["ema_bullish"] and result["price_above_trend"] and
            result["rsi_bullish"] and result["trend_strength"] > 0 and
            abs(extension_atr) <= CRYPTO_PULLBACK_MAX_ABS_ATR and
            below_fast_atr <= CRYPTO_PULLBACK_MAX_BELOW_EMA
        )
        return result

    def crypto_stop_mult(self, trend_strength: float) -> float:
        base = CRYPTO_BASE_STOP_ATR
        if trend_strength > 1.0:
            return min(base + 0.5, CRYPTO_MAX_STOP_ATR)
        if trend_strength < 0.3:
            return max(base - 0.5, CRYPTO_MIN_STOP_ATR)
        return base

    def get_equity_rankings(self) -> List[Tuple[str, float]]:
        scores = []
        for asset in EQUITY_ASSETS:
            o, h, l, c = self._ohlc(asset)
            if len(c) < max(EQUITY_MOM_LOOKBACK + 1, EQUITY_LONG_TREND_SMA):
                continue
            mom21    = safe_div(c[-1], c[-1 - EQUITY_MOM_SHORT], default=np.nan) - 1.0
            mom63    = safe_div(c[-1], c[-1 - EQUITY_MOM_MEDIUM], default=np.nan) - 1.0
            mom126   = safe_div(c[-1], c[-1 - EQUITY_MOM_LOOKBACK], default=np.nan) - 1.0
            sma100_v = sma(c, EQUITY_LONG_TREND_SMA)[-1]
            atr_v    = true_atr(h, l, c, EQUITY_ATR_WINDOW)[-1]
            if any(np.isnan([mom21, mom63, mom126, sma100_v, atr_v])) or atr_v == 0:
                continue
            if c[-1] <= sma100_v or mom126 <= 0:
                continue
            atr_pct = safe_div(atr_v, c[-1])
            if not (EQUITY_MIN_ATR_PCT <= atr_pct <= EQUITY_MAX_ATR_PCT):
                continue
            extension_atr = safe_div(c[-1] - sma100_v, atr_v)
            extension_penalty = max(0.0, extension_atr - 1.0) * 0.20
            score = 0.20 * mom21 + 0.30 * mom63 + 0.50 * mom126 - extension_penalty
            scores.append((asset, float(score)))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def get_top_equity_set(self) -> set:
        return {a for a, _ in self.get_equity_rankings()[:EQUITY_TOP_N]}

    def detect_future_signal(self, asset: str) -> dict:
        o, h, l, c = self._ohlc(asset)
        result = {"signal": 0, "atr_val": np.nan, "sma_v": np.nan,
                  "vol_ratio": np.nan, "slope50": 0.0,
                  "efficiency": np.nan, "clv": 0.5}
        lookback = self.future_breakout_lookback(asset)
        min_bars = max(FUTURE_TREND_SMA, lookback) + 10
        if len(c) < min_bars:
            return result

        sma100_arr = sma(c, FUTURE_TREND_SMA)
        sma50_arr  = sma(c, FUTURE_FAST_SMA)
        atr_arr    = true_atr(h, l, c, FUTURE_ATR_WINDOW)
        atr5_arr   = true_atr(h, l, c, 5)

        # v13.4: use bar highs for LONG reference, bar lows for SHORT reference.
        # Prior code used rolling_high/low of CLOSES, which is ~1-3% lower than
        # bar highs/lows in volatile commodities.  That produced false breakouts
        # (price cleared the close-based reference but not true prior resistance)
        # and drove the 35.9% futures win rate.
        prev_h  = h[:-1]
        prev_l  = l[:-1]
        hh_arr  = rolling_high(prev_h, lookback)  # highest prior bar HIGH
        ll_arr  = rolling_low(prev_l,  lookback)  # lowest  prior bar LOW

        px       = c[-1]
        sma100_v = sma100_arr[-1]
        sma50_v  = sma50_arr[-1]
        atr_v    = atr_arr[-1]
        atr5_v   = atr5_arr[-1]
        prev_hh  = hh_arr[-1]
        prev_ll  = ll_arr[-1]

        result["atr_val"] = atr_v
        result["sma_v"]   = sma100_v

        if any(np.isnan([sma100_v, sma50_v, atr_v, atr5_v, prev_hh, prev_ll])):
            return result

        vol_ratio            = safe_div(atr5_v, atr_v)
        result["vol_ratio"] = vol_ratio
        if vol_ratio > FUTURE_VOL_RATIO_MAX:
            return result

        slope50              = sma_slope(c, FUTURE_FAST_SMA, lookback=5)
        result["slope50"]   = slope50
        result["efficiency"] = efficiency_ratio(c, FUTURE_ER_WINDOW)
        result["clv"]       = close_location_value(h[-1], l[-1], px)

        if np.isnan(result["efficiency"]) or result["efficiency"] < FUTURE_MIN_ER_BY_ASSET.get(asset, FUTURE_MIN_ER):
            return result

        buffer = FUTURE_BREAKOUT_BUFFER_ATR * atr_v
        long_ok  = (
            px > sma100_v and px >= prev_hh + buffer and slope50 > 0 and
            result["clv"] >= FUTURE_MIN_CLV
        )
        short_ok = (
            px < sma100_v and px <= prev_ll - buffer and slope50 < 0 and
            result["clv"] <= (1.0 - FUTURE_MIN_CLV)
        )

        if long_ok:
            result["signal"] = 1
        elif short_ok:
            result["signal"] = -1

        return result

    # --------------------------------------------------
    # Entry / exit
    # --------------------------------------------------

    def enter_position(self, asset: str, side: int, px: float, ts: str,
                       atr_val: float, stop_mult: float,
                       conviction_scalar: float = 1.0):
        if self.trading_halted:
            return
        if self.count_open_positions() >= MAX_TOTAL_POSITIONS:
            return
        cls = ASSET_CLASS[asset]
        if self.count_open_positions(cls) >= MAX_CLASS_POSITIONS[cls]:
            return
        pos = self.positions[asset]
        if pos.side != 0 or pos.cooldown > 0:
            return
        if conviction_scalar < self.min_conviction_threshold(asset):
            return

        risk_usd, units = self.calculate_position_size(
            asset, atr_val, stop_mult, conviction_scalar=conviction_scalar
        )
        if risk_usd <= 0 or units <= 0:
            return

        pos.side               = side
        pos.entry_price        = px
        pos.entry_atr          = atr_val
        pos.stop_price         = px - side * (atr_val * stop_mult)
        pos.initial_stop_dist  = atr_val * stop_mult
        pos.units              = units
        pos.risk_usd           = risk_usd
        pos.entry_ts           = ts
        pos.bars_held          = 0
        pos.highest_price      = px
        pos.lowest_price       = px
        pos.trail_active       = False
        pos.peak_r             = 0.0
        pos.flip_confirm_count = 0
        pos.chop_regime_count  = 0
        pos.rank_exit_count    = 0

        self.performance["entries"]     += 1
        self.class_perf[cls]["entries"] += 1
        label = "LONG" if side == 1 else "SHORT"
        console.log(
            f"[green][ENTRY][/green] {asset} {label} @ {px:.2f} | "
            f"stop={pos.stop_price:.2f} | risk=${risk_usd:.0f}"
        )

    def exit_position(self, asset: str, px: float, ts: str, reason: str):
        pos = self.positions[asset]
        if pos.side == 0:
            return

        cls       = ASSET_CLASS[asset]
        # Always normalise R against the *initial* stop distance so that a
        # post-partial-profit breakeven-lock (which sets stop_price ≈ entry +
        # 10% of original stop) does not inflate R by 10×.
        stop_dist = pos.initial_stop_dist if pos.initial_stop_dist > 0 else abs(pos.entry_price - pos.stop_price)
        if stop_dist == 0:
            stop_dist = max(pos.entry_atr, 1e-9)

        if cls == "future":
            # --- Futures: dollar P&L via point_value, R relative to risk_usd ---
            spec      = future_spec(asset)
            gross_pnl = ((px - pos.entry_price) * pos.side
                         * pos.units * spec["point_value"])
            cost_usd  = self.future_round_trip_cost_usd(asset, pos.units)
            pnl       = gross_pnl - cost_usd
            # R is PnL expressed as a multiple of the original risk capital
            r_gross   = safe_div(gross_pnl, pos.risk_usd)
            r_net     = safe_div(pnl,       pos.risk_usd)
        else:
            # --- Equity / crypto: percentage-based ---
            r_gross = safe_div((px - pos.entry_price) * pos.side, stop_dist)
            cost_r  = safe_div(2 * self.one_way_cost(asset) * px, stop_dist)
            r_net   = r_gross - cost_r
            pnl     = r_net * pos.risk_usd

        self.daily_r[asset]               += r_net
        self.performance["exits"]         += 1
        self.performance["total_r"]       += r_net
        self.performance["total_pnl"]     += pnl
        self.class_perf[cls]["exits"]     += 1
        self.class_perf[cls]["total_r"]   += r_net
        self.class_perf[cls]["total_pnl"] += pnl
        self._all_trades_r.append(r_net)

        if r_net > 0:
            self.performance["wins"]              += 1
            self.performance["win_r_sum"]         += r_net
            self.performance["max_win_r"]          = max(self.performance["max_win_r"], r_net)
            self.class_perf[cls]["wins"]          += 1
            self.class_perf[cls]["win_r_sum"]     += r_net
        else:
            self.performance["losses"]            += 1
            self.performance["loss_r_sum"]        += abs(r_net)
            self.performance["max_loss_r"]         = max(self.performance["max_loss_r"], abs(r_net))
            self.class_perf[cls]["losses"]        += 1
            self.class_perf[cls]["loss_r_sum"]    += abs(r_net)

        if cls == "future":
            self._futures_trades_r.append(r_net)

        self.update_equity(pnl)
        self.trades.write([
            pos.entry_ts, ts, asset, cls, "LONG" if pos.side == 1 else "SHORT",
            pos.entry_price, px, pos.units, pos.entry_atr,
            pos.bars_held, r_gross, r_net, pnl, pos.risk_usd, reason
        ])

        cooldown = (CRYPTO_COOLDOWN_BARS if cls == "crypto" else
                    EQUITY_COOLDOWN_BARS if cls == "equity" else
                    FUTURE_COOLDOWN_BARS)
        self.positions[asset] = Position(cooldown=cooldown)
        color = "green" if r_net > 0 else "red"
        console.log(
            f"[{color}][EXIT {reason}][/{color}] {asset} @ {px:.2f} | "
            f"R={r_net:+.2f} | PnL=${pnl:+.0f} | Equity=${self.equity:,.0f}"
        )

    # --------------------------------------------------
    # Strategy helpers
    # --------------------------------------------------

    def breakeven_stop(self, side: int, entry_price: float, entry_dist: float) -> float:
        lock = 0.10 * entry_dist
        return entry_price + lock if side == 1 else entry_price - lock

    def crypto_conviction_scalar(self, asset: str, trend: dict) -> float:
        score = 1.0
        if self.btc_trend == "UP":
            score += 0.10
        if trend["is_strong_uptrend"]:
            score += 0.10
        if trend.get("pullback_ready", False):
            score += 0.05
        if trend["breakout_strength"] >= CRYPTO_MIN_BREAKOUT_ATR * 2.0:
            score += 0.05
        if 0.02 <= trend["atr_pct"] <= 0.08:
            score += 0.05
        if not np.isnan(trend.get("efficiency", np.nan)) and trend["efficiency"] >= CRYPTO_MIN_ER + 0.10:
            score += 0.05
        if asset != "BTC-USD" and self.crypto_relative_strength_ok(asset):
            score += 0.10
        if trend["extension_atr"] > 1.75:
            score -= 0.15
        return min(1.30, max(0.70, score))

    def equity_conviction_scalar(self, asset: str, top_assets: List[str],
                                 distance_above_sma: float, atr_val: float,
                                 slope50: float) -> float:
        score = 1.0
        if top_assets and asset == top_assets[0]:
            score += 0.10
        elif len(top_assets) > 1 and asset == top_assets[1]:
            score += 0.05
        if atr_val > 0 and distance_above_sma <= 0.5 * atr_val:
            score += 0.05
        if atr_val > 0 and distance_above_sma <= 1.0 * atr_val:
            score += 0.05
        if slope50 > 0:
            score += 0.05
        return min(1.20, max(0.75, score))

    def future_conviction_scalar(self, signal: int, sig: dict, px: float) -> float:
        score = 1.0
        if signal == 0 or np.isnan(sig.get("atr_val", np.nan)) or sig["atr_val"] == 0:
            return score
        dist_from_sma = safe_div(abs(px - sig["sma_v"]), sig["atr_val"])
        slope_contrib = min(0.10, abs(sig.get("slope50", 0.0)) * 10.0)
        score += slope_contrib
        if not np.isnan(sig.get("vol_ratio", np.nan)) and sig["vol_ratio"] < 1.0:
            score += 0.05
        if not np.isnan(sig.get("efficiency", np.nan)) and sig["efficiency"] >= FUTURE_MIN_ER + 0.10:
            score += 0.05
        if signal == 1 and sig.get("clv", 0.5) >= 0.80:
            score += 0.05
        if signal == -1 and sig.get("clv", 0.5) <= 0.20:
            score += 0.05
        if dist_from_sma > 2.5:
            score -= 0.10
        # ADX bonus: higher conviction in confirmed trending markets
        adx = sig.get("adx_val", 0.0)
        if adx >= 25.0:
            score += min(0.06, (adx - 20.0) / 80.0)
        # Jump penalty: spike-driven markets are unreliable for trend-following
        j_prob = sig.get("jump_prob", 0.0)
        if j_prob > 0.30:
            score -= 0.05 * min(1.0, (j_prob - 0.30) / 0.20)
        return min(1.20, max(0.75, score))

    # --------------------------------------------------
    # Strategy handlers
    # --------------------------------------------------

    def handle_crypto(self, asset: str, ts: str):
        o, h, l, c = self._ohlc(asset)
        if len(c) < CRYPTO_TREND_EMA + 10:
            return

        px    = c[-1]
        pos   = self.positions[asset]
        trend = self.detect_crypto_trend(asset)
        self.curr_signal[asset] = ("PB" if trend.get("pullback_ready", False) else
                                   "UP" if trend["is_uptrend"] else "-")

        if np.isnan(trend["atr_val"]) or trend["atr_val"] == 0:
            return

        if pos.cooldown > 0:
            pos.cooldown -= 1

        if pos.side != 0:
            pos.bars_held     += 1
            pos.highest_price  = max(pos.highest_price, px)

            entry_dist = abs(pos.entry_price - pos.stop_price)
            r_gross    = safe_div((px - pos.entry_price) * pos.side, entry_dist)
            cost_r     = safe_div(2 * self.one_way_cost(asset) * px, entry_dist)
            r_net      = r_gross - cost_r
            pos.peak_r = max(pos.peak_r, r_net)

            if r_net >= CRYPTO_TRAIL_ACTIVATE_R:
                pos.trail_active = True

            current_stop = pos.stop_price
            if pos.peak_r >= CRYPTO_BREAKEVEN_R:
                current_stop = max(current_stop,
                                   self.breakeven_stop(pos.side, pos.entry_price, entry_dist))
            if pos.trail_active:
                trail_mult   = (CRYPTO_TRAIL_TIGHT_ATR if r_net >= CRYPTO_TRAIL_TIGHTEN_R
                                else CRYPTO_TRAIL_ATR)
                current_stop = max(current_stop,
                                   pos.highest_price - trend["atr_val"] * trail_mult)

            exit_reason = None
            if px <= current_stop:
                exit_reason = ("TRAIL_STOP"
                               if pos.trail_active or pos.peak_r >= CRYPTO_BREAKEVEN_R
                               else "STOP_LOSS")
            elif r_net <= -CRYPTO_EMERGENCY_STOP_R:
                exit_reason = "EMERGENCY"
            elif pos.bars_held >= CRYPTO_TIME_STOP_BARS and pos.peak_r < CRYPTO_MIN_R_BY_TIME:
                exit_reason = "TIME_STOP"
            elif (not trend["ema_bullish"] and not trend["price_above_trend"]
                  and pos.bars_held > 5):
                exit_reason = "TREND_REVERSAL"

            if exit_reason:
                self.exit_position(asset, px, ts, exit_reason)
                return

        if self.positions[asset].side == 0:
            if REQUIRE_BTC_FILTER and self.btc_trend not in ["UP", "NEUTRAL"]:
                return
            if asset != "BTC-USD":
                if CRYPTO_ALT_REQUIRE_BTC_UP and self.btc_trend != "UP":
                    return
                if not self.crypto_relative_strength_ok(asset):
                    return
            atr_pct = trend["atr_pct"]
            entry_ok = trend["is_uptrend"] or trend.get("pullback_ready", False)
            if (entry_ok
                    and CRYPTO_MIN_ATR_PCT <= atr_pct <= CRYPTO_MAX_ATR_PCT
                    and trend["extension_atr"] <= CRYPTO_MAX_EXTENSION_ATR
                    and not np.isnan(trend.get("efficiency", np.nan))
                    and trend["efficiency"] >= CRYPTO_MIN_ER):
                stop_mult  = self.crypto_stop_mult(trend["trend_strength"])
                conviction = self.crypto_conviction_scalar(asset, trend)
                self.enter_position(asset, 1, px, ts, trend["atr_val"],
                                    stop_mult, conviction_scalar=conviction)

    def handle_equities(self, ts: str, equity_assets_in_bar: set):
        top_assets = [a for a, _ in self.get_equity_rankings()[:EQUITY_TOP_N]]
        top_set    = set(top_assets)

        for asset in EQUITY_ASSETS:
            if asset not in equity_assets_in_bar:
                if self.positions[asset].cooldown > 0:
                    self.positions[asset].cooldown -= 1
                continue

            o, h, l, c = self._ohlc(asset)
            if len(c) < max(EQUITY_MOM_LOOKBACK + 1, EQUITY_LONG_TREND_SMA):
                continue

            px        = c[-1]
            pos       = self.positions[asset]
            atr_arr   = true_atr(h, l, c, EQUITY_ATR_WINDOW)
            sma50_v   = sma(c, EQUITY_EXIT_SMA)[-1]
            sma100_v  = sma(c, EQUITY_LONG_TREND_SMA)[-1]
            atr_val   = atr_arr[-1]
            slope50   = sma_slope(c, EQUITY_EXIT_SMA, lookback=5)
            self.curr_signal[asset] = "TOP" if asset in top_set else "-"

            if np.isnan(atr_val) or np.isnan(sma50_v) or atr_val == 0:
                continue

            if pos.cooldown > 0:
                pos.cooldown -= 1

            if pos.side != 0:
                pos.bars_held     += 1
                pos.highest_price  = max(pos.highest_price, px)

                entry_dist = abs(pos.entry_price - pos.stop_price)
                r_gross    = safe_div((px - pos.entry_price) * pos.side, entry_dist)
                cost_r     = safe_div(2 * self.one_way_cost(asset) * px, entry_dist)
                r_net      = r_gross - cost_r
                pos.peak_r = max(pos.peak_r, r_net)

                current_stop = pos.stop_price
                if pos.peak_r >= EQUITY_BREAKEVEN_R:
                    current_stop = max(current_stop,
                                       self.breakeven_stop(pos.side, pos.entry_price, entry_dist))
                if r_net >= EQUITY_TRAIL_ACTIVATE_R:
                    pos.trail_active = True
                if pos.trail_active:
                    trail_mult = (EQUITY_TRAIL_TIGHT_ATR if pos.peak_r >= EQUITY_TRAIL_TIGHTEN_R
                                  else EQUITY_TRAIL_ATR)
                    current_stop = max(current_stop,
                                       pos.highest_price - atr_val * trail_mult)

                # Rank-exit: must be outside top-N for EQUITY_RANK_EXIT_BARS bars
                if asset not in top_set:
                    pos.rank_exit_count += 1
                else:
                    pos.rank_exit_count = 0

                exit_reason = None
                if px <= current_stop:
                    exit_reason = ("TRAIL_STOP"
                                   if pos.trail_active or pos.peak_r >= EQUITY_BREAKEVEN_R
                                   else "STOP_LOSS")
                elif not np.isnan(sma100_v) and px < sma100_v:
                    exit_reason = "SMA100_EXIT"          # hard floor: below SMA100
                elif px < sma50_v and not pos.trail_active:
                    exit_reason = "SMA50_EXIT"  # suppressed once trail is active: trail protects better
                elif pos.bars_held >= EQUITY_TIME_STOP_BARS and pos.peak_r < EQUITY_MIN_R_BY_TIME:
                    exit_reason = "TIME_STOP"
                elif pos.rank_exit_count >= EQUITY_RANK_EXIT_BARS:
                    exit_reason = "RANK_EXIT"

                if exit_reason:
                    self.exit_position(asset, px, ts, exit_reason)
                    continue

            if self.positions[asset].side == 0 and asset in top_set:
                if not self.equity_market_filter_ok():
                    continue
                if not self.equity_correlation_allows_entry(asset):
                    continue
                if not np.isnan(sma100_v) and atr_val > 0:
                    distance_above_sma = px - sma100_v
                    trend_ok = (sma50_v > sma100_v) and (slope50 > 0)
                    if 0 <= distance_above_sma <= EQUITY_PULLBACK_ATR * atr_val and trend_ok:
                        conviction = self.equity_conviction_scalar(
                            asset, top_assets, distance_above_sma, atr_val, slope50
                        )
                        self.enter_position(asset, 1, px, ts, atr_val, EQUITY_STOP_ATR,
                                            conviction_scalar=conviction)

    def handle_futures(self, asset: str, ts: str):
        o, h, l, c = self._ohlc(asset)
        if len(c) < max(FUTURE_TREND_SMA, FUTURE_BREAKOUT_LOOKBACK) + 10:
            return

        bar_open = o[-1]; bar_high = h[-1]; bar_low = l[-1]; px = c[-1]
        pos      = self.positions[asset]
        sig      = self.detect_future_signal(asset)
        atr_val  = sig["atr_val"]
        signal   = sig["signal"]
        self.curr_signal[asset] = ("LONG" if signal == 1 else
                                   "SHORT" if signal == -1 else "-")

        if np.isnan(atr_val) or atr_val == 0:
            return

        if pos.cooldown > 0:
            pos.cooldown -= 1

        if pos.side != 0:
            pos.bars_held += 1

            # R tracking uses stop distance for intra-trade monitoring
            entry_dist = abs(pos.entry_price - pos.stop_price)
            if entry_dist == 0:
                entry_dist = max(pos.entry_atr, 1e-9)

            spec    = future_spec(asset)
            pv      = spec["point_value"]
            # Unrealised R: (price move × point_value × contracts) / risk_usd
            unreal_gross = (px - pos.entry_price) * pos.side * pos.units * pv
            r_gross      = safe_div(unreal_gross, pos.risk_usd)
            cost_r       = safe_div(
                self.future_round_trip_cost_usd(asset, pos.units), pos.risk_usd
            )
            r_net        = r_gross - cost_r
            pos.peak_r   = max(pos.peak_r, r_net)

            current_stop = pos.stop_price
            if pos.peak_r >= FUTURE_BREAKEVEN_R:
                be = self.breakeven_stop(pos.side, pos.entry_price, entry_dist)
                if pos.side == 1:
                    current_stop = max(current_stop, be)
                else:
                    current_stop = min(current_stop, be)
            if pos.trail_active:
                trail_mult = (FUTURE_TRAIL_TIGHT_ATR
                              if pos.peak_r >= FUTURE_TRAIL_TIGHTEN_R
                              else FUTURE_TRAIL_ATR)
                if pos.side == 1:
                    current_stop = max(current_stop,
                                       pos.highest_price - atr_val * trail_mult)
                else:
                    current_stop = min(current_stop,
                                       pos.lowest_price + atr_val * trail_mult)

            stop_fill = self.futures_stop_fill_price(
                asset, pos.side, current_stop, bar_open, bar_high, bar_low
            )
            if stop_fill is not None:
                self.exit_position(
                    asset, stop_fill, ts,
                    "TRAIL_STOP" if pos.trail_active else "STOP_LOSS"
                )
                return

            # Update high/low after stop check so fill uses bar's extremes
            pos.highest_price = max(pos.highest_price, bar_high)
            pos.lowest_price  = min(pos.lowest_price,  bar_low)

            if r_net >= FUTURE_TRAIL_ACTIVATE_R:
                pos.trail_active = True

            exit_reason = None
            if pos.bars_held >= FUTURE_TIME_STOP_BARS and pos.peak_r < FUTURE_MIN_R_BY_TIME:
                exit_reason = "TIME_STOP"
            elif signal == -pos.side:
                pos.flip_confirm_count += 1
                if pos.flip_confirm_count >= FUTURE_FLIP_CONFIRM_BARS:
                    exit_reason = "SIGNAL_FLIP"
            else:
                pos.flip_confirm_count = 0

            if exit_reason:
                self.exit_position(asset, px, ts, exit_reason)
                return

        if self.positions[asset].side == 0 and pos.cooldown == 0:
            if signal != 0:
                pos.flip_confirm_count += 1
                if pos.flip_confirm_count >= FUTURE_BREAKOUT_CONFIRM_BARS:
                    conviction = self.future_conviction_scalar(signal, sig, px)
                    stop_mult  = self.future_stop_mult(asset, sig)
                    self.enter_position(asset, signal, px, ts, atr_val, stop_mult,
                                        conviction_scalar=conviction)
                    self.positions[asset].flip_confirm_count = 0
            else:
                pos.flip_confirm_count = 0

    # --------------------------------------------------
    # Bar processing
    # --------------------------------------------------

    def process_bar(self, ts: pd.Timestamp, bar_map: Dict[str, dict]):
        date_str = ts.strftime("%Y-%m-%d")
        ts_str   = ts.strftime("%Y-%m-%d %H:%M:%S")
        self._current_ts = ts   # exposed for MacroEventGate inside collect_candidate
        self.reset_daily(date_str)

        for asset, bar in bar_map.items():
            if isinstance(bar, dict):
                ob = OHLCBar(bar["open"], bar["high"], bar["low"], bar["close"],
                             bar.get("volume", 0.0))
            else:
                v  = float(bar)
                ob = OHLCBar(v, v, v, v)
            self.ohlc_history[asset].append(ob)
            self.latest_price[asset] = ob.close
            self.refresh_asset_snapshot(asset)

        self.btc_trend = self.get_btc_trend()

        if self.trading_halted:
            for asset, pos in self.positions.items():
                if pos.cooldown > 0:
                    pos.cooldown -= 1
                if pos.side != 0 and not np.isnan(self.latest_price[asset]):
                    self.exit_position(asset, self.latest_price[asset], ts_str, "HALT")
            return

        for asset in CRYPTO_ASSETS:
            if asset in bar_map:
                self.handle_crypto(asset, ts_str)

        equity_in_bar = {a for a in EQUITY_ASSETS if a in bar_map}
        self.handle_equities(ts_str, equity_in_bar)

        for asset in FUTURES_ASSETS:
            if asset in bar_map:
                self.handle_futures(asset, ts_str)

        for asset in bar_map:
            pos = self.positions[asset]
            self.telemetry.write([
                ts_str, asset, ASSET_CLASS[asset], self.latest_price[asset],
                self.curr_atr[asset], self.curr_rsi[asset], self.curr_signal[asset],
                pos.side, pos.bars_held, pos.peak_r, pos.trail_active,
                self.daily_r[asset], self.equity,
                safe_div(self.peak_equity - self.equity, self.peak_equity),
                self.btc_trend
            ])

        # Daily MTM snapshot: updates max_dd from open-position risk and feeds
        # the _daily_equity series used for accurate Sharpe calculation.
        self._record_daily_mtm()

    # --------------------------------------------------
    # Dashboard
    # --------------------------------------------------

    def update_dashboard(self) -> Panel:
        status = "[red]HALTED[/red]" if self.trading_halted else "[green]LIVE[/green]"
        dd_pct = self.max_dd * 100
        title  = (
            f"Multi-Asset Model v14.2 | {status} | BTC: {self.btc_trend} | "
            f"Equity: ${self.equity:,.0f} | DD: {dd_pct:.1f}%"
        )
        table = Table(title=title, expand=True)
        for col, just in [("Asset","left"),("Class","center"),("Price","right"),
                           ("ATR","right"),("RSI","right"),("Signal","center"),
                           ("Pos","center"),("Bars","right"),
                           ("PeakR","right"),("DailyR","right")]:
            table.add_column(col, justify=just,
                             style="cyan" if col == "Asset" else "")

        for asset in ALL_ASSETS:
            pos     = self.positions[asset]
            pos_txt = "LONG" if pos.side == 1 else "SHORT" if pos.side == -1 else "FLAT"
            table.add_row(
                asset, ASSET_CLASS[asset],
                f"{self.latest_price[asset]:.2f}" if not np.isnan(self.latest_price[asset]) else "-",
                f"{self.curr_atr[asset]:.2f}"     if not np.isnan(self.curr_atr[asset])     else "-",
                f"{self.curr_rsi[asset]:.1f}"     if not np.isnan(self.curr_rsi[asset])     else "-",
                self.curr_signal[asset], pos_txt, str(pos.bars_held),
                f"{pos.peak_r:+.2f}" if pos.side != 0 else "-",
                f"{self.daily_r[asset]:+.2f}",
            )

        exits   = self.performance["exits"]
        winrate = safe_div(self.performance["wins"], exits) * 100
        avg_r   = safe_div(self.performance["total_r"], exits)
        pf_raw  = safe_div(self.performance["win_r_sum"], self.performance["loss_r_sum"])
        pf_disp = f"{pf_raw:.2f}" if exits >= 10 else "n/a (<10)"

        subtitle = (
            f"Trades: {exits} | WR: {winrate:.1f}% | "
            f"Total R: {self.performance['total_r']:+.2f} | "
            f"PnL: ${self.performance['total_pnl']:+,.0f} | "
            f"Avg R: {avg_r:+.2f} | PF: {pf_disp}"
        )
        return Panel(table, subtitle=subtitle, border_style="blue")


class AdaptiveMultiAssetTradingModel(MultiAssetTradingModel):
    VERSION = "v11.1 Conservative Repair"
    MIN_EXPECTANCY_BUCKET_TRADES = 15
    EXPECTANCY_SHRINKAGE = 10.0
    EXPECTANCY_PRIOR_R = 0.00
    PORTFOLIO_CORR_LOOKBACK = 60
    PORTFOLIO_CORR_LIMIT = 0.88
    PORTFOLIO_MAX_NEW_TRADES = 2
    LOCAL_DAMAGE_BLOCK_STREAK = 4
    LOCAL_DAMAGE_SOFT_STREAK = 2
    FUTURE_BREAKOUT_CONFIRM_REQUIRED = 2
    ENABLE_CRYPTO_SHORTS = False
    ENABLE_EQUITY_SHORTS = False
    ENABLE_EQUITY_CONTINUATION = False
    ENABLE_ADAPTIVE_EXITS = True
    MIN_SCORE_BY_CLASS = {"crypto": 1.02, "equity": 1.00, "future": 0.98}

    def __init__(self):
        super().__init__()
        self.curr_regime: Dict[str, str] = {a: "-" for a in ALL_ASSETS}
        self.curr_setup: Dict[str, str] = {a: "-" for a in ALL_ASSETS}
        self.pending_candidates: List[dict] = []
        self.expectancy_buckets: Dict[str, dict] = {}
        self.asset_setup_perf: Dict[Tuple[str, str], dict] = {}
        self.asset_recent_r: Dict[str, deque] = {a: deque(maxlen=12) for a in ALL_ASSETS}
        self.equity_long_scores: Dict[str, float] = {}
        self.equity_short_scores: Dict[str, float] = {}
        self.telemetry = CSVBuffer("telemetry_v11_repair.csv", [
            "Timestamp","Asset","Class","Price","ATR","RSI","Signal","Regime","Setup",
            "PositionSide","BarsHeld","PeakR","MAE_R","MFE_R","TrailActive","DailyR",
            "Equity","DrawdownPct","BTCTrend"
        ])
        self.trades = CSVBuffer("trades_v11_repair.csv", [
            "EntryTS","ExitTS","Asset","Class","Side","Setup","Regime",
            "EntryPrice","ExitPrice","Units","EntryATR","BarsHeld",
            "R_Gross","R_Net","PnL_USD","RiskUSD","ExpectedR",
            "MAE_R","MFE_R","EntryScore","ExitReason"
        ])

    # --------------------------------------------------
    # Learning / expectancy helpers
    # --------------------------------------------------

    def _fresh_stats(self) -> dict:
        return {
            "trades": 0, "wins": 0, "losses": 0, "total_r": 0.0,
            "win_r_sum": 0.0, "loss_r_sum": 0.0,
            "sum_mfe": 0.0, "sum_mae": 0.0, "sum_bars": 0.0,
            "recent_r": deque(maxlen=12),
            "cold_streak": 0,
        }

    def _bucket_key(self, asset: str, setup: str, regime: str, side: int) -> str:
        side_txt = "LONG" if side == 1 else "SHORT"
        return f"{asset}|{setup}|{regime}|{side_txt}"

    def _get_bucket_stats(self, asset: str, setup: str, regime: str, side: int) -> dict:
        key = self._bucket_key(asset, setup, regime, side)
        if key not in self.expectancy_buckets:
            self.expectancy_buckets[key] = self._fresh_stats()
        return self.expectancy_buckets[key]

    def _get_asset_setup_stats(self, asset: str, setup: str) -> dict:
        key = (asset, setup)
        if key not in self.asset_setup_perf:
            self.asset_setup_perf[key] = self._fresh_stats()
        return self.asset_setup_perf[key]

    def _record_learning(self, asset: str, pos: Position, r_net: float):
        setup = getattr(pos, "setup_type", "UNKNOWN")
        regime = getattr(pos, "regime", "UNKNOWN")
        side = pos.side
        bucket = self._get_bucket_stats(asset, setup, regime, side)
        aset = self._get_asset_setup_stats(asset, setup)
        for target in [bucket, aset]:
            target["trades"] += 1
            target["total_r"] += r_net
            target["sum_mfe"] += getattr(pos, "trade_mfe_r", 0.0)
            target["sum_mae"] += getattr(pos, "trade_mae_r", 0.0)
            target["sum_bars"] += pos.bars_held
            target["recent_r"].append(r_net)
            if r_net > 0:
                target["wins"] += 1
                target["win_r_sum"] += r_net
                target["cold_streak"] = 0
            else:
                target["losses"] += 1
                target["loss_r_sum"] += abs(r_net)
                target["cold_streak"] += 1
        self.asset_recent_r[asset].append(r_net)

    def bucket_expectancy(self, asset: str, setup: str, regime: str, side: int) -> Tuple[float, float]:
        stats = self._get_bucket_stats(asset, setup, regime, side)
        n = stats["trades"]
        if n == 0:
            return 1.0, self.EXPECTANCY_PRIOR_R

        avg_r = safe_div(stats["total_r"], n)
        winrate = safe_div(stats["wins"], n)
        avg_mfe = safe_div(stats["sum_mfe"], n)
        avg_mae = safe_div(stats["sum_mae"], n)
        shrink = n / (n + self.EXPECTANCY_SHRINKAGE)
        exp_r = (1.0 - shrink) * self.EXPECTANCY_PRIOR_R + shrink * avg_r

        scalar = 1.0 + 0.60 * np.tanh(exp_r)
        scalar += 0.12 * (winrate - 0.50)
        scalar += 0.08 * np.tanh(max(0.0, avg_mfe) - abs(min(0.0, avg_mae)))
        if n >= self.MIN_EXPECTANCY_BUCKET_TRADES and stats["cold_streak"] >= self.LOCAL_DAMAGE_SOFT_STREAK:
            scalar -= 0.15
        scalar = float(np.clip(scalar, 0.45, 1.45))
        return scalar, float(exp_r)

    def localized_damage_scalar(self, asset: str, setup: str) -> float:
        stats = self._get_asset_setup_stats(asset, setup)
        n = stats["trades"]
        if n < 3:
            return 1.0
        recent = list(stats["recent_r"])
        recent_avg = np.mean(recent[-4:]) if recent else 0.0
        if stats["cold_streak"] >= self.LOCAL_DAMAGE_BLOCK_STREAK:
            return 0.0
        if stats["cold_streak"] >= self.LOCAL_DAMAGE_SOFT_STREAK:
            return 0.55
        if n >= self.MIN_EXPECTANCY_BUCKET_TRADES and recent_avg < -0.25:
            return 0.70
        return 1.0

    def adaptive_exit_profile(self, pos: Position, default_time_bars: int,
                              default_min_r: float,
                              default_trail_activate: float,
                              default_trail_mult: float) -> Tuple[int, float, float, float]:
        stats = self.expectancy_buckets.get(getattr(pos, "setup_key", ""))
        if not self.ENABLE_ADAPTIVE_EXITS or not stats or stats["trades"] < self.MIN_EXPECTANCY_BUCKET_TRADES:
            return default_time_bars, default_min_r, default_trail_activate, default_trail_mult

        avg_bars = safe_div(stats["sum_bars"], stats["trades"], default=float(default_time_bars))
        avg_mfe = safe_div(stats["sum_mfe"], stats["trades"])
        avg_mae = safe_div(stats["sum_mae"], stats["trades"])
        avg_r = safe_div(stats["total_r"], stats["trades"])

        time_bars = int(np.clip(round(0.65 * default_time_bars + 0.35 * avg_bars),
                                max(3, int(default_time_bars * 0.6)),
                                int(default_time_bars * 1.6)))
        min_r_by_time = float(np.clip(
            0.65 * default_min_r + 0.35 * max(0.10, min(avg_mfe * 0.40, avg_r + 0.25)),
            0.10, max(default_min_r * 1.5, 1.50)
        ))
        trail_activate = float(np.clip(
            0.70 * default_trail_activate + 0.30 * max(0.50, avg_mfe * 0.35),
            0.50, default_trail_activate + 0.75
        ))
        trail_mult = float(np.clip(
            0.75 * default_trail_mult + 0.25 * (default_trail_mult + max(-0.50, -avg_mae * 0.15)),
            max(1.0, default_trail_mult - 0.50), default_trail_mult + 0.75
        ))
        return time_bars, min_r_by_time, trail_activate, trail_mult

    def path_failure_exit(self, pos: Position) -> bool:
        stats = self.expectancy_buckets.get(getattr(pos, "setup_key", ""))
        if not self.ENABLE_ADAPTIVE_EXITS or not stats or stats["trades"] < self.MIN_EXPECTANCY_BUCKET_TRADES:
            return False
        avg_mfe = safe_div(stats["sum_mfe"], stats["trades"])
        avg_mae = safe_div(stats["sum_mae"], stats["trades"])
        if pos.bars_held < max(2, int(safe_div(stats["sum_bars"], stats["trades"], default=4) * 0.35)):
            return False
        weak_progress = getattr(pos, "trade_mfe_r", 0.0) < max(0.15, avg_mfe * 0.25)
        excessive_adverse = getattr(pos, "trade_mae_r", 0.0) < min(-0.35, avg_mae * 1.15)
        return weak_progress and excessive_adverse

    def pairwise_abs_corr(self, a1: str, a2: str, lookback: int = None) -> float:
        if lookback is None:
            lookback = self.PORTFOLIO_CORR_LOOKBACK
        c1 = self._close(a1)
        c2 = self._close(a2)
        if len(c1) < lookback + 2 or len(c2) < lookback + 2:
            return 0.0
        r1 = np.diff(np.log(c1[-(lookback + 1):]))
        r2 = np.diff(np.log(c2[-(lookback + 1):]))
        if len(r1) != len(r2):
            return 0.0
        corr = np.corrcoef(r1, r2)[0, 1]
        return 0.0 if np.isnan(corr) else float(abs(corr))

    def candidate_corr_ok(self, asset: str, selected_assets: List[str]) -> bool:
        for other in ALL_ASSETS:
            if other == asset:
                continue
            if self.positions[other].side != 0 and self.pairwise_abs_corr(asset, other) > self.PORTFOLIO_CORR_LIMIT:
                return False
        for other in selected_assets:
            if self.pairwise_abs_corr(asset, other) > self.PORTFOLIO_CORR_LIMIT:
                return False
        return True

    def collect_candidate(self, asset: str, side: int, px: float, atr_val: float,
                          stop_mult: float, setup: str, regime: str,
                          conviction: float, expected_r: float,
                          expectancy_scalar: float, localized_scalar: float,
                          score: float):
        if localized_scalar <= 0:
            return
        cls = ASSET_CLASS[asset]
        if score < self.MIN_SCORE_BY_CLASS.get(cls, 1.0):
            return
        self.pending_candidates.append({
            "asset": asset,
            "side": side,
            "price": px,
            "atr_val": atr_val,
            "stop_mult": stop_mult,
            "setup": setup,
            "regime": regime,
            "conviction": conviction,
            "expected_r": expected_r,
            "expectancy_scalar": expectancy_scalar,
            "localized_scalar": localized_scalar,
            "score": score,
        })

    def select_and_execute_candidates(self, ts: str):
        candidates = sorted(self.pending_candidates, key=lambda x: x["score"], reverse=True)
        selected_assets: List[str] = []
        entered = 0
        for cand in candidates:
            if entered >= self.PORTFOLIO_MAX_NEW_TRADES:
                break
            asset = cand["asset"]
            if self.positions[asset].side != 0:
                continue
            if not self.candidate_corr_ok(asset, selected_assets):
                continue
            self.enter_position(
                asset, cand["side"], cand["price"], ts,
                cand["atr_val"], cand["stop_mult"],
                conviction_scalar=cand["conviction"],
                setup_type=cand["setup"], regime=cand["regime"],
                expected_r=cand["expected_r"],
                expectancy_scalar=cand["expectancy_scalar"],
                localized_scalar=cand["localized_scalar"],
                candidate_score=cand["score"],
            )
            if self.positions[asset].side != 0:
                selected_assets.append(asset)
                entered += 1
        self.pending_candidates = []

    # --------------------------------------------------
    # Sizing / execution realism
    # --------------------------------------------------

    def calculate_position_size(self, asset: str, atr_val: float, stop_mult: float,
                                conviction_scalar: float = 1.0,
                                expectancy_scalar: float = 1.0,
                                localized_scalar: float = 1.0) -> Tuple[float, float]:
        cls = ASSET_CLASS[asset]
        combined_scalar = (
            self.vol_regime_scalar(asset) *
            self.class_risk_scalar(cls) *
            max(0.20, conviction_scalar) *
            max(0.20, expectancy_scalar) *
            max(0.0, localized_scalar)
        )
        if combined_scalar < 0.20:
            return 0.0, 0.0

        risk_frac = self.current_risk_fraction() * combined_scalar
        risk_frac = min(MAX_RISK_FRACTION, max(MIN_RISK_FRACTION * 0.20, risk_frac))
        desired_risk = self.equity * risk_frac
        class_remaining = max(
            0.0,
            self.equity * CLASS_RISK_BUDGET[cls] - self.class_risk_in_use(cls)
        )
        risk_usd = min(desired_risk, class_remaining)
        stop_distance = atr_val * stop_mult
        if risk_usd <= 0 or stop_distance <= 0:
            return 0.0, 0.0

        if cls == "future":
            spec = future_spec(asset)
            per_contract_risk = stop_distance * spec["point_value"]
            per_contract_cost = self.future_round_trip_cost_usd(asset, 1.0)
            total_per_contract = per_contract_risk + per_contract_cost
            contracts = int(np.floor(safe_div(risk_usd, total_per_contract)))
            if contracts <= 0:
                return 0.0, 0.0
            sized_risk = contracts * per_contract_risk
            return sized_risk, float(contracts)

        units = safe_div(risk_usd, stop_distance)
        return risk_usd, units

    def adjusted_entry_price(self, side: int, px: float, atr_val: float, setup: str) -> float:
        if "BREAK" in setup or "CONTINUATION" in setup:
            slip = 0.04 * atr_val
        elif "PULLBACK" in setup or "RETEST" in setup or "RALLY" in setup:
            slip = 0.02 * atr_val
        else:
            slip = 0.05 * atr_val
        return px + slip if side == 1 else px - slip

    def generalized_stop_fill_price(self, side: int, stop_price: float,
                                    bar_open: float, bar_high: float,
                                    bar_low: float) -> Optional[float]:
        if side == 1 and bar_low <= stop_price:
            return min(bar_open, stop_price)
        if side == -1 and bar_high >= stop_price:
            return max(bar_open, stop_price)
        return None

    def current_trade_r(self, asset: str, pos: Position, px: float,
                        cost_adjusted: bool = False) -> float:
        # Use initial_stop_dist so that a post-partial-profit breakeven-lock
        # does not shrink stop_dist to 10% of original, inflating R by 10×.
        stop_dist = pos.initial_stop_dist if pos.initial_stop_dist > 0 else abs(pos.entry_price - pos.stop_price)
        if stop_dist == 0:
            stop_dist = max(pos.entry_atr, 1e-9)
        cls = ASSET_CLASS[asset]
        if cls == "future":
            spec = future_spec(asset)
            gross = (px - pos.entry_price) * pos.side * pos.units * spec["point_value"]
            r_val = safe_div(gross, pos.risk_usd)
            if cost_adjusted:
                r_val -= safe_div(self.future_round_trip_cost_usd(asset, pos.units), pos.risk_usd)
            return r_val
        r_val = safe_div((px - pos.entry_price) * pos.side, stop_dist)
        if cost_adjusted:
            r_val -= safe_div(2 * self.one_way_cost(asset) * px, stop_dist)
        return r_val

    def update_trade_path(self, asset: str, pos: Position, bar_high: float, bar_low: float):
        favorable_px = bar_high if pos.side == 1 else bar_low
        adverse_px = bar_low if pos.side == 1 else bar_high
        trade_mfe = self.current_trade_r(asset, pos, favorable_px, cost_adjusted=False)
        trade_mae = self.current_trade_r(asset, pos, adverse_px, cost_adjusted=False)
        pos.trade_mfe_r = max(getattr(pos, "trade_mfe_r", 0.0), trade_mfe)
        pos.trade_mae_r = min(getattr(pos, "trade_mae_r", 0.0), trade_mae)

    def enter_position(self, asset: str, side: int, px: float, ts: str,
                       atr_val: float, stop_mult: float,
                       conviction_scalar: float = 1.0,
                       setup_type: str = "GENERIC",
                       regime: str = "UNKNOWN",
                       expected_r: float = 0.0,
                       expectancy_scalar: float = 1.0,
                       localized_scalar: float = 1.0,
                       candidate_score: float = 1.0):
        if self.trading_halted:
            return
        if self.count_open_positions() >= MAX_TOTAL_POSITIONS:
            return
        cls = ASSET_CLASS[asset]
        if self.count_open_positions(cls) >= MAX_CLASS_POSITIONS[cls]:
            return
        pos = self.positions[asset]
        if pos.side != 0 or pos.cooldown > 0:
            return
        if conviction_scalar < self.min_conviction_threshold(asset) or localized_scalar <= 0.0:
            return

        entry_px = self.adjusted_entry_price(side, px, atr_val, setup_type)
        risk_usd, units = self.calculate_position_size(
            asset, atr_val, stop_mult,
            conviction_scalar=conviction_scalar,
            expectancy_scalar=expectancy_scalar,
            localized_scalar=localized_scalar,
            setup=setup_type
        )
        if risk_usd <= 0 or units <= 0:
            return

        pos.side = side
        pos.entry_price = entry_px
        pos.entry_atr = atr_val
        pos.stop_price = entry_px - side * (atr_val * stop_mult)
        pos.initial_stop_dist = atr_val * stop_mult
        pos.units = units
        pos.risk_usd = risk_usd
        pos.entry_ts = ts
        pos.bars_held = 0
        pos.highest_price = entry_px
        pos.lowest_price = entry_px
        pos.trail_active = False
        pos.peak_r = 0.0
        pos.flip_confirm_count = 0
        pos.rank_exit_count = 0
        pos.setup_type = setup_type
        pos.regime = regime
        pos.setup_key = self._bucket_key(asset, setup_type, regime, side)
        pos.expected_r = expected_r
        pos.expectancy_scalar = expectancy_scalar
        pos.localized_scalar = localized_scalar
        pos.entry_score = candidate_score
        pos.trade_mfe_r = 0.0
        pos.trade_mae_r = 0.0

        self.performance["entries"] += 1
        self.class_perf[cls]["entries"] += 1
        label = "LONG" if side == 1 else "SHORT"
        console.log(
            f"[green][ENTRY][/green] {asset} {label} {setup_type} @ {entry_px:.2f} | "
            f"regime={regime} | score={candidate_score:.2f} | risk=${risk_usd:.0f}"
        )
        # Live broker order submission
        if self._broker is not None:
            self._broker.submit_entry(asset, side, units)

    def exit_position(self, asset: str, px: float, ts: str, reason: str):
        pos = self.positions[asset]
        if pos.side == 0:
            return

        cls = ASSET_CLASS[asset]
        # Always normalise R against the *initial* stop distance so that a
        # post-partial-profit breakeven-lock does not inflate R by 10×.
        stop_dist = pos.initial_stop_dist if pos.initial_stop_dist > 0 else abs(pos.entry_price - pos.stop_price)
        if stop_dist == 0:
            stop_dist = max(pos.entry_atr, 1e-9)

        if cls == "future":
            # --- Futures: dollar P&L via point_value, R relative to risk_usd ---
            spec = future_spec(asset)
            gross_pnl = ((px - pos.entry_price) * pos.side
                         * pos.units * spec["point_value"])
            cost_usd = self.future_round_trip_cost_usd(asset, pos.units)
            pnl = gross_pnl - cost_usd
            r_gross = safe_div(gross_pnl, pos.risk_usd)
            r_net = safe_div(pnl, pos.risk_usd)
        else:
            # --- Equity / crypto: percentage-based ---
            r_gross = safe_div((px - pos.entry_price) * pos.side, stop_dist)
            cost_r = safe_div(2 * self.one_way_cost(asset) * px, stop_dist)
            r_net = r_gross - cost_r
            pnl = r_net * pos.risk_usd

        self.daily_r[asset] += r_net
        self.performance["exits"] += 1
        self.performance["total_r"] += r_net
        self.performance["total_pnl"] += pnl
        self.class_perf[cls]["exits"] += 1
        self.class_perf[cls]["total_r"] += r_net
        self.class_perf[cls]["total_pnl"] += pnl
        self._all_trades_r.append(r_net)

        if r_net > 0:
            self.performance["wins"] += 1
            self.performance["win_r_sum"] += r_net
            self.performance["max_win_r"] = max(self.performance["max_win_r"], r_net)
            self.class_perf[cls]["wins"] += 1
            self.class_perf[cls]["win_r_sum"] += r_net
        else:
            self.performance["losses"] += 1
            self.performance["loss_r_sum"] += abs(r_net)
            self.performance["max_loss_r"] = max(self.performance["max_loss_r"], abs(r_net))
            self.class_perf[cls]["losses"] += 1
            self.class_perf[cls]["loss_r_sum"] += abs(r_net)

        if cls == "future":
            self._futures_trades_r.append(r_net)

        self.update_equity(pnl)
        self.trades.write([
            pos.entry_ts, ts, asset, cls, "LONG" if pos.side == 1 else "SHORT",
            getattr(pos, "setup_type", "UNKNOWN"),
            getattr(pos, "regime", "UNKNOWN"),
            pos.entry_price, px, pos.units, pos.entry_atr, pos.bars_held,
            r_gross, r_net, pnl, pos.risk_usd, getattr(pos, "expected_r", 0.0),
            getattr(pos, "trade_mae_r", 0.0), getattr(pos, "trade_mfe_r", 0.0),
            getattr(pos, "entry_score", 1.0), reason
        ])

        cooldown = (CRYPTO_COOLDOWN_BARS if cls == "crypto" else
                    EQUITY_COOLDOWN_BARS if cls == "equity" else
                    FUTURE_COOLDOWN_BARS)
        self.positions[asset] = Position(cooldown=cooldown)
        color = "green" if r_net > 0 else "red"
        console.log(
            f"[{color}][EXIT {reason}][/{color}] {asset} @ {px:.2f} | "
            f"setup={getattr(pos, 'setup_type', 'UNKNOWN')} | R={r_net:+.2f} | "
            f"PnL=${pnl:+.0f} | Equity=${self.equity:,.0f}"
        )
        # Live broker order submission
        if self._broker is not None:
            self._broker.submit_exit(asset)

    # --------------------------------------------------
    # Regime / setup classifiers
    # --------------------------------------------------

    def benchmark_for_equity(self, asset: str) -> str:
        if asset in ["AAPL", "MSFT", "NVDA", "QQQ"]:
            return "QQQ"
        if asset in ["XLE", "XOM", "CVX"]:
            return "XLE"
        if asset in ["XLV"]:
            return "XLV"
        if asset in ["XLF"]:
            return "XLF"
        if asset in ["XLI"]:
            return "XLI"
        if asset in ["XLY"]:
            return "XLY"
        if asset in ["IWM"]:
            return "IWM"
        return "SPY"

    def equity_market_filter_for_side(self, asset: str, side: int) -> bool:
        # Sector/benchmark filter: require the asset's own benchmark to trend
        # in the desired direction (sector trend).
        benchmark = self.benchmark_for_equity(asset)
        c = self._close(benchmark)
        if len(c) < EQUITY_LONG_TREND_SMA + 10:
            return False
        sma50_v = sma(c, EQUITY_EXIT_SMA)[-1]
        sma100_v = sma(c, EQUITY_LONG_TREND_SMA)[-1]
        if np.isnan(sma50_v) or np.isnan(sma100_v):
            return False
        if side == 1:
            sector_ok = c[-1] > sma100_v and sma50_v > sma100_v
        else:
            sector_ok = c[-1] < sma100_v and sma50_v < sma100_v
        if not sector_ok:
            return False
        # v14.7 - Global macro filter: also require SPY to be trending in the
        # same direction.  Prevents sector longs against a broad bear market
        # (and sector shorts against a broad bull market) where the sector
        # benchmark can temporarily hold its SMA100 even as the market falls.
        if benchmark == "SPY":
            return True   # already checked above; no redundant call needed
        spy_c = self._close("SPY")
        if len(spy_c) < EQUITY_LONG_TREND_SMA + 10:
            return True   # insufficient history; don't block entry
        spy_sma100 = sma(spy_c, EQUITY_LONG_TREND_SMA)[-1]
        if np.isnan(spy_sma100):
            return True
        if side == 1:
            return spy_c[-1] > spy_sma100
        return spy_c[-1] < spy_sma100

    def crypto_relative_strength_short_ok(self, asset: str) -> bool:
        if asset == "BTC-USD":
            return True
        asset_c = self._close(asset)
        btc_c = self._close("BTC-USD")
        min_len = min(len(asset_c), len(btc_c))
        need = max(CRYPTO_ALT_RS_SLOW, CRYPTO_ALT_RS_ROC_LOOKBACK + 1) + 5
        if min_len < need:
            return False
        ratio = asset_c[-min_len:] / btc_c[-min_len:]
        fast_v = ema(ratio, CRYPTO_ALT_RS_FAST)[-1]
        slow_v = ema(ratio, CRYPTO_ALT_RS_SLOW)[-1]
        roc20 = safe_div(ratio[-1], ratio[-1 - CRYPTO_ALT_RS_ROC_LOOKBACK], default=np.nan) - 1.0
        if any(np.isnan([fast_v, slow_v, roc20])):
            return False
        return fast_v < slow_v and roc20 < 0

    def detect_crypto_state(self, asset: str) -> dict:
        o, h, l, c = self._ohlc(asset)
        out = {
            "atr_val": np.nan, "atr_pct": np.nan, "efficiency": np.nan,
            "long_breakout": False, "long_pullback": False,
            "short_breakdown": False, "short_retrace": False,
            "trend_strength": 0.0, "breakout_strength": 0.0,
            "short_break_strength": 0.0, "extension_atr": 0.0,
            "side_bias": 0, "regime": "CHOP"
        }
        if len(c) < CRYPTO_TREND_EMA + 10:
            return out

        fast = ema(c, CRYPTO_FAST_EMA)
        slow = ema(c, CRYPTO_SLOW_EMA)
        trend = ema(c, CRYPTO_TREND_EMA)
        atr_arr = true_atr(h, l, c, CRYPTO_ATR_WINDOW)
        rsi_arr = wilder_rsi(c, CRYPTO_RSI_WINDOW)

        px = c[-1]
        fast_v = fast[-1]
        slow_v = slow[-1]
        trend_v = trend[-1]
        atr_v = atr_arr[-1]
        rsi_v = rsi_arr[-1]

        if any(np.isnan([px, fast_v, slow_v, trend_v, atr_v, rsi_v])) or atr_v == 0:
            return out

        bullish = fast_v > slow_v and px > trend_v and rsi_v > CRYPTO_RSI_BULL_THRESHOLD
        bearish = fast_v < slow_v and px < trend_v and rsi_v < 45
        breakout_strength = safe_div(px - slow_v, atr_v)
        short_break_strength = safe_div(slow_v - px, atr_v)
        trend_strength = safe_div(abs(fast_v - slow_v), atr_v)
        extension_atr = safe_div(px - fast_v, atr_v)
        above_fast_atr = safe_div(px - fast_v, atr_v)
        below_fast_atr = safe_div(fast_v - px, atr_v)
        eff = efficiency_ratio(c, CRYPTO_ER_WINDOW)
        atr_pct = safe_div(atr_v, px)

        out.update({
            "atr_val": atr_v,
            "atr_pct": atr_pct,
            "efficiency": eff,
            "trend_strength": trend_strength,
            "breakout_strength": breakout_strength,
            "short_break_strength": short_break_strength,
            "extension_atr": extension_atr,
        })

        out["long_breakout"] = bullish and breakout_strength >= max(CRYPTO_MIN_BREAKOUT_ATR, 0.20) and extension_atr > 0.25
        out["long_pullback"] = bullish and abs(extension_atr) <= CRYPTO_PULLBACK_MAX_ABS_ATR and below_fast_atr <= CRYPTO_PULLBACK_MAX_BELOW_EMA
        out["short_breakdown"] = bearish and short_break_strength >= max(CRYPTO_MIN_BREAKOUT_ATR, 0.20) and below_fast_atr > 0.25
        out["short_retrace"] = bearish and abs(extension_atr) <= CRYPTO_PULLBACK_MAX_ABS_ATR and above_fast_atr <= CRYPTO_PULLBACK_MAX_BELOW_EMA

        # SQUEEZE expansion: ATR has been contracting (low vol) but is now
        # breaking out with directional intent.  Detect by comparing current
        # ATR% to its own 10-bar median - a 25%+ expansion signals the end of
        # the squeeze.  These setups have high follow-through probability.
        prev_atr_pct = np.median(
            [safe_div(true_atr(h, l, c, CRYPTO_ATR_WINDOW)[i], c[i])
             for i in range(-11, -1)]
        ) if len(c) >= CRYPTO_ATR_WINDOW + 11 else atr_pct
        squeeze_expanding = (
            not np.isnan(prev_atr_pct) and prev_atr_pct < 0.022 and
            atr_pct >= prev_atr_pct * 1.25 and
            atr_pct >= 0.015
        )
        if squeeze_expanding and bullish and breakout_strength >= CRYPTO_MIN_BREAKOUT_ATR:
            out["long_breakout"] = True
        if squeeze_expanding and bearish and short_break_strength >= CRYPTO_MIN_BREAKOUT_ATR:
            out["short_breakdown"] = True

        if atr_pct > 0.10 and (np.isnan(eff) or eff < CRYPTO_MIN_ER):
            out["regime"] = "PANIC"
        elif atr_pct < 0.02:
            out["regime"] = "SQUEEZE"
        elif bullish and not np.isnan(eff) and eff >= 0.40:
            out["regime"] = "TREND_UP"
            out["side_bias"] = 1
        elif bearish and not np.isnan(eff) and eff >= 0.40:
            out["regime"] = "TREND_DOWN"
            out["side_bias"] = -1
        elif bullish or bearish:
            out["regime"] = "PULLBACK"
            out["side_bias"] = 1 if bullish else -1
        return out

    def classify_future_regime(self, sig: dict, px: float) -> str:
        eff = sig.get("efficiency", np.nan)
        vol_ratio = sig.get("vol_ratio", np.nan)
        slope50 = sig.get("slope50", 0.0)
        atr_val = sig.get("atr_val", np.nan)
        sma_v = sig.get("sma_v", np.nan)
        if np.isnan(atr_val) or np.isnan(sma_v) or atr_val == 0:
            return "CHOP"
        dist = safe_div(abs(px - sma_v), atr_val)
        if not np.isnan(vol_ratio) and vol_ratio > 1.25:
            return "EXPLOSIVE"
        if not np.isnan(eff) and eff >= 0.45 and abs(slope50) > 1e-4:
            # Return directional label so ML featuriser and candidate_score
            # regime_bonus can distinguish long vs short trend quality.
            return "TREND_UP" if slope50 > 0 else "TREND_DOWN"
        if dist < 0.75:
            return "RETEST"
        return "CHOP"

    def get_equity_rankings(self) -> List[Tuple[str, float]]:
        scores = []
        score_map = {}
        for asset in EQUITY_ASSETS:
            o, h, l, c = self._ohlc(asset)
            if len(c) < max(EQUITY_MOM_LOOKBACK + 1, EQUITY_LONG_TREND_SMA):
                continue
            benchmark = self.benchmark_for_equity(asset)
            bench_c = self._close(benchmark)
            if len(bench_c) < EQUITY_MOM_LOOKBACK + 1:
                continue
            mom21 = safe_div(c[-1], c[-1 - EQUITY_MOM_SHORT], default=np.nan) - 1.0
            mom63 = safe_div(c[-1], c[-1 - EQUITY_MOM_MEDIUM], default=np.nan) - 1.0
            mom126 = safe_div(c[-1], c[-1 - EQUITY_MOM_LOOKBACK], default=np.nan) - 1.0
            bench63 = safe_div(bench_c[-1], bench_c[-1 - EQUITY_MOM_MEDIUM], default=np.nan) - 1.0
            bench126 = safe_div(bench_c[-1], bench_c[-1 - EQUITY_MOM_LOOKBACK], default=np.nan) - 1.0
            rel63 = mom63 - bench63
            rel126 = mom126 - bench126
            accel = mom21 - mom63
            sma100_v = sma(c, EQUITY_LONG_TREND_SMA)[-1]
            atr_v = true_atr(h, l, c, EQUITY_ATR_WINDOW)[-1]
            if any(np.isnan([mom21, mom63, mom126, rel63, rel126, sma100_v, atr_v])) or atr_v == 0:
                continue
            atr_pct = safe_div(atr_v, c[-1])
            if not (EQUITY_MIN_ATR_PCT <= atr_pct <= EQUITY_MAX_ATR_PCT):
                continue
            extension_atr = safe_div(c[-1] - sma100_v, atr_v)
            extension_penalty = max(0.0, extension_atr - 1.35) * 0.22
            if c[-1] <= sma100_v or mom126 <= 0:
                continue
            score = (
                0.08 * mom21 + 0.30 * mom63 + 0.26 * mom126 +
                0.26 * rel63 + 0.07 * rel126 + 0.03 * accel -
                extension_penalty
            )
            score = float(score)
            scores.append((asset, score))
            score_map[asset] = score
        scores.sort(key=lambda x: x[1], reverse=True)
        self.equity_long_scores = score_map
        return scores

    def get_equity_short_rankings(self) -> List[Tuple[str, float]]:
        scores = []
        score_map = {}
        for asset in EQUITY_ASSETS:
            o, h, l, c = self._ohlc(asset)
            if len(c) < max(EQUITY_MOM_LOOKBACK + 1, EQUITY_LONG_TREND_SMA):
                continue
            benchmark = self.benchmark_for_equity(asset)
            bench_c = self._close(benchmark)
            if len(bench_c) < EQUITY_MOM_LOOKBACK + 1:
                continue
            mom21 = safe_div(c[-1], c[-1 - EQUITY_MOM_SHORT], default=np.nan) - 1.0
            mom63 = safe_div(c[-1], c[-1 - EQUITY_MOM_MEDIUM], default=np.nan) - 1.0
            mom126 = safe_div(c[-1], c[-1 - EQUITY_MOM_LOOKBACK], default=np.nan) - 1.0
            bench63 = safe_div(bench_c[-1], bench_c[-1 - EQUITY_MOM_MEDIUM], default=np.nan) - 1.0
            bench126 = safe_div(bench_c[-1], bench_c[-1 - EQUITY_MOM_LOOKBACK], default=np.nan) - 1.0
            rel63 = bench63 - mom63
            rel126 = bench126 - mom126
            accel = mom63 - mom21
            sma100_v = sma(c, EQUITY_LONG_TREND_SMA)[-1]
            atr_v = true_atr(h, l, c, EQUITY_ATR_WINDOW)[-1]
            if any(np.isnan([mom21, mom63, mom126, rel63, rel126, sma100_v, atr_v])) or atr_v == 0:
                continue
            atr_pct = safe_div(atr_v, c[-1])
            if not (EQUITY_MIN_ATR_PCT <= atr_pct <= EQUITY_MAX_ATR_PCT):
                continue
            extension_atr = safe_div(sma100_v - c[-1], atr_v)
            extension_penalty = max(0.0, extension_atr - 1.35) * 0.22
            if c[-1] >= sma100_v or mom126 >= 0:
                continue
            score = (
                0.08 * (-mom21) + 0.30 * (-mom63) + 0.26 * (-mom126) +
                0.26 * rel63 + 0.07 * rel126 + 0.03 * accel -
                extension_penalty
            )
            score = float(score)
            scores.append((asset, score))
            score_map[asset] = score
        scores.sort(key=lambda x: x[1], reverse=True)
        self.equity_short_scores = score_map
        return scores

    def detect_future_candidate(self, asset: str) -> dict:
        sig = self.detect_future_signal(asset)
        o, h, l, c = self._ohlc(asset)
        out = dict(sig)
        out["setup"] = "NONE"
        out["regime"] = "CHOP"
        if len(c) < max(FUTURE_TREND_SMA, FUTURE_BREAKOUT_LOOKBACK) + 10:
            return out
        px = c[-1]
        out["regime"] = self.classify_future_regime(sig, px)

        # Compute ADX and jump probability - used to gate all setup types
        adx_arr = wilder_adx(h, l, c, FUTURE_ADX_WINDOW)
        adx_val = float(adx_arr[-1]) if not np.isnan(adx_arr[-1]) else 0.0
        j_prob  = jump_probability(c, window=FUTURE_ADX_WINDOW)
        out["adx_val"]   = adx_val
        out["jump_prob"] = j_prob

        # --- BREAKOUT gate: require ADX ≥ 22 and no jump regime ---
        if sig["signal"] == 1:
            if adx_val >= FUTURE_MIN_ADX_BREAKOUT and j_prob < FUTURE_MAX_JUMP_PROB:
                out["setup"] = "LONG_BREAKOUT"
                return out
            # Insufficient trend strength; fall through to TREND / RETEST checks
            out["signal"] = 0
        if sig["signal"] == -1:
            if adx_val >= FUTURE_MIN_ADX_BREAKOUT and j_prob < FUTURE_MAX_JUMP_PROB:
                out["setup"] = "SHORT_BREAKOUT"
                return out
            out["signal"] = 0

        # Shared indicator computation for TREND and RETEST setups
        sma100_v = sma(c, FUTURE_TREND_SMA)[-1]
        sma50_v  = sma(c, FUTURE_FAST_SMA)[-1]
        atr_v    = true_atr(h, l, c, FUTURE_ATR_WINDOW)[-1]
        if any(np.isnan([sma100_v, sma50_v, atr_v])) or atr_v == 0:
            return out

        eff      = sig.get("efficiency", np.nan)   # reuse value already computed in detect_future_signal
        clv      = close_location_value(h[-1], l[-1], px)
        slope50  = sma_slope(c, FUTURE_FAST_SMA, lookback=5)
        dist_fast = safe_div(abs(px - sma50_v), atr_v)
        out["efficiency"] = eff
        out["clv"]        = clv
        out["slope50"]    = slope50
        out["atr_val"]    = atr_v
        out["sma_v"]      = sma100_v
        out["vol_ratio"]  = safe_div(true_atr(h, l, c, 5)[-1], atr_v)
        # Use the *looser* of the two thresholds as the early-return gate.
        # FUTURE_TREND_SETUP_MIN_ER (0.30) < FUTURE_MIN_ER (0.35) because TREND
        # entries operate inside confirmed trends and require less ER than a new
        # BREAKOUT.  Using min() means only ER < 0.30 causes an early return,
        # allowing TREND setups with ER 0.30–0.34 to proceed.  The original code
        # used FUTURE_MIN_ER (0.35) directly, which blocked those setups and made
        # FUTURE_TREND_SETUP_MIN_ER dead code.
        if np.isnan(eff) or eff < min(FUTURE_TREND_SETUP_MIN_ER,
                                      FUTURE_MIN_ER_BY_ASSET.get(asset, FUTURE_MIN_ER)):
            return out

        # --- LONG_TREND / SHORT_TREND: full SMA-stack alignment + ADX gate ---
        # Enters on a shallow pullback to SMA20 within a confirmed trending market.
        # No new N-bar high required; higher ER and ADX thresholds ensure quality.
        sma20_v = sma(c, FUTURE_TREND_SETUP_SMA_FAST)[-1]
        if (not np.isnan(sma20_v) and
                adx_val >= FUTURE_TREND_SETUP_MIN_ADX and
                eff >= FUTURE_TREND_SETUP_MIN_ER and
                j_prob < FUTURE_MAX_JUMP_PROB):
            dist_sma20 = safe_div(abs(px - sma20_v), atr_v)
            if (px > sma100_v and sma50_v > sma100_v and sma20_v > sma50_v and
                    slope50 > 0 and
                    dist_sma20 <= FUTURE_TREND_SETUP_MAX_DIST_ATR and
                    clv >= FUTURE_MIN_CLV):
                out["signal"] = 1
                out["setup"]  = "LONG_TREND"
                return out
            if (px < sma100_v and sma50_v < sma100_v and sma20_v < sma50_v and
                    slope50 < 0 and
                    dist_sma20 <= FUTURE_TREND_SETUP_MAX_DIST_ATR and
                    clv <= (1.0 - FUTURE_MIN_CLV)):
                out["signal"] = -1
                out["setup"]  = "SHORT_TREND"
                return out

        # --- LONG_RETEST / SHORT_RETEST: existing logic with ADX gate ---
        if adx_val < FUTURE_MIN_ADX_RETEST:
            return out

        if (px > sma100_v and sma50_v > sma100_v and slope50 > 0 and
                dist_fast <= FUTURE_RETEST_MAX_DIST_FAST_ATR and clv >= FUTURE_MIN_CLV):
            out["signal"] = 1
            out["setup"]  = "LONG_RETEST"
        elif (px < sma100_v and sma50_v < sma100_v and slope50 < 0 and
                dist_fast <= FUTURE_RETEST_MAX_DIST_FAST_ATR and clv <= (1.0 - FUTURE_MIN_CLV)):
            out["signal"] = -1
            out["setup"]  = "SHORT_RETEST"
        return out

    # --------------------------------------------------
    # Conviction / candidate scores
    # --------------------------------------------------

    def crypto_conviction_v11(self, asset: str, state: dict, side: int, setup: str) -> float:
        score = 0.95
        if side == 1 and self.btc_trend == "UP":
            score += 0.12
        if side == -1 and self.btc_trend == "DOWN":
            score += 0.12
        if not np.isnan(state.get("efficiency", np.nan)) and state["efficiency"] >= CRYPTO_MIN_ER + 0.10:
            score += 0.08
        if 0.02 <= state.get("atr_pct", 0.0) <= 0.08:
            score += 0.05
        if side == 1 and asset != "BTC-USD" and self.crypto_relative_strength_ok(asset):
            score += 0.08
        if side == -1 and asset != "BTC-USD" and self.crypto_relative_strength_short_ok(asset):
            score += 0.08
        if "PULLBACK" in setup or "RETRACE" in setup:
            score += 0.04
        if "BREAK" in setup and abs(state.get("extension_atr", 0.0)) > 1.8:
            score -= 0.10
        if state.get("regime") == "PANIC":
            score -= 0.20
        return float(np.clip(score, 0.55, 1.35))

    def equity_conviction_v11(self, asset: str, side: int, setup: str,
                               distance_atr: float, slope50: float) -> float:
        long_score = self.equity_long_scores.get(asset, 0.0)
        short_score = self.equity_short_scores.get(asset, 0.0)
        score = 0.95
        score += min(0.15, abs(slope50) * 12.0)
        score += 0.10 * min(1.0, max(long_score, short_score) * 10.0)
        if distance_atr <= 0.75:
            score += 0.06
        if "CONTINUATION" in setup or "BREAKDOWN" in setup:
            score += 0.03
        if not self.equity_market_filter_for_side(asset, side):
            score -= 0.20
        # Slope acceleration: penalise entries where the SMA50 slope is decelerating.
        # A high but collapsing slope means the trend quality is degrading at entry.
        c = self._close(asset)
        if len(c) >= 12:
            prev_slope50 = sma_slope(c[:-5], 50, lookback=5)
            accel = slope50 - prev_slope50
            if not np.isnan(accel) and np.sign(accel) != np.sign(slope50) and abs(accel) > 0.0002:
                score -= 0.06  # momentum deceleration penalty
        return float(np.clip(score, 0.55, 1.30))

    def future_conviction_v11(self, asset: str, cand: dict, px: float) -> float:
        score = self.future_conviction_scalar(cand.get("signal", 0), cand, px)
        setup = cand.get("setup", "")
        if setup.endswith("RETEST"):
            score += 0.05
        elif setup.endswith("TREND"):
            # Bonus for strong ADX (confirmed trend direction)
            adx = cand.get("adx_val", 0.0)
            if adx >= 20.0:
                score += min(0.08, (adx - 20.0) / 50.0)
            # Bonus for low jump probability (clean directional move)
            j_prob = cand.get("jump_prob", 0.5)
            score += 0.04 * (1.0 - j_prob)
        # EXPLOSIVE regime: volatility expansion at a new N-bar breakout is the
        # highest-probability trend-following condition; reward BREAKOUT setups
        # while still penalising TREND/RETEST entries (noise is elevated there).
        if cand.get("regime") == "EXPLOSIVE":
            if "BREAKOUT" in setup:
                score += 0.06   # v14.1: bonus for breakout-on-expansion
            else:
                score -= 0.05   # TREND / RETEST: elevated noise, unchanged penalty
        # Rates-proxy filter for metals: ZB=F (30Y bond) below its SMA100 means
        # rising rates → dollar headwind for GC/SI/HG longs (reverse for shorts).
        # ZB above SMA100 (falling rates) provides a tailwind for metals longs.
        _METALS = {"GC=F", "SI=F", "HG=F"}
        if asset in _METALS:
            c_zb = self._close("ZB=F")
            if len(c_zb) >= FUTURE_TREND_SMA + 5:
                zb_sma = sma(c_zb, FUTURE_TREND_SMA)[-1]
                if not np.isnan(zb_sma):
                    side = cand.get("signal", 0)
                    if side == 1 and c_zb[-1] < zb_sma:
                        score -= 0.06   # rising rates headwind for metals longs
                    elif side == 1 and c_zb[-1] > zb_sma:
                        score += 0.04   # falling rates tailwind for metals longs
                    elif side == -1 and c_zb[-1] > zb_sma:
                        score -= 0.06   # falling rates headwind for metals shorts
        return float(np.clip(score, 0.55, 1.30))

    def candidate_score(self, conviction: float, expectancy_scalar: float,
                        localized_scalar: float, expected_r: float,
                        regime: str, setup: str) -> float:
        regime_bonus = {
            "TREND_UP": 1.05, "TREND_DOWN": 1.05,
            "TREND": 1.05, "RETEST": 1.02,
            "PULLBACK": 1.00, "CHOP": 0.92,
            "SQUEEZE": 0.95, "PANIC": 0.82,
            "EXPLOSIVE": 0.95,
        }.get(regime, 1.0)
        setup_bonus = 1.00
        score = conviction * expectancy_scalar * localized_scalar * regime_bonus * setup_bonus
        score *= 1.0 + 0.20 * np.tanh(expected_r)
        return float(score)

    # --------------------------------------------------
    # Strategy handlers
    # --------------------------------------------------

    def handle_crypto(self, asset: str, ts: str):
        o, h, l, c = self._ohlc(asset)
        if len(c) < CRYPTO_TREND_EMA + 10:
            return

        bar_open = o[-1]
        bar_high = h[-1]
        bar_low = l[-1]
        px = c[-1]
        pos = self.positions[asset]
        state = self.detect_crypto_state(asset)
        self.curr_regime[asset] = state["regime"]
        self.curr_setup[asset] = "-"
        self.curr_signal[asset] = "-"

        if np.isnan(state["atr_val"]) or state["atr_val"] == 0:
            return

        if pos.cooldown > 0:
            pos.cooldown -= 1

        if pos.side != 0:
            pos.bars_held += 1
            pos.highest_price = max(pos.highest_price, bar_high)
            pos.lowest_price = min(pos.lowest_price, bar_low)
            self.update_trade_path(asset, pos, bar_high, bar_low)

            r_net = self.current_trade_r(asset, pos, px, cost_adjusted=True)
            pos.peak_r = max(pos.peak_r, r_net)

            setup = getattr(pos, "setup_type", "LONG_BREAKOUT")
            default_time = CRYPTO_TIME_STOP_BARS + (2 if "PULLBACK" in setup or "RETRACE" in setup else 0)
            default_min_r = 0.50 if ("PULLBACK" in setup or "RETRACE" in setup) else CRYPTO_MIN_R_BY_TIME
            default_trail_activate = 0.75 if ("PULLBACK" in setup or "RETRACE" in setup) else CRYPTO_TRAIL_ACTIVATE_R
            default_trail_mult = 1.75 if ("PULLBACK" in setup or "RETRACE" in setup) else CRYPTO_TRAIL_ATR
            time_bars, min_r_by_time, trail_activate_r, trail_mult = self.adaptive_exit_profile(
                pos, default_time, default_min_r, default_trail_activate, default_trail_mult
            )

            if r_net >= trail_activate_r:
                pos.trail_active = True

            current_stop = pos.stop_price
            if pos.peak_r >= CRYPTO_BREAKEVEN_R:
                _be_dist_c = pos.initial_stop_dist if pos.initial_stop_dist > 0 else abs(pos.entry_price - pos.stop_price)
                be = self.breakeven_stop(pos.side, pos.entry_price, _be_dist_c)
                current_stop = max(current_stop, be) if pos.side == 1 else min(current_stop, be)
            if pos.trail_active:
                if pos.side == 1:
                    current_stop = max(current_stop, pos.highest_price - state["atr_val"] * trail_mult)
                else:
                    current_stop = min(current_stop, pos.lowest_price + state["atr_val"] * trail_mult)

            stop_fill = self.generalized_stop_fill_price(pos.side, current_stop, bar_open, bar_high, bar_low)
            exit_reason = None
            if stop_fill is not None:
                self.exit_position(asset, stop_fill, ts, "TRAIL_STOP" if pos.trail_active else "STOP_LOSS")
                return
            if self.path_failure_exit(pos):
                exit_reason = "PATH_FAIL"
            elif r_net <= -CRYPTO_EMERGENCY_STOP_R:
                exit_reason = "EMERGENCY"
            elif pos.bars_held >= time_bars and pos.peak_r < min_r_by_time:
                exit_reason = "TIME_STOP"
            elif pos.side == 1 and state["regime"] == "TREND_DOWN" and pos.bars_held > 3:
                exit_reason = "REGIME_FLIP"
            elif pos.side == -1 and state["regime"] == "TREND_UP" and pos.bars_held > 3:
                exit_reason = "REGIME_FLIP"

            if exit_reason:
                self.exit_position(asset, px, ts, exit_reason)
                return

        if self.positions[asset].side == 0:
            if state["regime"] == "PANIC":
                return

            side = 0
            setup = None
            if state["long_breakout"]:
                side = 1; setup = "LONG_BREAKOUT"
            elif state["long_pullback"]:
                side = 1; setup = "LONG_PULLBACK"
            elif self.ENABLE_CRYPTO_SHORTS and state["short_breakdown"]:
                side = -1; setup = "SHORT_BREAKDOWN"
            elif self.ENABLE_CRYPTO_SHORTS and state["short_retrace"]:
                side = -1; setup = "SHORT_RETRACE"

            if side == 0 or setup is None:
                return

            if side == 1:
                if REQUIRE_BTC_FILTER and self.btc_trend not in ["UP", "NEUTRAL"]:
                    return
                if asset != "BTC-USD":
                    if CRYPTO_ALT_REQUIRE_BTC_UP and self.btc_trend != "UP":
                        return
                    if not self.crypto_relative_strength_ok(asset):
                        return
            else:
                if REQUIRE_BTC_FILTER and self.btc_trend not in ["DOWN", "NEUTRAL"]:
                    return
                if asset != "BTC-USD" and not self.crypto_relative_strength_short_ok(asset):
                    return

            atr_pct = state["atr_pct"]
            if not (CRYPTO_MIN_ATR_PCT <= atr_pct <= CRYPTO_MAX_ATR_PCT):
                return
            if not np.isnan(state["efficiency"]) and state["efficiency"] < CRYPTO_MIN_ER:
                return
            if side == 1 and state["extension_atr"] > CRYPTO_MAX_EXTENSION_ATR:
                return
            if side == -1 and (-state["extension_atr"]) > CRYPTO_MAX_EXTENSION_ATR:
                return

            conviction = self.crypto_conviction_v11(asset, state, side, setup)
            expectancy_scalar, expected_r = self.bucket_expectancy(asset, setup, state["regime"], side)
            localized_scalar = self.localized_damage_scalar(asset, setup)
            score = self.candidate_score(conviction, expectancy_scalar, localized_scalar, expected_r,
                                         state["regime"], setup)
            stop_mult = self.crypto_stop_mult(state["trend_strength"])
            self.curr_setup[asset] = setup
            self.curr_signal[asset] = setup.replace("LONG_", "L_").replace("SHORT_", "S_")
            self.collect_candidate(asset, side, px, state["atr_val"], stop_mult, setup, state["regime"],
                                   conviction, expected_r, expectancy_scalar, localized_scalar, score)

    def handle_equities(self, ts: str, equity_assets_in_bar: set):
        long_rankings = self.get_equity_rankings()
        short_rankings = self.get_equity_short_rankings()
        top_long_assets = [a for a, _ in long_rankings[:EQUITY_TOP_N]]
        top_short_assets = [a for a, _ in short_rankings[:EQUITY_TOP_N]]
        top_long_set = set(top_long_assets)
        top_short_set = set(top_short_assets)

        for asset in EQUITY_ASSETS:
            if asset not in equity_assets_in_bar:
                if self.positions[asset].cooldown > 0:
                    self.positions[asset].cooldown -= 1
                continue

            o, h, l, c = self._ohlc(asset)
            if len(c) < max(EQUITY_MOM_LOOKBACK + 1, EQUITY_LONG_TREND_SMA):
                continue

            bar_open = o[-1]; bar_high = h[-1]; bar_low = l[-1]; px = c[-1]
            pos = self.positions[asset]
            atr_val = true_atr(h, l, c, EQUITY_ATR_WINDOW)[-1]
            sma50_v = sma(c, EQUITY_EXIT_SMA)[-1]
            sma100_v = sma(c, EQUITY_LONG_TREND_SMA)[-1]
            slope50 = sma_slope(c, EQUITY_EXIT_SMA, lookback=5)
            if any(np.isnan([atr_val, sma50_v, sma100_v])) or atr_val == 0:
                continue

            long_setup = "-"
            short_setup = "-"
            self.curr_regime[asset] = "UPTREND" if px > sma100_v and slope50 > 0 else "DOWNTREND" if px < sma100_v and slope50 < 0 else "CHOP"
            self.curr_setup[asset] = "-"
            self.curr_signal[asset] = "-"

            if pos.cooldown > 0:
                pos.cooldown -= 1

            if pos.side != 0:
                pos.bars_held += 1
                pos.highest_price = max(pos.highest_price, bar_high)
                pos.lowest_price = min(pos.lowest_price, bar_low)
                self.update_trade_path(asset, pos, bar_high, bar_low)
                r_net = self.current_trade_r(asset, pos, px, cost_adjusted=True)
                pos.peak_r = max(pos.peak_r, r_net)

                setup = getattr(pos, "setup_type", "LONG_PULLBACK")
                default_time = EQUITY_TIME_STOP_BARS + (2 if "PULLBACK" in setup or "RALLY" in setup else 0)
                default_min_r = 0.35 if ("PULLBACK" in setup or "RALLY" in setup) else EQUITY_MIN_R_BY_TIME
                default_trail_activate = 0.80 if ("PULLBACK" in setup or "RALLY" in setup) else EQUITY_TRAIL_ACTIVATE_R
                default_trail_mult = 1.60 if ("PULLBACK" in setup or "RALLY" in setup) else EQUITY_TRAIL_ATR
                time_bars, min_r_by_time, trail_activate_r, trail_mult = self.adaptive_exit_profile(
                    pos, default_time, default_min_r, default_trail_activate, default_trail_mult
                )
                if r_net >= trail_activate_r:
                    pos.trail_active = True

                current_stop = pos.stop_price
                if pos.peak_r >= EQUITY_BREAKEVEN_R:
                    _be_dist_eq = pos.initial_stop_dist if pos.initial_stop_dist > 0 else abs(pos.entry_price - pos.stop_price)
                    be = self.breakeven_stop(pos.side, pos.entry_price, _be_dist_eq)
                    current_stop = max(current_stop, be) if pos.side == 1 else min(current_stop, be)
                if pos.trail_active:
                    if pos.side == 1:
                        current_stop = max(current_stop, pos.highest_price - atr_val * trail_mult)
                    else:
                        current_stop = min(current_stop, pos.lowest_price + atr_val * trail_mult)

                stop_fill = self.generalized_stop_fill_price(pos.side, current_stop, bar_open, bar_high, bar_low)
                if stop_fill is not None:
                    self.exit_position(asset, stop_fill, ts, "TRAIL_STOP" if pos.trail_active else "STOP_LOSS")
                    continue

                if pos.side == 1:
                    if asset not in top_long_set:
                        pos.rank_exit_count += 1
                    else:
                        pos.rank_exit_count = 0
                else:
                    if asset not in top_short_set:
                        pos.rank_exit_count += 1
                    else:
                        pos.rank_exit_count = 0

                exit_reason = None
                if self.path_failure_exit(pos):
                    exit_reason = "PATH_FAIL"
                elif pos.side == 1 and px < sma100_v:
                    exit_reason = "SMA100_EXIT"
                elif pos.side == -1 and px > sma100_v:
                    exit_reason = "SMA100_EXIT"
                elif pos.side == 1 and px < sma50_v and pos.highest_price >= sma50_v and not pos.trail_active:
                    # Only apply SMA50 trailing exit after the trade has traded at
                    # or above SMA50.  This prevents PULLBACK entries (made near
                    # SMA100, below SMA50) from being stopped out immediately on
                    # the very next bar before the trade has had a chance to develop.
                    # Suppressed once trail is active — the ATR trail protects more
                    # precisely and a single SMA50 close would clip 3R+ winners.
                    exit_reason = "SMA50_EXIT"
                elif pos.side == -1 and px > sma50_v and pos.lowest_price <= sma50_v and not pos.trail_active:
                    exit_reason = "SMA50_EXIT"
                elif pos.bars_held >= time_bars and pos.peak_r < min_r_by_time:
                    exit_reason = "TIME_STOP"
                elif pos.rank_exit_count >= EQUITY_RANK_EXIT_BARS:
                    exit_reason = "RANK_EXIT"

                if exit_reason:
                    self.exit_position(asset, px, ts, exit_reason)
                    continue

            if self.positions[asset].side == 0:
                if not self.equity_correlation_allows_entry(asset):
                    continue

                dist_long_atr = safe_div(px - sma100_v, atr_val)
                dist_short_atr = safe_div(sma100_v - px, atr_val)

                # Efficiency-ratio gate: block entries in choppy, non-trending
                # markets.  A low ER means price has been oscillating without
                # directional progress, making pullback/rally entries high-risk.
                er = efficiency_ratio(c, 20)
                if not np.isnan(er) and er < 0.25:
                    continue

                side = 0
                setup = None

                if asset in top_long_set and self.equity_market_filter_for_side(asset, 1) and (sma50_v > sma100_v) and slope50 > 0:
                    if 0 <= dist_long_atr <= EQUITY_PULLBACK_MAX_DIST_ATR:
                        side = 1; setup = "LONG_PULLBACK"
                    elif self.ENABLE_EQUITY_CONTINUATION and EQUITY_CONTINUATION_MIN_DIST_ATR < dist_long_atr <= EQUITY_CONTINUATION_MAX_DIST_ATR and self.equity_long_scores.get(asset, 0.0) > 0:
                        side = 1; setup = "LONG_CONTINUATION"

                if self.ENABLE_EQUITY_SHORTS and side == 0 and asset in top_short_set and self.equity_market_filter_for_side(asset, -1) and (sma50_v < sma100_v) and slope50 < 0:
                    if 0 <= dist_short_atr <= EQUITY_CONTINUATION_MIN_DIST_ATR:
                        side = -1; setup = "SHORT_RALLY"
                    elif EQUITY_CONTINUATION_MIN_DIST_ATR < dist_short_atr <= EQUITY_CONTINUATION_MAX_DIST_ATR and self.equity_short_scores.get(asset, 0.0) > 0:
                        side = -1; setup = "SHORT_BREAKDOWN"

                if side == 0 or setup is None:
                    continue

                # RSI quality gate: block PULLBACK entries that are overbought
                # (RSI > 62 = momentum extended, poor R/R) or in a broken trend
                # (RSI < 38 = selling pressure likely continues).
                rsi_v = self.curr_rsi[asset]
                if not np.isnan(rsi_v):
                    if setup == "LONG_PULLBACK" and not (EQUITY_PULLBACK_RSI_MIN <= rsi_v <= EQUITY_PULLBACK_RSI_MAX):
                        continue
                    if setup == "SHORT_RALLY" and not (EQUITY_SHORT_RALLY_RSI_MIN <= rsi_v <= EQUITY_SHORT_RALLY_RSI_MAX):
                        continue

                # CLV gate: require the day's close in the upper half of the bar
                # range for long entries, and the lower half for short entries.
                # This avoids entering on down-closing bars within an uptrend and
                # mirrors the CLV filter already applied to futures entries.
                bar_clv = close_location_value(bar_high, bar_low, px)
                if side == 1 and bar_clv < 0.45:
                    continue
                if side == -1 and bar_clv > 0.55:
                    continue

                regime = self.curr_regime[asset]
                distance_atr = dist_long_atr if side == 1 else dist_short_atr
                conviction = self.equity_conviction_v11(asset, side, setup, distance_atr, slope50)
                expectancy_scalar, expected_r = self.bucket_expectancy(asset, setup, regime, side)
                localized_scalar = self.localized_damage_scalar(asset, setup)
                # Per-setup stop ATR: CONTINUATION entries are made at extension,
                # so tighter stops improve R/R.  PULLBACK / RALLY entries are
                # closer to SMA100 support/resistance and keep the wider stop.
                if "CONTINUATION" in setup or "BREAKDOWN" in setup:
                    entry_stop_atr = 1.80
                else:
                    entry_stop_atr = EQUITY_STOP_ATR
                score = self.candidate_score(conviction, expectancy_scalar, localized_scalar, expected_r,
                                             regime, setup)
                self.curr_setup[asset] = setup
                self.curr_signal[asset] = setup.replace("LONG_", "L_").replace("SHORT_", "S_")
                self.collect_candidate(asset, side, px, atr_val, entry_stop_atr, setup, regime,
                                       conviction, expected_r, expectancy_scalar, localized_scalar, score)

    def handle_futures(self, asset: str, ts: str):
        o, h, l, c = self._ohlc(asset)
        if len(c) < max(FUTURE_TREND_SMA, FUTURE_BREAKOUT_LOOKBACK) + 10:
            return

        bar_open = o[-1]; bar_high = h[-1]; bar_low = l[-1]; px = c[-1]
        pos = self.positions[asset]
        cand = self.detect_future_candidate(asset)
        atr_val = cand.get("atr_val", np.nan)
        signal = cand.get("signal", 0)
        setup = cand.get("setup", "NONE")
        regime = cand.get("regime", "CHOP")
        self.curr_regime[asset] = regime
        self.curr_setup[asset] = setup if setup != "NONE" else "-"
        self.curr_signal[asset] = setup.replace("LONG_", "L_").replace("SHORT_", "S_") if setup != "NONE" else "-"

        if np.isnan(atr_val) or atr_val == 0:
            return

        if pos.cooldown > 0:
            pos.cooldown -= 1

        if pos.side != 0:
            pos.bars_held += 1
            pos.highest_price = max(pos.highest_price, bar_high)
            pos.lowest_price = min(pos.lowest_price, bar_low)
            self.update_trade_path(asset, pos, bar_high, bar_low)
            r_net = self.current_trade_r(asset, pos, px, cost_adjusted=True)
            pos.peak_r = max(pos.peak_r, r_net)

            active_setup = getattr(pos, "setup_type", "LONG_BREAKOUT")
            _is_retest = "RETEST" in active_setup
            _is_trend  = active_setup in ("LONG_TREND", "SHORT_TREND")

            # Partial profit for futures BREAKOUT / BREAKDOWN entries:
            # take 50 % off at FUTURE_PARTIAL_PROFIT_R (1.5R) to lock in gains
            # before the full trail activates.  Mirrors the crypto mechanism.
            # `take_partial_profit` is defined in ROIBarbellModel (the only
            # concrete subclass).  `hasattr` guards against direct instantiation
            # of this base class; if the method is absent, hasattr returns False
            # and the block is safely skipped (no AttributeError).
            _is_fut_breakout = any(tag in active_setup for tag in ["BREAKOUT", "BREAKDOWN"])
            if (_is_fut_breakout and not getattr(pos, 'scaled_out', False) and
                    pos.peak_r >= FUTURE_PARTIAL_PROFIT_R and
                    hasattr(self, 'take_partial_profit')):
                self.take_partial_profit(asset, pos, px, ts)
                if pos.side == 0:
                    return
            default_time = (FUTURE_TIME_STOP_BARS + 2 if _is_retest else
                            FUTURE_TIME_STOP_BARS + 3 if _is_trend else
                            FUTURE_TIME_STOP_BARS)
            default_min_r = (0.35 if _is_retest else
                             0.35 if _is_trend else   # TREND needs patience; lower bar (was 0.40)
                             0.45)                    # BREAKOUT: slightly lower than global 0.50
            default_trail_activate = (0.80 if _is_retest else
                                      1.00 if _is_trend else
                                      FUTURE_TRAIL_ACTIVATE_R)
            default_trail_mult = (1.60 if _is_retest else
                                  1.80 if _is_trend else
                                  FUTURE_TRAIL_ATR)
            time_bars, min_r_by_time, trail_activate_r, trail_mult = self.adaptive_exit_profile(
                pos, default_time, default_min_r, default_trail_activate, default_trail_mult
            )

            if r_net >= trail_activate_r:
                pos.trail_active = True

            current_stop = pos.stop_price
            if pos.peak_r >= FUTURE_BREAKEVEN_R:
                _be_dist = pos.initial_stop_dist if pos.initial_stop_dist > 0 else abs(pos.entry_price - pos.stop_price)
                be = self.breakeven_stop(pos.side, pos.entry_price, _be_dist)
                current_stop = max(current_stop, be) if pos.side == 1 else min(current_stop, be)
            if pos.trail_active:
                if pos.side == 1:
                    current_stop = max(current_stop, pos.highest_price - atr_val * trail_mult)
                else:
                    current_stop = min(current_stop, pos.lowest_price + atr_val * trail_mult)

            stop_fill = self.generalized_stop_fill_price(pos.side, current_stop, bar_open, bar_high, bar_low)
            if stop_fill is not None:
                self.exit_position(asset, stop_fill, ts, "TRAIL_STOP" if pos.trail_active else "STOP_LOSS")
                return

            exit_reason = None
            if self.path_failure_exit(pos):
                exit_reason = "PATH_FAIL"
            elif pos.bars_held >= time_bars and pos.peak_r < min_r_by_time:
                exit_reason = "TIME_STOP"
            elif (not pos.trail_active and
                  not np.isnan(cand.get("sma_v", np.nan)) and
                  ((pos.side == 1 and px < cand.get("sma_v", np.nan)) or
                   (pos.side == -1 and px > cand.get("sma_v", np.nan)))):
                # SMA100 floor: price crossed back through the trend baseline
                # before the ATR trail engaged; exit early rather than waiting
                # for the full trail distance to be given back.
                exit_reason = "SMA_FLOOR"
            elif signal == -pos.side:
                pos.flip_confirm_count += 1
                if pos.flip_confirm_count >= FUTURE_FLIP_CONFIRM_BARS:
                    exit_reason = "SIGNAL_FLIP"
            else:
                pos.flip_confirm_count = 0

            # CHOP-regime degradation exit: once a trade has banked meaningful
            # profit (peak_r ≥ 1.0) and the regime has deteriorated to CHOP for
            # 3 consecutive bars, close the position rather than holding through
            # a slow mean-reversion that the formal SIGNAL_FLIP cannot catch.
            if exit_reason is None:
                if regime == "CHOP" and pos.peak_r >= 1.0:
                    pos.chop_regime_count += 1
                    if pos.chop_regime_count >= 3:
                        exit_reason = "CHOP_REGIME"
                else:
                    pos.chop_regime_count = 0

            if exit_reason:
                self.exit_position(asset, px, ts, exit_reason)
                return

        if self.positions[asset].side == 0 and pos.cooldown == 0 and signal != 0 and setup != "NONE":
            required = self.FUTURE_BREAKOUT_CONFIRM_REQUIRED if "BREAKOUT" in setup else 1
            pos.flip_confirm_count += 1
            if pos.flip_confirm_count >= required:
                # Correlation guard: block entry when another open future is
                # highly correlated (> 0.85) — prevents doubling up on the
                # same macro driver (e.g. GC+SI or ZC+ZS simultaneously).
                if not self.futures_correlation_allows_entry(asset):
                    pos.flip_confirm_count = 0
                    return
                # Volume confirmation on breakout setups
                if "BREAKOUT" in setup and not self.vol_breakout_ok(asset):
                    pos.flip_confirm_count = 0
                    return
                conviction = self.future_conviction_v11(asset, cand, px)
                expectancy_scalar, expected_r = self.bucket_expectancy(asset, setup, regime, signal)
                localized_scalar = self.localized_damage_scalar(asset, setup)
                score = self.candidate_score(conviction, expectancy_scalar, localized_scalar, expected_r,
                                             regime, setup)
                stop_mult = self.future_stop_mult(asset, cand)
                if "RETEST" in setup:
                    stop_mult = max(1.9, stop_mult - 0.20)
                elif setup in ("LONG_TREND", "SHORT_TREND"):
                    # TREND entries are close to SMA20 - tighter stop is viable
                    stop_mult = max(2.0, stop_mult - 0.15)
                self.collect_candidate(asset, signal, px, atr_val, stop_mult, setup, regime,
                                       conviction, expected_r, expectancy_scalar, localized_scalar, score)
                pos.flip_confirm_count = 0
        elif self.positions[asset].side == 0:
            pos.flip_confirm_count = 0

    # --------------------------------------------------
    # Bar processing / dashboard
    # --------------------------------------------------

    def process_bar(self, ts: pd.Timestamp, bar_map: Dict[str, dict]):
        date_str = ts.strftime("%Y-%m-%d")
        ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
        self.reset_daily(date_str)
        self.pending_candidates = []

        for asset, bar in bar_map.items():
            if isinstance(bar, dict):
                ob = OHLCBar(bar["open"], bar["high"], bar["low"], bar["close"],
                             bar.get("volume", 0.0))
            else:
                v = float(bar)
                ob = OHLCBar(v, v, v, v)
            self.ohlc_history[asset].append(ob)
            self.latest_price[asset] = ob.close
            self.refresh_asset_snapshot(asset)

        self.btc_trend = self.get_btc_trend()

        if self.trading_halted:
            for asset, pos in self.positions.items():
                if pos.cooldown > 0:
                    pos.cooldown -= 1
                if pos.side != 0 and not np.isnan(self.latest_price[asset]):
                    self.exit_position(asset, self.latest_price[asset], ts_str, "HALT")
            return

        for asset in CRYPTO_ASSETS:
            if asset in bar_map:
                self.handle_crypto(asset, ts_str)

        equity_in_bar = {a for a in EQUITY_ASSETS if a in bar_map}
        self.handle_equities(ts_str, equity_in_bar)

        for asset in FUTURES_ASSETS:
            if asset in bar_map:
                self.handle_futures(asset, ts_str)

        self.select_and_execute_candidates(ts_str)

        for asset in bar_map:
            pos = self.positions[asset]
            self.telemetry.write([
                ts_str, asset, ASSET_CLASS[asset], self.latest_price[asset],
                self.curr_atr[asset], self.curr_rsi[asset], self.curr_signal[asset],
                self.curr_regime[asset], self.curr_setup[asset],
                pos.side, pos.bars_held, pos.peak_r,
                getattr(pos, "trade_mae_r", 0.0), getattr(pos, "trade_mfe_r", 0.0),
                pos.trail_active, self.daily_r[asset], self.equity,
                safe_div(self.peak_equity - self.equity, self.peak_equity),
                self.btc_trend
            ])

        # Daily MTM snapshot: updates max_dd from open-position risk and feeds
        # the _daily_equity series used for accurate Sharpe calculation.
        self._record_daily_mtm()

    def update_dashboard(self) -> Panel:
        status = "[red]HALTED[/red]" if self.trading_halted else "[green]LIVE[/green]"
        dd_pct = self.max_dd * 100
        title = (
            f"Multi-Asset Model {self.VERSION} | {status} | BTC: {self.btc_trend} | "
            f"Equity: ${self.equity:,.0f} | DD: {dd_pct:.1f}%"
        )
        table = Table(title=title, expand=True)
        for col, just in [("Asset","left"),("Class","center"),("Price","right"),
                          ("ATR","right"),("Signal","center"),("Regime","center"),
                          ("Pos","center"),("Bars","right"),("PeakR","right"),("DailyR","right")]:
            table.add_column(col, justify=just,
                             style="cyan" if col == "Asset" else "")
        for asset in ALL_ASSETS:
            pos = self.positions[asset]
            pos_txt = "LONG" if pos.side == 1 else "SHORT" if pos.side == -1 else "FLAT"
            table.add_row(
                asset, ASSET_CLASS[asset],
                f"{self.latest_price[asset]:.2f}" if not np.isnan(self.latest_price[asset]) else "-",
                f"{self.curr_atr[asset]:.2f}" if not np.isnan(self.curr_atr[asset]) else "-",
                self.curr_signal[asset], self.curr_regime[asset], pos_txt, str(pos.bars_held),
                f"{pos.peak_r:+.2f}" if pos.side != 0 else "-",
                f"{self.daily_r[asset]:+.2f}",
            )
        exits = self.performance["exits"]
        winrate = safe_div(self.performance["wins"], exits) * 100
        avg_r = safe_div(self.performance["total_r"], exits)
        pf_raw = safe_div(self.performance["win_r_sum"], self.performance["loss_r_sum"])
        pf_disp = f"{pf_raw:.2f}" if exits >= 10 else "n/a (<10)"
        subtitle = (
            f"Trades: {exits} | WR: {winrate:.1f}% | Total R: {self.performance['total_r']:+.2f} | "
            f"PnL: ${self.performance['total_pnl']:+,.0f} | Avg R: {avg_r:+.2f} | PF: {pf_disp} | "
            f"Buckets: {len(self.expectancy_buckets)}"
        )
        return Panel(table, subtitle=subtitle, border_style="blue")


# =========================================================
# MONTE CARLO
# =========================================================

def run_monte_carlo(
    futures_r: List[float],
    initial_capital: float   = INITIAL_CAPITAL,
    n_sims: int              = MC_SIMULATIONS,
    ruin_dd_threshold: float = MC_RUIN_DRAWDOWN,
    seed: int                = 42,
) -> None:
    if len(futures_r) < 5:
        console.log("[yellow]Monte Carlo: need ≥ 5 futures trades[/yellow]")
        return

    r_arr    = np.array(futures_r, dtype=float)
    n_trades = len(r_arr)
    rng      = np.random.default_rng(seed=seed)

    terminal_equities = np.empty(n_sims, dtype=float)
    max_drawdowns     = np.empty(n_sims, dtype=float)
    ruin_count        = 0

    def _risk_frac(eq: float, peak: float) -> float:
        dd = safe_div(peak - eq, peak)
        if dd > 0.10: return MIN_RISK_FRACTION
        if dd < 0.02: return MAX_RISK_FRACTION * 0.75
        return BASE_RISK_FRACTION

    def _sample_path() -> np.ndarray:
        sampled = []
        while len(sampled) < n_trades:
            block_len = int(rng.integers(MC_BLOCK_MIN_TRADES, MC_BLOCK_MAX_TRADES + 1))
            start_idx = int(rng.integers(0, n_trades))
            for j in range(block_len):
                sampled.append(r_arr[(start_idx + j) % n_trades])
                if len(sampled) >= n_trades:
                    break
        return np.array(sampled[:n_trades], dtype=float)

    for i in range(n_sims):
        sampled = _sample_path()
        eq = initial_capital; peak = initial_capital; max_dd_sim = 0.0
        for r in sampled:
            r_eff = float(r)
            if r_eff < 0 and rng.random() < MC_STRESS_LOSS_PROB:
                r_eff *= MC_STRESS_LOSS_MULTIPLIER
            rf  = _risk_frac(eq, peak)
            # NOTE (v13.5): eq + r_eff * eq * rf treats each R-multiple as a
            # fraction of equity - valid for a continuously-sized strategy.
            # Actual futures sizing uses integer contracts which introduces a
            # floor effect: below a certain equity level, 1 contract represents
            # more than `rf` fraction of the account (understated risk).  At
            # high equity levels fractional scaling over-states growth.  This
            # MC therefore gives directionally correct scenario distributions
            # but the variance in low-equity / high-equity tails is somewhat
            # underestimated and overestimated, respectively.
            eq  = max(0.0, eq + r_eff * eq * rf)
            if eq > peak: peak = eq
            dd = safe_div(peak - eq, peak)
            if dd > max_dd_sim: max_dd_sim = dd
        terminal_equities[i] = eq
        max_drawdowns[i]     = max_dd_sim
        if max_dd_sim >= ruin_dd_threshold:
            ruin_count += 1

    ruin_prob = ruin_count / n_sims * 100
    pcts      = [5, 25, 50, 75, 95]
    eq_pcts   = np.percentile(terminal_equities, pcts)
    dd_pcts   = np.percentile(max_drawdowns,     pcts)

    t = Table(title=f"Monte Carlo - Futures ({n_sims:,} sims, {n_trades} trades each)")
    t.add_column("Metric", style="cyan")
    for lbl in ["p5","p25","Median","p75","p95"]:
        t.add_column(lbl, justify="right")
    t.add_row("Terminal Equity ($)", *[f"${v:,.0f}"    for v in eq_pcts])
    t.add_row("Max Drawdown (%)",    *[f"{v*100:.1f}%" for v in dd_pcts])
    console.print(t)

    color = "red" if ruin_prob > 10 else "yellow" if ruin_prob > 5 else "green"
    console.print(
        f"[{color}]Ruin probability (DD ≥ {ruin_dd_threshold*100:.0f}%): "
        f"{ruin_prob:.1f}% ({ruin_count:,}/{n_sims:,})[/{color}]"
    )
    console.print(
        f"Expected: ${np.mean(terminal_equities):,.0f} | "
        f"Std: ${np.std(terminal_equities):,.0f} | "
        f"Median: ${np.median(terminal_equities):,.0f}"
    )


def run_trade_stress_report(
    trades_r: List[float],
    initial_capital: float = INITIAL_CAPITAL,
) -> None:
    if len(trades_r) < 10:
        console.log("[yellow]Stress report: need ≥ 10 realised trades[/yellow]")
        return

    def _rf(eq: float, peak: float) -> float:
        dd = safe_div(peak - eq, peak)
        if dd > 0.10: return MIN_RISK_FRACTION
        if dd < 0.02: return MAX_RISK_FRACTION * 0.75
        return BASE_RISK_FRACTION

    scenarios = [
        ("Base",      1.00, 1.00, 0.00),
        ("Realistic", STRESS_REALISTIC_WIN_MULT, STRESS_REALISTIC_LOSS_MULT, STRESS_REALISTIC_COST_R),
        ("Hostile",   STRESS_HOSTILE_WIN_MULT,   STRESS_HOSTILE_LOSS_MULT,   STRESS_HOSTILE_COST_R),
    ]
    t = Table(title="Trade Stress Report")
    t.add_column("Scenario", style="cyan")
    t.add_column("Terminal Equity", justify="right")
    t.add_column("Return",          justify="right")
    t.add_column("Max DD",          justify="right")

    for name, win_mult, loss_mult, cost_r in scenarios:
        eq = initial_capital; peak = initial_capital; max_dd = 0.0
        for r in trades_r:
            r_adj = (r * win_mult - cost_r) if r >= 0 else (r * loss_mult - cost_r)
            rf    = _rf(eq, peak)
            eq    = max(0.0, eq + r_adj * eq * rf)
            peak  = max(peak, eq)
            max_dd = max(max_dd, safe_div(peak - eq, peak))
        ret = safe_div(eq - initial_capital, initial_capital) * 100
        t.add_row(name, f"${eq:,.0f}", f"{ret:+.1f}%", f"{max_dd*100:.1f}%")
    console.print(t)


# =========================================================
# BACKTEST
# =========================================================

def load_backtest_data(start: str, end: str) -> Dict[str, pd.DataFrame]:
    """Load OHLCV history for all assets using batched fetch + parquet cache.

    Data source priority (see ``DataProvider.get_history_batch``):
        1. Polygon.io — equities and crypto when ``POLYGON_API_KEY`` is set.
        2. Binance    — crypto when Polygon.io is unavailable.
        3. yfinance   — futures and any asset where higher-priority sources
                        return no data.  A per-symbol fallback is attempted
                        whenever the yfinance batch call returns empty for a
                        ticker, so each asset independently receives its own
                        price series rather than being silently omitted.
    Results are cached to ``.price_cache/`` and reused within 23 hours,
    making repeated Optuna trial runs essentially instantaneous after the
    first download.
    """
    console.log("Loading price history (batched)...")
    raw = _data_provider.get_history_batch(ALL_ASSETS, start, end, DATA_INTERVAL)
    data: Dict[str, pd.DataFrame] = {}
    for asset, df in raw.items():
        if df.empty:
            console.log(f"[yellow]  No data for {asset}[/yellow]")
            continue
        have_ohlc = all(c in df.columns for c in ["Open","High","Low","Close"])
        if have_ohlc:
            keep_cols = [c for c in ["Open","High","Low","Close","Volume"] if c in df.columns]
            data[asset] = df[keep_cols].copy()
            console.log(f"  {asset} → {len(df)} bars (OHLC{'+V' if 'Volume' in keep_cols else ''})")
        elif "Close" in df.columns:
            for col in ["Open","High","Low"]:
                df[col] = df["Close"]
            data[asset] = df[["Open","High","Low","Close"]].copy()
            console.log(f"  {asset} → {len(df)} bars (close-only, synthesised)")
        else:
            console.log(f"[yellow]  No usable columns for {asset}[/yellow]")
    return data


def _bar_map_from_row(df: pd.DataFrame, ts: pd.Timestamp) -> Optional[dict]:
    if ts not in df.index:
        return None
    row = df.loc[ts]
    # df.loc[ts] returns a DataFrame when duplicate timestamps survive dedup;
    # squeeze to a Series so float() conversions are always scalar.
    if isinstance(row, pd.DataFrame):
        row = row.iloc[0]
    return {"open":   float(row["Open"]),  "high":  float(row["High"]),
            "low":    float(row["Low"]),   "close": float(row["Close"]),
            "volume": float(row["Volume"]) if "Volume" in row.index else 0.0}


def _reset_model_counters(model: MultiAssetTradingModel):
    model.performance   = {k: (0 if isinstance(v, int) else 0.0)
                           for k, v in model.performance.items()}
    model.class_perf    = model._new_class_perf()
    model._futures_trades_r = []
    model._all_trades_r     = []
    model._equity_series    = [model.equity]
    model._daily_equity     = [model.equity]
    model.peak_equity    = model.equity
    model.max_dd         = 0.0
    model.trading_halted = False


def _print_results(model: MultiAssetTradingModel, label: str = "Backtest Results"):
    p         = model.performance
    exits     = p["exits"]
    wins      = p["wins"]
    losses    = p["losses"]
    total_r   = p["total_r"]
    total_pnl = p["total_pnl"]
    winrate   = safe_div(wins, exits) * 100
    avg_r     = safe_div(total_r, exits)
    roi       = safe_div(total_pnl, INITIAL_CAPITAL) * 100

    # Profit factor guard: only compute when there are enough trades
    pf        = safe_div(p["win_r_sum"], p["loss_r_sum"]) if exits >= 10 else float("nan")
    avg_win   = safe_div(p["win_r_sum"],  wins)
    avg_loss  = safe_div(p["loss_r_sum"], losses)

    # BUG FIX (v13.5): use the *daily MTM* equity series so the Sharpe annualiser
    # (sqrt 252) matches the actual observation frequency (one value per bar/day).
    # The old _equity_series recorded one point per *trade exit*, so sqrt(252)
    # over-stated Sharpe by ~3× for a strategy with ≈29 trades/year.
    daily_arr = np.array(model._daily_equity)
    daily_rets = np.diff(daily_arr) / np.maximum(daily_arr[:-1], 1.0)
    sharpe    = sharpe_ratio(daily_rets)
    sortino   = sortino_ratio(daily_rets)

    # BUG FIX (v13.5): Calmar uses annualised CAGR, not total return over the
    # full period.  Derive n_years from the length of the daily series.
    n_years  = max(len(model._daily_equity) - 1, 1) / float(TRADING_DAYS_PER_YEAR)
    calmar   = annualised_calmar(roi / 100, model.max_dd, n_years)

    t = Table(title=label)
    t.add_column("Metric", style="cyan")
    t.add_column("Value",  justify="right", style="green")
    for lbl, val in [
        ("Trades",        str(exits)),
        ("Wins / Losses", f"{wins} / {losses}"),
        ("Win Rate",      f"{winrate:.1f}%"),
        ("Profit Factor", f"{pf:.2f}" if not np.isnan(pf) else "n/a"),
        ("Avg Win R",     f"{avg_win:+.2f}"),
        ("Avg Loss R",    f"{avg_loss:.2f}"),
        ("Max Win R",     f"{p['max_win_r']:+.2f}"),
        ("Max Loss R",    f"{p['max_loss_r']:.2f}"),
        ("Total R",       f"{total_r:+.2f}"),
        ("Avg R/Trade",   f"{avg_r:+.2f}"),
        ("Total PnL",     f"${total_pnl:+,.0f}"),
        ("ROI",           f"{roi:+.1f}%"),
        ("Final Equity",  f"${model.equity:,.0f}"),
        ("Max Drawdown",  f"{model.max_dd * 100:.1f}%"),
        ("Sharpe Ratio",       f"{sharpe:.2f}"),
        ("Sortino Ratio",      f"{sortino:.2f}"),
        ("Calmar (annualised)", f"{calmar:.2f}"),
        ("Halted",             "YES" if model.trading_halted else "NO"),
    ]:
        t.add_row(lbl, val)
    console.print(t)

    ct = Table(title="Per-Class Breakdown")
    ct.add_column("Class",   style="cyan")
    ct.add_column("Entries", justify="right")
    ct.add_column("Exits",   justify="right")
    ct.add_column("Wins",    justify="right")
    ct.add_column("Win%",    justify="right")
    ct.add_column("PF",      justify="right")
    ct.add_column("Risk×",   justify="right")
    ct.add_column("Total R", justify="right")
    ct.add_column("PnL",     justify="right")
    for cls, cp in model.class_perf.items():
        wr     = safe_div(cp["wins"], cp["exits"]) * 100
        pf_cls = safe_div(cp["win_r_sum"], cp["loss_r_sum"],
                          default=float("inf") if cp["win_r_sum"] > 0 else 0.0)
        ct.add_row(
            cls, str(cp["entries"]), str(cp["exits"]), str(cp["wins"]),
            f"{wr:.1f}%",
            f"{pf_cls:.2f}" if np.isfinite(pf_cls) else "∞",
            f"{model.class_risk_scalar(cls):.2f}×",
            f"{cp['total_r']:+.2f}",
            f"${cp['total_pnl']:+,.0f}",
        )
    console.print(ct)


class InstitutionalRepairModel(AdaptiveMultiAssetTradingModel):
    VERSION = "v11.2 Institutional Repair"
    MIN_EXPECTANCY_BUCKET_TRADES = 12
    EXPECTANCY_SHRINKAGE = 8.0
    PORTFOLIO_MAX_NEW_TRADES = 2
    MIN_SCORE_BY_CLASS = {"crypto": 1.06, "equity": 1.10, "future": 1.00}
    MIN_ABS_EQUITY_SCORE = 0.020
    MIN_STRUCTURAL_R_BY_CLASS = {"crypto": 1.15, "equity": 1.05, "future": 0.95}
    MIN_STRUCTURAL_R_BY_SETUP = {
        "LONG_BREAKOUT": 1.25,
        "SHORT_BREAKDOWN": 1.25,
        "LONG_CONTINUATION": 1.20,
        "SHORT_BREAKDOWN_CONT": 1.20,
        "LONG_PULLBACK": 1.00,
        "SHORT_RALLY": 1.00,
        "LONG_RETEST": 1.00,
        "SHORT_RETEST": 1.00,
        "SHORT_RETRACE": 1.00,
        "LONG_TREND": 1.05,
        "SHORT_TREND": 1.05,
    }

    def current_risk_fraction(self) -> float:
        dd = safe_div(self.peak_equity - self.equity, self.peak_equity)
        if dd > 0.08:
            return MIN_RISK_FRACTION * 0.85
        if dd > 0.04:
            return BASE_RISK_FRACTION * 0.70
        if dd < 0.02:
            return BASE_RISK_FRACTION * 0.95
        return BASE_RISK_FRACTION

    def class_risk_scalar(self, cls: str) -> float:
        cp = self.class_perf[cls]
        exits = cp["exits"]
        if exits < 6:
            return 1.0
        avg_r = safe_div(cp["total_r"], exits)
        pf = (safe_div(cp["win_r_sum"], cp["loss_r_sum"])
              if cp["loss_r_sum"] > 0
              else (float("inf") if cp["win_r_sum"] > 0 else 1.0))
        if exits >= 12:
            if pf < 0.90 and avg_r < 0.0:
                # v13.4: raised from 0.25 → 0.40.  At 0.25 the combined_scalar in
                # ROIBarbellModel (~0.19 with typical conviction/exp) fell below
                # the 0.20 floor causing futures entries to be completely blocked -
                # a self-sealing death spiral.  At 0.40 the combined_scalar is ~0.30,
                # passing the floor and allowing recovery trades to fire.
                return 0.40
            if pf < 1.00 or avg_r < 0.0:
                return 0.50
            if pf > 1.35 and avg_r > 0.10:
                return 1.10
            return 1.0
        if pf < 0.90 and avg_r < 0.0:
            return 0.55
        return 1.0

    def estimate_structural_expected_r(self, asset: str, side: int, px: float,
                                       atr_val: float, stop_mult: float,
                                       setup: str) -> float:
        o, h, l, c = self._ohlc(asset)
        if len(c) < 55 or atr_val <= 0 or stop_mult <= 0:
            return 0.0
        risk_distance = atr_val * stop_mult
        if risk_distance <= 0:
            return 0.0

        prior_high_20 = float(np.max(h[-21:-1])) if len(h) >= 21 else px
        prior_low_20 = float(np.min(l[-21:-1])) if len(l) >= 21 else px
        prior_high_55 = float(np.max(h[-56:-1])) if len(h) >= 56 else prior_high_20
        prior_low_55 = float(np.min(l[-56:-1])) if len(l) >= 56 else prior_low_20
        range_20 = max(atr_val, prior_high_20 - prior_low_20)
        range_55 = max(range_20, prior_high_55 - prior_low_55)

        if side == 1:
            open_room = max(0.0, prior_high_20 - px, prior_high_55 - px)
        else:
            open_room = max(0.0, px - prior_low_20, px - prior_low_55)

        if any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"]):
            projected_move = max(open_room, 0.90 * range_20, 0.65 * range_55, 2.75 * atr_val)
        else:
            projected_move = max(open_room, 0.65 * range_20, 0.50 * range_55, 2.10 * atr_val)

        structural_r = safe_div(projected_move, risk_distance)
        return float(np.clip(structural_r, 0.0, 4.5))

    def min_structural_r_required(self, asset: str, setup: str) -> float:
        return self.MIN_STRUCTURAL_R_BY_SETUP.get(
            setup,
            self.MIN_STRUCTURAL_R_BY_CLASS.get(ASSET_CLASS[asset], 1.0),
        )

    def candidate_score(self, conviction: float, expectancy_scalar: float,
                        localized_scalar: float, expected_r: float,
                        regime: str, setup: str) -> float:
        regime_bonus = {
            "TREND_UP": 1.06, "TREND_DOWN": 1.06,
            "UPTREND": 1.05, "DOWNTREND": 1.05,
            "TREND": 1.04, "RETEST": 1.02,
            "PULLBACK": 1.00, "CHOP": 0.90,
            "SQUEEZE": 0.94, "PANIC": 0.80,
            "EXPLOSIVE": 0.93,
        }.get(regime, 1.0)
        setup_bonus = 1.03 if any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"]) else 1.00
        reward_bonus = 1.0 + 0.40 * np.tanh(expected_r - 1.0)
        score = conviction * expectancy_scalar * localized_scalar * regime_bonus * setup_bonus * reward_bonus
        return float(score)

    def collect_candidate(self, asset: str, side: int, px: float, atr_val: float,
                          stop_mult: float, setup: str, regime: str,
                          conviction: float, expected_r: float,
                          expectancy_scalar: float, localized_scalar: float,
                          score: float):
        if localized_scalar <= 0:
            return
        cls = ASSET_CLASS[asset]
        if cls == "equity":
            raw_score = self.equity_long_scores.get(asset, 0.0) if side == 1 else self.equity_short_scores.get(asset, 0.0)
            if raw_score < self.MIN_ABS_EQUITY_SCORE:
                return

        structural_r = self.estimate_structural_expected_r(asset, side, px, atr_val, stop_mult, setup)
        if structural_r < self.min_structural_r_required(asset, setup):
            return

        blended_expected_r = max(0.0, 0.75 * structural_r + 0.25 * max(-0.50, expected_r + 0.25))
        score = self.candidate_score(conviction, expectancy_scalar, localized_scalar,
                                     blended_expected_r, regime, setup)
        if score < self.MIN_SCORE_BY_CLASS.get(cls, 1.0):
            return

        self.pending_candidates.append({
            "asset": asset,
            "side": side,
            "price": px,
            "atr_val": atr_val,
            "stop_mult": stop_mult,
            "setup": setup,
            "regime": regime,
            "conviction": conviction,
            "expected_r": blended_expected_r,
            "expectancy_scalar": expectancy_scalar,
            "localized_scalar": localized_scalar,
            "score": score,
        })

    def adaptive_exit_profile(self, pos: Position, default_time_bars: int,
                              default_min_r: float,
                              default_trail_activate: float,
                              default_trail_mult: float) -> Tuple[int, float, float, float]:
        time_bars, min_r_by_time, trail_activate, trail_mult = super().adaptive_exit_profile(
            pos, default_time_bars, default_min_r, default_trail_activate, default_trail_mult
        )
        setup = getattr(pos, "setup_type", "")
        if any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"]):
            trail_activate = max(trail_activate, 1.35)
            trail_mult = max(trail_mult, 2.05)
            min_r_by_time = max(min_r_by_time, 0.45)
        elif any(tag in setup for tag in ["PULLBACK", "RALLY", "RETEST", "RETRACE"]):
            trail_activate = max(trail_activate, 1.00)
            trail_mult = max(trail_mult, 1.75)
            min_r_by_time = max(min_r_by_time, 0.30)
        elif setup in ("LONG_TREND", "SHORT_TREND"):
            # TREND entries: moderate trail to let the trend develop
            trail_activate = max(trail_activate, 1.10)
            trail_mult = max(trail_mult, 1.95)
            min_r_by_time = max(min_r_by_time, 0.35)
        return int(time_bars), float(min_r_by_time), float(trail_activate), float(trail_mult)

    def path_failure_exit(self, pos: Position) -> bool:
        stats = self.expectancy_buckets.get(getattr(pos, "setup_key", ""))
        if not self.ENABLE_ADAPTIVE_EXITS or not stats or stats["trades"] < self.MIN_EXPECTANCY_BUCKET_TRADES:
            return False
        avg_bars = safe_div(stats["sum_bars"], stats["trades"], default=4)
        avg_mfe = safe_div(stats["sum_mfe"], stats["trades"])
        avg_mae = safe_div(stats["sum_mae"], stats["trades"])
        if pos.bars_held < max(3, int(avg_bars * 0.50)):
            return False
        weak_progress = getattr(pos, "trade_mfe_r", 0.0) < max(0.10, avg_mfe * 0.20)
        excessive_adverse = getattr(pos, "trade_mae_r", 0.0) < min(-0.45, avg_mae * 1.25)
        return weak_progress and excessive_adverse and getattr(pos, "peak_r", 0.0) < 0.35



class CoreAlphaRepairModel(InstitutionalRepairModel):
    VERSION = "v11.3 Core Alpha Repair"
    MIN_EXPECTANCY_BUCKET_TRADES = 20
    EXPECTANCY_SHRINKAGE = 20.0
    PORTFOLIO_MAX_NEW_TRADES = 3
    LOCAL_DAMAGE_BLOCK_STREAK = 6
    LOCAL_DAMAGE_SOFT_STREAK = 3
    MIN_SCORE_BY_CLASS = {"crypto": 0.97, "equity": 0.95, "future": 0.93}
    MIN_ABS_EQUITY_SCORE = 0.008

    def _setup_family(self, setup: str) -> str:
        setup = (setup or "UNKNOWN").upper()
        if any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"]):
            return "BREAKOUT"
        if any(tag in setup for tag in ["PULLBACK", "RALLY", "RETEST", "RETRACE"]):
            return "PULLBACK"
        if "TREND" in setup:
            return "TREND"
        return setup

    def _bucket_key(self, asset: str, setup: str, regime: str, side: int) -> str:
        side_txt = "LONG" if side == 1 else "SHORT"
        cls = ASSET_CLASS[asset]
        family = self._setup_family(setup)
        return f"{cls}|{family}|{side_txt}"

    def _effective_prior_r(self, setup: str) -> float:
        """Returns the Bayesian prior expected-R for the given setup.
        Overridden by ROIBarbellModel to use setup-family-specific priors."""
        return self.EXPECTANCY_PRIOR_R

    def bucket_expectancy(self, asset: str, setup: str, regime: str, side: int) -> Tuple[float, float]:
        stats = self._get_bucket_stats(asset, setup, regime, side)
        n = stats["trades"]
        prior = self._effective_prior_r(setup)
        if n == 0:
            return 1.0, prior

        avg_r = safe_div(stats["total_r"], n)
        winrate = safe_div(stats["wins"], n)
        avg_mfe = safe_div(stats["sum_mfe"], n)
        avg_mae = safe_div(stats["sum_mae"], n)
        shrink = n / (n + self.EXPECTANCY_SHRINKAGE)
        exp_r = (1.0 - shrink) * prior + shrink * avg_r

        scalar = 1.0 + 0.25 * np.tanh(exp_r / 1.25)
        scalar += 0.05 * (winrate - 0.50)
        scalar += 0.04 * np.tanh(max(0.0, avg_mfe) - abs(min(0.0, avg_mae)))
        if n >= self.MIN_EXPECTANCY_BUCKET_TRADES and stats["cold_streak"] >= self.LOCAL_DAMAGE_SOFT_STREAK:
            scalar -= 0.08
        scalar = float(np.clip(scalar, 0.80, 1.20))
        return scalar, float(exp_r)

    def localized_damage_scalar(self, asset: str, setup: str) -> float:
        stats = self._get_asset_setup_stats(asset, setup)
        n = stats["trades"]
        if n < 5:
            return 1.0
        recent = list(stats["recent_r"])
        recent_avg = np.mean(recent[-4:]) if recent else 0.0
        if stats["cold_streak"] >= self.LOCAL_DAMAGE_BLOCK_STREAK:
            return 0.70
        if stats["cold_streak"] >= self.LOCAL_DAMAGE_SOFT_STREAK:
            return 0.88
        if n >= self.MIN_EXPECTANCY_BUCKET_TRADES and recent_avg < -0.40:
            return 0.90
        return 1.0

    def _benchmark_excess_returns(self, asset: str, lookback: int) -> float:
        cls = ASSET_CLASS[asset]
        c = self._close(asset)
        if len(c) < lookback + 2:
            return np.nan
        own_ret = np.log(safe_div(c[-1], c[-1 - lookback], default=np.nan))
        if np.isnan(own_ret):
            return np.nan

        if cls == "equity":
            bench = self.benchmark_for_equity(asset)
            bc = self._close(bench)
            if len(bc) < lookback + 2:
                return np.nan
            bench_ret = np.log(safe_div(bc[-1], bc[-1 - lookback], default=np.nan))
            return own_ret - bench_ret

        if cls == "crypto":
            if asset == "BTC-USD":
                return own_ret
            bc = self._close("BTC-USD")
            if len(bc) < lookback + 2:
                return np.nan
            bench_ret = np.log(safe_div(bc[-1], bc[-1 - lookback], default=np.nan))
            return own_ret - bench_ret

        peers = []
        for other in FUTURES_ASSETS:
            if other == asset:
                continue
            oc = self._close(other)
            if len(oc) < lookback + 2:
                continue
            ret = np.log(safe_div(oc[-1], oc[-1 - lookback], default=np.nan))
            if not np.isnan(ret):
                peers.append(ret)
        if not peers:
            return own_ret
        return own_ret - float(np.median(peers))

    def excess_momentum_alpha(self, asset: str, side: int) -> float:
        c = self._close(asset)
        if len(c) < 70:
            return 0.0
        ex21 = self._benchmark_excess_returns(asset, 21)
        ex63 = self._benchmark_excess_returns(asset, 63)
        if np.isnan(ex21) or np.isnan(ex63):
            return 0.0
        rets = np.diff(np.log(c[-41:]))
        vol = np.std(rets, ddof=1) * np.sqrt(20) if len(rets) >= 5 else np.nan
        if np.isnan(vol) or vol <= 1e-6:
            return 0.0
        # Blend 3 horizons when 126-day history is available; the longer
        # horizon rewards assets with *sustained* benchmark outperformance,
        # which is more persistent than short-horizon momentum.
        ex126 = self._benchmark_excess_returns(asset, 126) if len(c) >= 130 else np.nan
        if not np.isnan(ex126):
            signal = (0.40 * ex21 + 0.35 * ex63 + 0.25 * ex126) / vol
        else:
            signal = (0.60 * ex21 + 0.40 * ex63) / vol
        signal *= 1.0 if side == 1 else -1.0
        return float(np.clip(signal, -1.5, 1.5))

    def compression_breakout_alpha(self, asset: str, side: int, setup: str = "") -> float:
        o, h, l, c = self._ohlc(asset)
        if len(c) < 45:
            return 0.0
        range10 = float(np.max(h[-10:]) - np.min(l[-10:]))
        range40 = float(np.max(h[-40:]) - np.min(l[-40:]))
        if range40 <= 0:
            return 0.0
        clv = close_location_value(h[-1], l[-1], c[-1])
        directional_close = clv if side == 1 else (1.0 - clv)
        # For BREAKOUT/BREAKDOWN/CONTINUATION entries the edge comes from range
        # *expansion* (the squeeze is already breaking out).  Penalising range10 >
        # range40 (the original logic) incorrectly discounts the best breakout bars.
        # For all other setups keep the original compression-rewards-contraction rule.
        if any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"]):
            expansion = float(np.clip(range10 / range40 - 1.0, 0.0, 1.0))
            signal = expansion * (2.0 * directional_close - 1.0)
        else:
            compression = 1.0 - np.clip(range10 / range40, 0.0, 1.25)
            signal = compression * (2.0 * directional_close - 1.0)
        return float(np.clip(signal, -1.0, 1.0))

    def trend_quality_alpha(self, asset: str, side: int, px: float, atr_val: float, setup: str) -> float:
        c = self._close(asset)
        if len(c) < 105 or atr_val <= 0:
            return 0.0
        sma20_v = sma(c, 20)[-1]
        sma50_v = sma(c, 50)[-1]
        sma100_v = sma(c, 100)[-1]
        slope20 = sma_slope(c, 20, lookback=5)
        if any(np.isnan([sma20_v, sma50_v, sma100_v])):
            return 0.0
        aligned = 0.0
        if side == 1 and px > sma20_v and sma20_v > sma50_v and sma50_v > sma100_v:
            aligned = 1.0
        elif side == -1 and px < sma20_v and sma20_v < sma50_v and sma50_v < sma100_v:
            aligned = 1.0
        slope_term = np.clip((slope20 * 100.0) * (1.0 if side == 1 else -1.0), -1.0, 1.0)
        extension = abs(px - sma20_v) / atr_val
        extension_penalty = max(0.0, extension - 2.0) * 0.35
        setup_bonus = 0.10 if any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"]) else 0.0
        # Efficiency-ratio bonus: reward clean, directional price action and
        # penalise choppy markets.  ER > 0.45 is trending; ER < 0.25 is noise.
        er = efficiency_ratio(c, 20)
        eff_bonus = 0.0 if np.isnan(er) else float(np.clip((er - 0.35) / 0.15, -1.0, 1.0))
        signal = 0.38 * aligned + 0.38 * slope_term + 0.14 * eff_bonus + setup_bonus - extension_penalty
        return float(np.clip(signal, -1.0, 1.0))

    def core_alpha_score(self, asset: str, side: int, setup: str, px: float, atr_val: float) -> float:
        residual = self.excess_momentum_alpha(asset, side)
        compression = self.compression_breakout_alpha(asset, side, setup)
        trend_quality = self.trend_quality_alpha(asset, side, px, atr_val, setup)
        cls = ASSET_CLASS[asset]
        # Class-specific weighting: crypto is momentum-dominated; equities
        # reward SMA-alignment (trend quality); futures benefit most from
        # compression-then-breakout signals.
        if cls == "crypto":
            alpha = 0.60 * residual + 0.20 * compression + 0.20 * trend_quality
        elif cls == "equity":
            alpha = 0.40 * residual + 0.20 * compression + 0.40 * trend_quality
        else:  # future
            alpha = 0.35 * residual + 0.40 * compression + 0.25 * trend_quality
        if any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"]) and compression > 0:
            alpha += 0.08 * compression
        # TREND setups: reward strong trend_quality signal (SMA alignment is primary)
        if setup in ("LONG_TREND", "SHORT_TREND") and trend_quality > 0:
            alpha += 0.10 * trend_quality
        return float(np.clip(alpha, -1.0, 1.0))

    def candidate_score(self, conviction: float, expectancy_scalar: float,
                        localized_scalar: float, expected_r: float,
                        regime: str, setup: str) -> float:
        regime_bonus = {
            "TREND_UP": 1.04, "TREND_DOWN": 1.04,
            "UPTREND": 1.03, "DOWNTREND": 1.03,
            "TREND": 1.03, "RETEST": 1.01,
            "PULLBACK": 1.00, "CHOP": 0.96,
            "SQUEEZE": 0.99, "PANIC": 0.88,
            "EXPLOSIVE": 0.97,
        }.get(regime, 1.0)
        expectancy_term = 0.88 + 0.12 * expectancy_scalar
        localized_term = 0.85 + 0.15 * localized_scalar
        reward_bonus = 1.0 + 0.15 * np.tanh(expected_r - 0.75)
        setup_bonus = 1.02 if any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"]) else 1.00
        score = conviction * expectancy_term * localized_term * regime_bonus * setup_bonus * reward_bonus
        return float(score)

    def collect_candidate(self, asset: str, side: int, px: float, atr_val: float,
                          stop_mult: float, setup: str, regime: str,
                          conviction: float, expected_r: float,
                          expectancy_scalar: float, localized_scalar: float,
                          score: float):
        cls = ASSET_CLASS[asset]
        if localized_scalar <= 0:
            return
        if cls == "equity":
            raw_score = self.equity_long_scores.get(asset, 0.0) if side == 1 else self.equity_short_scores.get(asset, 0.0)
            if raw_score < self.MIN_ABS_EQUITY_SCORE:
                return

        structural_r = self.estimate_structural_expected_r(asset, side, px, atr_val, stop_mult, setup)
        if structural_r < 0.50:
            return

        alpha_score = self.core_alpha_score(asset, side, setup, px, atr_val)
        if alpha_score < -0.85:
            return

        blended_expected_r = max(0.0, 0.35 * structural_r + 0.65 * max(-0.35, expected_r + 0.15))
        base_score = self.candidate_score(conviction, expectancy_scalar, localized_scalar,
                                          blended_expected_r, regime, setup)
        structural_bonus = 1.0 + 0.12 * np.tanh(structural_r - 1.0)
        alpha_bonus = 1.0 + 0.22 * alpha_score
        score = base_score * structural_bonus * alpha_bonus
        if score < self.MIN_SCORE_BY_CLASS.get(cls, 1.0):
            return

        self.pending_candidates.append({
            "asset": asset,
            "side": side,
            "price": px,
            "atr_val": atr_val,
            "stop_mult": stop_mult,
            "setup": setup,
            "regime": regime,
            "conviction": conviction,
            "expected_r": blended_expected_r,
            "expectancy_scalar": expectancy_scalar,
            "localized_scalar": localized_scalar,
            "score": score,
            "alpha_score": alpha_score,
            "structural_r": structural_r,
        })

    def adaptive_exit_profile(self, pos: Position, default_time_bars: int,
                              default_min_r: float,
                              default_trail_activate: float,
                              default_trail_mult: float) -> Tuple[int, float, float, float]:
        time_bars, min_r_by_time, trail_activate, trail_mult = AdaptiveMultiAssetTradingModel.adaptive_exit_profile(
            self, pos, default_time_bars, default_min_r, default_trail_activate, default_trail_mult
        )
        setup = getattr(pos, "setup_type", "")
        if any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"]):
            time_bars = max(time_bars, default_time_bars + 2)
            min_r_by_time = min(min_r_by_time, max(0.25, default_min_r * 0.85))
            trail_activate = max(trail_activate, 1.60)
            trail_mult = max(trail_mult, 1.80)  # v14.8: tightened from 2.35 → 1.80; locks in 0.76R at trail activation (was 0.53R)
        elif any(tag in setup for tag in ["PULLBACK", "RALLY", "RETEST", "RETRACE"]):
            time_bars = max(time_bars, default_time_bars + 1)
            min_r_by_time = min(min_r_by_time, max(0.20, default_min_r * 0.85))
            trail_activate = max(trail_activate, 0.95)
            trail_mult = max(trail_mult, 1.90)
        elif setup in ("LONG_TREND", "SHORT_TREND"):
            time_bars = max(time_bars, default_time_bars + 2)
            min_r_by_time = min(min_r_by_time, max(0.25, default_min_r * 0.85))
            trail_activate = max(trail_activate, 1.15)
            trail_mult = max(trail_mult, 2.00)
        return int(time_bars), float(min_r_by_time), float(trail_activate), float(trail_mult)

    def path_failure_exit(self, pos: Position) -> bool:
        stats = self.expectancy_buckets.get(getattr(pos, "setup_key", ""))
        if not self.ENABLE_ADAPTIVE_EXITS or not stats or stats["trades"] < max(30, self.MIN_EXPECTANCY_BUCKET_TRADES):
            return False
        avg_bars = safe_div(stats["sum_bars"], stats["trades"], default=4)
        avg_mfe = safe_div(stats["sum_mfe"], stats["trades"])
        avg_mae = safe_div(stats["sum_mae"], stats["trades"])
        if pos.bars_held < max(4, int(avg_bars * 0.60)):
            return False
        weak_progress = getattr(pos, "trade_mfe_r", 0.0) < max(0.15, avg_mfe * 0.18)
        excessive_adverse = getattr(pos, "trade_mae_r", 0.0) < min(-0.55, avg_mae * 1.40)
        return weak_progress and excessive_adverse and getattr(pos, "peak_r", 0.0) < 0.20



class ROIBarbellModel(CoreAlphaRepairModel):
    VERSION = "v14.7"
    MIN_EXPECTANCY_BUCKET_TRADES = 12   # v14.7: lowered from 24; at 24 the learning system was inert for months on a cold start
    EXPECTANCY_SHRINKAGE = 28.0
    PORTFOLIO_MAX_NEW_TRADES = 4
    LOCAL_DAMAGE_BLOCK_STREAK = 8
    LOCAL_DAMAGE_SOFT_STREAK = 4
    MIN_SCORE_BY_CLASS = {"crypto": 0.89, "equity": 0.95, "future": 0.93}

    # v14.7: rebalanced — crypto budget reduced, equity/futures raised.
    # Crypto holds only 3 assets and cannot profit in bear markets (shorts off).
    # Equity and futures can generate alpha across a wider range of macro regimes.
    CRYPTO_BUDGET = 0.40  # was 0.60
    EQUITY_BUDGET = 0.30  # was 0.22
    FUTURE_BUDGET = 0.30  # was 0.18

    # v13.3: enable equity continuation entries and tighten breakout confirmation
    # v14.7: ENABLE_EQUITY_SHORTS re-enabled with sustained-downtrend guard (see
    # equity_market_filter_for_side override below).  The v14.4 negative-R was
    # caused by entering shorts after only one bar below SMA100; the 10-of-15-bar
    # persistence check eliminates those whipsaw entries.
    ENABLE_EQUITY_SHORTS           = False   # v14.8: disabled (v14.4/14.5/14.7 all showed consistent negative/flat equity R from short side)
    ENABLE_EQUITY_CONTINUATION    = True   # was False (inherited)
    FUTURE_BREAKOUT_CONFIRM_REQUIRED = 1   # was 2 (inherited); 1 bar is enough with ADX gate

    CRYPTO_BREAKOUT_EXTENSION_LIMIT = 2.85
    CRYPTO_BREAKOUT_TIME_BARS = 15
    CRYPTO_PULLBACK_TIME_BARS = 9
    CRYPTO_BREAKOUT_MIN_R_BY_TIME = 0.25
    CRYPTO_PULLBACK_MIN_R_BY_TIME = 0.35
    CRYPTO_BREAKOUT_TRAIL_ACTIVATE = 1.60  # v14.7: lowered from 2.20; breakouts peaked 1.5–2.0R with no trailing protection; earlier trail prevents full give-back
    CRYPTO_BREAKOUT_TRAIL_MULT = 2.50      # v14.7: tightened from 3.00 to partially offset earlier activation
    CRYPTO_PULLBACK_TRAIL_ACTIVATE = 0.95
    CRYPTO_PULLBACK_TRAIL_MULT = 1.90
    CRYPTO_PYRAMID_TRIGGER_R = 1.35   # raised from 1.25: align with CRYPTO_TRAIL_ACTIVATE_R so add-on only fires once trail is engaged
    CRYPTO_PYRAMID_RISK_ADD = 0.45
    CRYPTO_MAX_PYRAMID_ADDS = 1
    # Partial profit-taking for breakout positions
    BREAKOUT_PARTIAL_PROFIT_R = 1.50
    BREAKOUT_PARTIAL_SCALE    = 0.50

    # Setup-family-specific Bayesian priors for bucket_expectancy.
    # A universal prior of 0.00 under-estimates breakout R and over-estimates pullback R.
    FAMILY_PRIOR_R = {"BREAKOUT": 0.40, "PULLBACK": 0.20, "TREND": 0.30}

    def _effective_prior_r(self, setup: str) -> float:
        return self.FAMILY_PRIOR_R.get(self._setup_family(setup), self.EXPECTANCY_PRIOR_R)

    def equity_market_filter_for_side(self, asset: str, side: int) -> bool:
        """Overrides the base method with a sustained-downtrend persistence check for
        equity short entries (v14.7 fix).

        For long entries: delegates to the base method (sector benchmark + SPY check).

        For short entries: additionally requires the benchmark close to have been below
        its SMA100 for at least 10 of the last 15 bars.  This eliminates whipsaw short
        entries where the benchmark briefly dipped below SMA100 (1–2 bars) and
        immediately recovered — the main cause of negative R on the short side in v14.4.
        """
        # Always run the base filter first (sector benchmark + SPY macro check)
        if not super().equity_market_filter_for_side(asset, side):
            return False
        if side != -1:
            return True
        # Shorts: require sustained downtrend — benchmark below SMA100 for ≥ 10 / 15 bars
        benchmark = self.benchmark_for_equity(asset)
        c = self._close(benchmark)
        lookback = 15
        if len(c) < EQUITY_LONG_TREND_SMA + lookback:
            return False
        sma100_arr = sma(c, EQUITY_LONG_TREND_SMA)
        if len(sma100_arr) < lookback:
            return False
        bars_below = sum(
            1 for i in range(-lookback, 0)
            if not np.isnan(sma100_arr[i]) and c[i] < sma100_arr[i]
        )
        return bars_below >= 10

    def __init__(self, live_mode: bool = False):
        super().__init__()
        telemetry_headers = list(self.telemetry.headers)
        trade_headers = list(self.trades.headers)
        self.telemetry = CSVBuffer("telemetry_v11_4_roi.csv", telemetry_headers)
        self.trades = CSVBuffer("trades_v11_4_roi.csv", trade_headers)
        # AI / ML components - all degrade gracefully when deps are absent
        self._event_gate    = MacroEventGate(live_mode=live_mode)
        self._sentiment     = LLMSentimentCache(live_mode=live_mode)
        self._ml_expectancy = MLExpectancyModel()
        # Per-entry feature store for ML training: entry_ts+asset -> features
        self._ml_pending_features: Dict[str, dict] = {}
        self._live_mode = live_mode

    def save_state(self, path: str) -> None:
        """Persist base state + ML training data to *path* (JSON)."""
        super().save_state(path)
        ml_path = path.replace(".json", "_ml.json")
        ml = self._ml_expectancy
        ml_state: dict = {
            "X":                    ml._X,
            "y":                    ml._y,
            "since_last_train":     ml._since_last_train,
            "pending_features":     self._ml_pending_features,
        }
        tmp = ml_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(ml_state, f)
        os.replace(tmp, ml_path)
        # Persist trained LightGBM model if available
        if lgb is not None and ml._model is not None:
            lgb_path = path.replace(".json", "_lgb.txt")
            try:
                ml._model.save_model(lgb_path)
            except Exception as exc:
                console.log(f"[yellow]LightGBM model save failed: {exc}[/yellow]")
        console.log(f"[cyan]ML state saved → {ml_path}[/cyan]")

    def load_state(self, path: str) -> bool:
        """Restore base state + ML training data from *path*."""
        ok = super().load_state(path)
        if not ok:
            return False
        ml_path = path.replace(".json", "_ml.json")
        if os.path.exists(ml_path):
            try:
                with open(ml_path) as f:
                    ml_state = json.load(f)
                ml = self._ml_expectancy
                ml._X                  = ml_state.get("X", [])
                ml._y                  = ml_state.get("y", [])
                ml._since_last_train   = int(ml_state.get("since_last_train", 0))
                self._ml_pending_features = ml_state.get("pending_features", {})
                console.log(
                    f"[cyan]ML state loaded - {len(ml._y)} training samples[/cyan]"
                )
            except Exception as exc:
                console.log(f"[yellow]ML state load failed: {exc}[/yellow]")
        # Reload trained LightGBM model if a saved file exists
        lgb_path = path.replace(".json", "_lgb.txt")
        if lgb is not None and os.path.exists(lgb_path):
            try:
                self._ml_expectancy._model = lgb.Booster(model_file=lgb_path)
                console.log(f"[cyan]LightGBM model restored from {lgb_path}[/cyan]")
            except Exception as exc:
                console.log(f"[yellow]LightGBM model restore failed: {exc}[/yellow]")
        return True

    def custom_class_budget(self, cls: str) -> float:
        return {
            "crypto": self.CRYPTO_BUDGET,
            "equity": self.EQUITY_BUDGET,
            "future": self.FUTURE_BUDGET,
        }.get(cls, CLASS_RISK_BUDGET.get(cls, 0.25))

    def current_risk_fraction(self) -> float:
        dd = safe_div(self.peak_equity - self.equity, self.peak_equity)
        if dd > 0.12:
            return MIN_RISK_FRACTION * 0.90
        if dd > 0.06:
            return BASE_RISK_FRACTION * 0.75
        if dd < 0.02:
            return MAX_RISK_FRACTION * 0.95
        return BASE_RISK_FRACTION * 1.05

    def class_risk_scalar(self, cls: str) -> float:
        if cls != "crypto":
            return super().class_risk_scalar(cls)
        cp = self.class_perf[cls]
        exits = cp["exits"]
        if exits < max(18, CLASS_MIN_EXITS_FOR_SCALING):
            return 1.0
        avg_r = safe_div(cp["total_r"], exits)
        pf = (safe_div(cp["win_r_sum"], cp["loss_r_sum"])
              if cp["loss_r_sum"] > 0
              else (float("inf") if cp["win_r_sum"] > 0 else 1.0))
        if pf < 0.85 and avg_r < -0.10:
            return 0.75
        if pf < 1.00 and avg_r < 0.0:
            return 0.90
        if pf > 1.45 and avg_r > 0.12:
            return 1.20
        return 1.0

    def calculate_position_size(self, asset: str, atr_val: float, stop_mult: float,
                                conviction_scalar: float = 1.0,
                                expectancy_scalar: float = 1.0,
                                localized_scalar: float = 1.0,
                                setup: str = "") -> Tuple[float, float]:
        cls = ASSET_CLASS[asset]
        # Setup-family multiplier: increase risk on high-conviction breakouts,
        # reduce it on lower-probability pullback/mean-reversion entries.
        _family = self._setup_family(setup) if setup else "UNKNOWN"
        _family_mult = {"BREAKOUT": 1.10, "PULLBACK": 0.90}.get(_family, 1.00)
        combined_scalar = (
            self.vol_regime_scalar(asset) *
            self.class_risk_scalar(cls) *
            max(0.35 if cls == "crypto" else 0.20, conviction_scalar) *
            max(0.40 if cls == "crypto" else 0.20, expectancy_scalar) *
            max(0.75 if cls == "crypto" else 0.30, localized_scalar) *
            _family_mult
        )
        if cls == "crypto":
            combined_scalar *= 1.15
        floor = 0.40 if cls == "crypto" else 0.30  # raised from 0.20: prevents economically unviable undersized equity/futures entries
        if combined_scalar < floor:
            return 0.0, 0.0

        risk_frac = self.current_risk_fraction() * combined_scalar
        max_risk = MAX_RISK_FRACTION * (1.20 if cls == "crypto" else 1.00)
        min_risk = MIN_RISK_FRACTION * (0.40 if cls == "crypto" else 0.20)
        risk_frac = min(max_risk, max(min_risk, risk_frac))
        desired_risk = self.equity * risk_frac
        class_remaining = max(
            0.0,
            self.equity * self.custom_class_budget(cls) - self.class_risk_in_use(cls)
        )
        risk_usd = min(desired_risk, class_remaining)
        stop_distance = atr_val * stop_mult
        if risk_usd <= 0 or stop_distance <= 0:
            return 0.0, 0.0

        if cls == "future":
            spec = future_spec(asset)
            per_contract_risk = stop_distance * spec["point_value"]
            per_contract_cost = self.future_round_trip_cost_usd(asset, 1.0)
            total_per_contract = per_contract_risk + per_contract_cost
            contracts = int(np.floor(safe_div(risk_usd, total_per_contract)))
            # v14.7: fallback threshold lowered from 4.0× to 2.0×.  The 4× floor
            # allowed entering at up to 4× intended risk when the sizing scalar
            # was near zero, bypassing risk management.  2× is sufficient for a
            # 1-contract override when model risk is only slightly undersized.
            if contracts <= 0 and risk_usd > 0:
                if per_contract_risk <= risk_usd * 2.0:
                    contracts = 1
            if contracts <= 0:
                return 0.0, 0.0
            sized_risk = contracts * per_contract_risk
            return sized_risk, float(contracts)

        units = safe_div(risk_usd, stop_distance)
        return risk_usd, units

    def candidate_corr_ok(self, asset: str, selected_assets: List[str]) -> bool:
        for other in ALL_ASSETS:
            if other == asset or self.positions[other].side == 0:
                continue
            # v14.1: lower the crypto-crypto limit from 0.97 → 0.85 to enforce
            # genuine intra-class diversification (BTC/ETH/SOL are typically
            # 0.80-0.90 correlated; 0.97 allowed nearly identical positions).
            limit = 0.85 if asset in CRYPTO_ASSETS and other in CRYPTO_ASSETS else self.PORTFOLIO_CORR_LIMIT
            if self.pairwise_abs_corr(asset, other) > limit:
                return False
        for other in selected_assets:
            limit = 0.85 if asset in CRYPTO_ASSETS and other in CRYPTO_ASSETS else self.PORTFOLIO_CORR_LIMIT
            if self.pairwise_abs_corr(asset, other) > limit:
                return False
        return True

    def crypto_conviction_v11(self, asset: str, state: dict, side: int, setup: str) -> float:
        score = 0.95
        rs_long = asset != "BTC-USD" and self.crypto_relative_strength_ok(asset)
        rs_short = asset != "BTC-USD" and self.crypto_relative_strength_short_ok(asset)
        if side == 1 and self.btc_trend == "UP":
            score += 0.12
        elif side == 1 and self.btc_trend == "NEUTRAL" and rs_long:
            score += 0.05
        if side == -1 and self.btc_trend == "DOWN":
            score += 0.12
        if not np.isnan(state.get("efficiency", np.nan)) and state["efficiency"] >= CRYPTO_MIN_ER + 0.10:
            score += 0.08
        if 0.02 <= state.get("atr_pct", 0.0) <= 0.08:
            score += 0.05
        if side == 1 and rs_long:
            score += 0.10
        if side == -1 and rs_short:
            score += 0.08
        if "PULLBACK" in setup or "RETRACE" in setup:
            score += 0.04
        if "BREAK" in setup or "CONTINUATION" in setup:
            score += 0.10
            ext = abs(state.get("extension_atr", 0.0))
            if ext > 2.35:
                score -= 0.04
            elif ext > 1.80:
                score -= 0.02
        if side == 1 and state.get("regime") in ["TREND_UP", "EXPLOSIVE"]:
            score += 0.05
        if state.get("regime") == "PANIC":
            score -= 0.20

        # ── LLM sentiment modifier (live mode only; 0.0 during backtesting) ──
        # Provides a +/-0.08 nudge based on GPT-4o-mini directional sentiment.
        # Capped at ±0.08 so it cannot override any single technical factor.
        _ts = getattr(self, "_current_ts", None)
        if _ts is not None:
            date_str = _ts.strftime("%Y-%m-%d")
            sentiment = self._sentiment.get_sentiment(asset, date_str)
            score += 0.08 * float(sentiment) * float(side)

        return float(np.clip(score, 0.65, 1.45))

    def candidate_score(self, conviction: float, expectancy_scalar: float,
                        localized_scalar: float, expected_r: float,
                        regime: str, setup: str) -> float:
        score = super().candidate_score(conviction, expectancy_scalar, localized_scalar,
                                        expected_r, regime, setup)
        if any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"]):
            score *= 1.05
        if regime in ["TREND_UP", "UPTREND", "TREND_DOWN", "DOWNTREND"]:
            score *= 1.02
        return float(score)

    def collect_candidate(self, asset: str, side: int, px: float, atr_val: float,
                          stop_mult: float, setup: str, regime: str,
                          conviction: float, expected_r: float,
                          expectancy_scalar: float, localized_scalar: float,
                          score: float):
        cls = ASSET_CLASS[asset]
        if localized_scalar <= 0:
            return

        # ── Macro-event gate ─────────────────────────────────────────────────
        # Block all new entries on FOMC / CPI / USDA days to avoid adverse
        # momentum surprises from scheduled macro releases.
        _ts = getattr(self, "_current_ts", None)
        if _ts is not None and self._event_gate.is_event_day(_ts):
            return

        if cls == "equity":
            raw_score = self.equity_long_scores.get(asset, 0.0) if side == 1 else self.equity_short_scores.get(asset, 0.0)
            if raw_score < self.MIN_ABS_EQUITY_SCORE:
                return

        is_breakout = any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"])
        structural_r = self.estimate_structural_expected_r(asset, side, px, atr_val, stop_mult, setup)
        structural_floor = 0.35 if cls == "crypto" and is_breakout else 0.50
        if structural_r < structural_floor:
            return

        alpha_score = self.core_alpha_score(asset, side, setup, px, atr_val)
        alpha_floor = -0.95 if cls == "crypto" else -0.85
        if alpha_score < alpha_floor:
            return

        if cls == "crypto" and is_breakout:
            blended_expected_r = max(0.0, 0.20 * structural_r + 0.80 * max(-0.30, expected_r + 0.20))
        else:
            blended_expected_r = max(0.0, 0.35 * structural_r + 0.65 * max(-0.35, expected_r + 0.15))

        base_score = self.candidate_score(conviction, expectancy_scalar, localized_scalar,
                                          blended_expected_r, regime, setup)
        structural_bonus = 1.0 + (0.10 if cls == "crypto" and is_breakout else 0.12) * np.tanh(structural_r - 1.0)
        alpha_bonus = 1.0 + (0.28 if cls == "crypto" and is_breakout else 0.22) * alpha_score
        roi_bonus = 1.10 if cls == "crypto" and is_breakout else 1.0
        score = base_score * structural_bonus * alpha_bonus * roi_bonus
        if score < self.MIN_SCORE_BY_CLASS.get(cls, 1.0):
            return

        self.pending_candidates.append({
            "asset": asset,
            "side": side,
            "price": px,
            "atr_val": atr_val,
            "stop_mult": stop_mult,
            "setup": setup,
            "regime": regime,
            "conviction": conviction,
            "expected_r": blended_expected_r,
            "expectancy_scalar": expectancy_scalar,
            "localized_scalar": localized_scalar,
            "score": score,
            "alpha_score": alpha_score,
            "structural_r": structural_r,
            # ML feature snapshot for MLExpectancyModel training
            "_ml_features": {
                "conviction":        conviction,
                "expectancy_scalar": expectancy_scalar,
                "localized_scalar":  localized_scalar,
                "alpha_score":       alpha_score,
                "structural_r":      structural_r,
                "side":              side,
                "setup":             setup,
                "regime":            regime,
                "cls":               cls,
            },
        })

    def select_and_execute_candidates(self, ts: str):
        def _priority(cand: dict):
            is_crypto_breakout = cand["asset"] in CRYPTO_ASSETS and any(
                tag in cand["setup"] for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"]
            )
            return (1 if is_crypto_breakout else 0, cand["score"])

        candidates = sorted(self.pending_candidates, key=_priority, reverse=True)
        selected_assets: List[str] = []
        entered = 0
        for cand in candidates:
            if entered >= self.PORTFOLIO_MAX_NEW_TRADES:
                break
            asset = cand["asset"]
            if self.positions[asset].side != 0:
                continue
            if not self.candidate_corr_ok(asset, selected_assets):
                continue
            self.enter_position(
                asset, cand["side"], cand["price"], ts,
                cand["atr_val"], cand["stop_mult"],
                conviction_scalar=cand["conviction"],
                setup_type=cand["setup"], regime=cand["regime"],
                expected_r=cand["expected_r"],
                expectancy_scalar=cand["expectancy_scalar"],
                localized_scalar=cand["localized_scalar"],
                candidate_score=cand["score"],
            )
            if self.positions[asset].side != 0:
                selected_assets.append(asset)
                entered += 1
                # Save ML features keyed by asset for _record_learning to retrieve
                if "_ml_features" in cand:
                    self._ml_pending_features[asset] = cand["_ml_features"]
        self.pending_candidates = []

    def _record_learning(self, asset: str, pos: Position, r_net: float):
        """Extends base learning with MLExpectancyModel training."""
        super()._record_learning(asset, pos, r_net)
        features = self._ml_pending_features.pop(asset, None)
        if features is not None:
            self._ml_expectancy.record_trade(features, r_net)

    def bucket_expectancy(self, asset: str, setup: str, regime: str, side: int) -> Tuple[float, float]:
        """Bayesian scalar blended with ML prediction when model is ready."""
        bayesian_scalar, exp_r = super().bucket_expectancy(asset, setup, regime, side)
        # Build a minimal feature dict for ML prediction using current state
        cls = ASSET_CLASS[asset]
        features = {
            "conviction":        1.0,   # not known here; use neutral
            "expectancy_scalar": bayesian_scalar,
            "localized_scalar":  1.0,
            "alpha_score":       0.0,
            "structural_r":      max(0.0, exp_r),
            "side":              side,
            "setup":             setup,
            "regime":            regime,
            "cls":               cls,
        }
        blended = self._ml_expectancy.predict_scalar(features, bayesian_scalar)
        return blended, exp_r

    def adaptive_exit_profile(self, pos: Position, default_time_bars: int,
                              default_min_r: float,
                              default_trail_activate: float,
                              default_trail_mult: float) -> Tuple[int, float, float, float]:
        time_bars, min_r_by_time, trail_activate, trail_mult = CoreAlphaRepairModel.adaptive_exit_profile(
            self, pos, default_time_bars, default_min_r, default_trail_activate, default_trail_mult
        )
        setup = getattr(pos, "setup_type", "")
        is_crypto = getattr(pos, "setup_key", "").startswith("crypto|")
        if is_crypto and any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"]):
            time_bars = max(time_bars, self.CRYPTO_BREAKOUT_TIME_BARS)
            min_r_by_time = min(min_r_by_time, self.CRYPTO_BREAKOUT_MIN_R_BY_TIME)
            trail_activate = max(trail_activate, self.CRYPTO_BREAKOUT_TRAIL_ACTIVATE)
            trail_mult = max(trail_mult, self.CRYPTO_BREAKOUT_TRAIL_MULT)
        elif is_crypto and any(tag in setup for tag in ["PULLBACK", "RALLY", "RETEST", "RETRACE"]):
            time_bars = max(time_bars, self.CRYPTO_PULLBACK_TIME_BARS)
            min_r_by_time = min(min_r_by_time, self.CRYPTO_PULLBACK_MIN_R_BY_TIME)
            trail_activate = max(trail_activate, self.CRYPTO_PULLBACK_TRAIL_ACTIVATE)
            trail_mult = max(trail_mult, self.CRYPTO_PULLBACK_TRAIL_MULT)
        return int(time_bars), float(min_r_by_time), float(trail_activate), float(trail_mult)

    def path_failure_exit(self, pos: Position) -> bool:
        setup = getattr(pos, "setup_type", "")
        is_crypto = getattr(pos, "setup_key", "").startswith("crypto|")
        if is_crypto and any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"]):
            stats = self.expectancy_buckets.get(getattr(pos, "setup_key", ""))
            if not self.ENABLE_ADAPTIVE_EXITS or not stats or stats["trades"] < max(int(self.MIN_EXPECTANCY_BUCKET_TRADES * 1.25), self.MIN_EXPECTANCY_BUCKET_TRADES):
                return False
            avg_bars = safe_div(stats["sum_bars"], stats["trades"], default=6)
            avg_mfe = safe_div(stats["sum_mfe"], stats["trades"])
            avg_mae = safe_div(stats["sum_mae"], stats["trades"])
            if pos.bars_held < max(5, int(avg_bars * 0.75)):
                return False
            weak_progress = getattr(pos, "trade_mfe_r", 0.0) < max(0.10, avg_mfe * 0.12)
            excessive_adverse = getattr(pos, "trade_mae_r", 0.0) < min(-0.80, avg_mae * 1.60)
            return weak_progress and excessive_adverse and getattr(pos, "peak_r", 0.0) < 0.10
        return CoreAlphaRepairModel.path_failure_exit(self, pos)

    def take_partial_profit(self, asset: str, pos: Position, px: float, ts: str):
        """Exit BREAKOUT_PARTIAL_SCALE fraction of an open position at px.

        Locks in gains early on breakout trades, reducing give-back risk while
        letting the remaining position run with the existing trail stop.  After
        scaling out the stop is moved to breakeven so the trade cannot turn into
        a loss on the remaining units.
        """
        scale = self.BREAKOUT_PARTIAL_SCALE
        exit_units = pos.units * scale
        if exit_units <= 0:
            return
        cls = ASSET_CLASS[asset]
        stop_dist = abs(pos.entry_price - pos.stop_price)
        if stop_dist == 0:
            stop_dist = max(pos.entry_atr, 1e-9)
        if cls == "future":
            spec = future_spec(asset)
            gross_pnl = (px - pos.entry_price) * pos.side * exit_units * spec["point_value"]
            cost_usd = self.future_round_trip_cost_usd(asset, exit_units)
            pnl = gross_pnl - cost_usd
            r_gross = safe_div(gross_pnl, pos.risk_usd * scale)
            r_net = safe_div(pnl, pos.risk_usd * scale)
        else:
            r_gross = safe_div((px - pos.entry_price) * pos.side, stop_dist)
            cost_r = safe_div(2 * self.one_way_cost(asset) * px, stop_dist)
            r_net = r_gross - cost_r
            pnl = r_net * pos.risk_usd * scale

        # BUG FIX (v13.5): Do NOT update exits/wins/losses/total_r/_all_trades_r
        # here.  `exit_position` is called later for the *remaining* units and
        # increments all those counters once for the whole trade.  Updating them
        # here too caused every partial-profit trade to be counted *twice* in
        # trade count, win-rate, Total-R, and Profit Factor.
        # We DO update equity (settled cash) and total_pnl (dollar accounting).
        self.update_equity(pnl)
        self.performance["total_pnl"] += pnl
        self.class_perf[cls]["total_pnl"] += pnl

        # Write a diagnostic CSV row tagged PARTIAL_PROFIT (not counted in stats)
        self.trades.write([
            pos.entry_ts, ts, asset, cls, "LONG" if pos.side == 1 else "SHORT",
            getattr(pos, "setup_type", "UNKNOWN"),
            getattr(pos, "regime", "UNKNOWN"),
            pos.entry_price, px, exit_units, pos.entry_atr, pos.bars_held,
            r_gross, r_net, pnl, pos.risk_usd * scale, getattr(pos, "expected_r", 0.0),
            getattr(pos, "trade_mae_r", 0.0), getattr(pos, "trade_mfe_r", 0.0),
            getattr(pos, "entry_score", 1.0), "PARTIAL_PROFIT"
        ])
        # Reduce position to the remaining fraction
        pos.units    *= (1.0 - scale)
        pos.risk_usd *= (1.0 - scale)
        pos.scaled_out = True
        # Move stop to breakeven so the remainder cannot become a loss
        be = self.breakeven_stop(pos.side, pos.entry_price, stop_dist)
        if pos.side == 1:
            pos.stop_price = max(pos.stop_price, be)
        else:
            pos.stop_price = min(pos.stop_price, be)
        console.log(
            f"[yellow][PARTIAL][/yellow] {asset} scale-out @ {px:.2f} | "
            f"R={r_net:+.2f} | PnL=${pnl:+.0f} | remaining={pos.units:.4f} units"
        )

    def add_on_to_crypto_winner(self, asset: str, pos: Position, px: float, atr_val: float):
        if asset not in CRYPTO_ASSETS or pos.side != 1:
            return
        if getattr(pos, "pyramid_count", 0) >= self.CRYPTO_MAX_PYRAMID_ADDS:
            return
        if getattr(pos, "peak_r", 0.0) < self.CRYPTO_PYRAMID_TRIGGER_R:
            return
        # Only add on if the original entry still carries conviction; prevents
        # stacking into positions that started strong but have since degraded.
        if getattr(pos, "entry_score", 1.0) < 0.85:
            return
        if getattr(pos, "trade_mae_r", 0.0) < -0.75:
            return
        stop_distance = abs(px - pos.stop_price)
        if stop_distance <= 0:
            stop_distance = atr_val * max(1.0, CRYPTO_BASE_STOP_ATR)
        class_remaining = max(
            0.0,
            self.equity * self.custom_class_budget("crypto") - self.class_risk_in_use("crypto")
        )
        extra_risk = min(
            pos.risk_usd * self.CRYPTO_PYRAMID_RISK_ADD,
            class_remaining,
            self.equity * self.current_risk_fraction() * 0.75,
        )
        if extra_risk <= 0:
            return
        add_units = safe_div(extra_risk, stop_distance)
        if add_units <= 0:
            return
        old_units = pos.units
        new_units = old_units + add_units
        new_entry_price = safe_div(pos.entry_price * old_units + px * add_units, new_units, default=px)
        # Keep the stop_price consistent with the new blended entry so risk
        # accounting remains accurate after the add-on.
        stop_mult_used = safe_div(abs(pos.entry_price - pos.stop_price), pos.entry_atr,
                                  default=CRYPTO_BASE_STOP_ATR)
        pos.entry_price = new_entry_price
        pos.stop_price  = new_entry_price - pos.side * (pos.entry_atr * stop_mult_used)
        pos.units = new_units
        pos.risk_usd += extra_risk
        pos.pyramid_count = getattr(pos, "pyramid_count", 0) + 1
        pos.entry_score = max(getattr(pos, "entry_score", 1.0), getattr(pos, "entry_score", 1.0) + 0.05)
        console.log(
            f"[cyan][ADD][/cyan] {asset} add-on @ {px:.2f} | +risk=${extra_risk:.0f} | units={pos.units:.4f}"
        )

    def handle_crypto(self, asset: str, ts: str):
        o, h, l, c = self._ohlc(asset)
        if len(c) < CRYPTO_TREND_EMA + 10:
            return

        bar_open = o[-1]
        bar_high = h[-1]
        bar_low = l[-1]
        px = c[-1]
        pos = self.positions[asset]
        state = self.detect_crypto_state(asset)
        self.curr_regime[asset] = state["regime"]
        self.curr_setup[asset] = "-"
        self.curr_signal[asset] = "-"

        if np.isnan(state["atr_val"]) or state["atr_val"] == 0:
            return

        if pos.cooldown > 0:
            pos.cooldown -= 1

        if pos.side != 0:
            pos.bars_held += 1
            pos.highest_price = max(pos.highest_price, bar_high)
            pos.lowest_price = min(pos.lowest_price, bar_low)
            self.update_trade_path(asset, pos, bar_high, bar_low)

            r_net = self.current_trade_r(asset, pos, px, cost_adjusted=True)
            pos.peak_r = max(pos.peak_r, r_net)

            setup = getattr(pos, "setup_type", "LONG_BREAKOUT")
            is_breakout = any(tag in setup for tag in ["BREAKOUT", "BREAKDOWN", "CONTINUATION"])
            if is_breakout and pos.side == 1:
                # Lock in half the position at BREAKOUT_PARTIAL_PROFIT_R before
                # the pyramid add so sizing math stays consistent.
                if not pos.scaled_out and pos.peak_r >= self.BREAKOUT_PARTIAL_PROFIT_R:
                    self.take_partial_profit(asset, pos, px, ts)
                if pos.side != 0 and pos.units > 0:
                    self.add_on_to_crypto_winner(asset, pos, px, state["atr_val"])

            default_time = self.CRYPTO_BREAKOUT_TIME_BARS if is_breakout else self.CRYPTO_PULLBACK_TIME_BARS
            default_min_r = self.CRYPTO_BREAKOUT_MIN_R_BY_TIME if is_breakout else self.CRYPTO_PULLBACK_MIN_R_BY_TIME
            default_trail_activate = self.CRYPTO_BREAKOUT_TRAIL_ACTIVATE if is_breakout else self.CRYPTO_PULLBACK_TRAIL_ACTIVATE
            default_trail_mult = self.CRYPTO_BREAKOUT_TRAIL_MULT if is_breakout else self.CRYPTO_PULLBACK_TRAIL_MULT
            time_bars, min_r_by_time, trail_activate_r, trail_mult = self.adaptive_exit_profile(
                pos, default_time, default_min_r, default_trail_activate, default_trail_mult
            )

            if r_net >= trail_activate_r:
                pos.trail_active = True

            current_stop = pos.stop_price
            if pos.peak_r >= CRYPTO_BREAKEVEN_R:
                _be_dist_roi = pos.initial_stop_dist if pos.initial_stop_dist > 0 else abs(pos.entry_price - pos.stop_price)
                be = self.breakeven_stop(pos.side, pos.entry_price, _be_dist_roi)
                current_stop = max(current_stop, be) if pos.side == 1 else min(current_stop, be)
            if pos.trail_active:
                if pos.side == 1:
                    current_stop = max(current_stop, pos.highest_price - state["atr_val"] * trail_mult)
                else:
                    current_stop = min(current_stop, pos.lowest_price + state["atr_val"] * trail_mult)

            stop_fill = self.generalized_stop_fill_price(pos.side, current_stop, bar_open, bar_high, bar_low)
            exit_reason = None
            if stop_fill is not None:
                self.exit_position(asset, stop_fill, ts, "TRAIL_STOP" if pos.trail_active else "STOP_LOSS")
                return
            if self.path_failure_exit(pos):
                exit_reason = "PATH_FAIL"
            elif r_net <= -CRYPTO_EMERGENCY_STOP_R:
                exit_reason = "EMERGENCY"
            elif pos.bars_held >= time_bars and pos.peak_r < min_r_by_time:
                exit_reason = "TIME_STOP"
            elif pos.side == 1 and state["regime"] == "TREND_DOWN" and pos.bars_held > 5 and pos.peak_r < 1.00:
                exit_reason = "REGIME_FLIP"
            elif pos.side == -1 and state["regime"] == "TREND_UP" and pos.bars_held > 5 and pos.peak_r < 1.00:
                exit_reason = "REGIME_FLIP"

            if exit_reason:
                self.exit_position(asset, px, ts, exit_reason)
                return

        if self.positions[asset].side == 0:
            if state["regime"] == "PANIC":
                return

            side = 0
            setup = None
            if state["long_breakout"]:
                side = 1; setup = "LONG_BREAKOUT"
            elif state["long_pullback"]:
                side = 1; setup = "LONG_PULLBACK"
            elif self.ENABLE_CRYPTO_SHORTS and state["short_breakdown"]:
                side = -1; setup = "SHORT_BREAKDOWN"
            elif self.ENABLE_CRYPTO_SHORTS and state["short_retrace"]:
                side = -1; setup = "SHORT_RETRACE"

            if side == 0 or setup is None:
                return

            if side == 1:
                if REQUIRE_BTC_FILTER and self.btc_trend == "DOWN":
                    return
                if asset != "BTC-USD":
                    rs_ok = self.crypto_relative_strength_ok(asset)
                    if not rs_ok:
                        return
                    # btc_trend == "DOWN" already filtered above; no redundant check needed
                    strong_breakout = (
                        setup == "LONG_BREAKOUT" and
                        state.get("efficiency", 0.0) >= CRYPTO_MIN_ER + 0.08 and
                        state.get("breakout_strength", 0.0) >= CRYPTO_MIN_BREAKOUT_ATR * 1.50
                    )
                    if CRYPTO_ALT_REQUIRE_BTC_UP and self.btc_trend != "UP" and not strong_breakout:
                        return
            else:
                if REQUIRE_BTC_FILTER and self.btc_trend not in ["DOWN", "NEUTRAL"]:
                    return
                if asset != "BTC-USD" and not self.crypto_relative_strength_short_ok(asset):
                    return

            atr_pct = state["atr_pct"]
            if not (CRYPTO_MIN_ATR_PCT <= atr_pct <= CRYPTO_MAX_ATR_PCT):
                return
            if not np.isnan(state["efficiency"]) and state["efficiency"] < CRYPTO_MIN_ER:
                return
            # Volume confirmation: breakouts should occur on above-average volume
            if setup in ("LONG_BREAKOUT", "SHORT_BREAKDOWN") and not self.vol_breakout_ok(asset):
                return

            long_ext_limit = self.CRYPTO_BREAKOUT_EXTENSION_LIMIT if setup == "LONG_BREAKOUT" else CRYPTO_MAX_EXTENSION_ATR
            short_ext_limit = self.CRYPTO_BREAKOUT_EXTENSION_LIMIT if setup == "SHORT_BREAKDOWN" else CRYPTO_MAX_EXTENSION_ATR
            if side == 1 and state["extension_atr"] > long_ext_limit:
                return
            if side == -1 and (-state["extension_atr"]) > short_ext_limit:
                return

            conviction = self.crypto_conviction_v11(asset, state, side, setup)
            if setup == "LONG_BREAKOUT":
                conviction = min(1.50, conviction + 0.08)
            expectancy_scalar, expected_r = self.bucket_expectancy(asset, setup, state["regime"], side)
            localized_scalar = self.localized_damage_scalar(asset, setup)
            score = self.candidate_score(conviction, expectancy_scalar, localized_scalar, expected_r,
                                         state["regime"], setup)
            stop_mult = self.crypto_stop_mult(state["trend_strength"])
            if setup == "LONG_BREAKOUT":
                stop_mult = min(CRYPTO_MAX_STOP_ATR, stop_mult + 0.35)
            self.curr_setup[asset] = setup
            self.curr_signal[asset] = setup.replace("LONG_", "L_").replace("SHORT_", "S_")
            self.collect_candidate(asset, side, px, state["atr_val"], stop_mult, setup, state["regime"],
                                   conviction, expected_r, expectancy_scalar, localized_scalar, score)

def run_backtest(start: str, end: str, wf_splits: int = 0,
                 run_mc: bool = True, mc_seed: int = 42,
                 mc_sims: int = MC_SIMULATIONS,
                 run_stress: bool = True,
                 state_file: str = _MODEL_STATE_FILE):
    console.rule("[bold yellow]Multi-Asset Backtest v14.1[/bold yellow]")

    data = load_backtest_data(start, end)
    if not data:
        console.log("[red]No data loaded - aborting[/red]")
        return

    all_ts = sorted(set().union(*(df.index for df in data.values())))
    console.log(f"Simulating {len(all_ts)} bars "
                f"({all_ts[0].date()} → {all_ts[-1].date()})...")

    def _feed(model: MultiAssetTradingModel,
              timestamps: List[pd.Timestamp],
              progress: bool = False):
        for i, ts in enumerate(timestamps):
            bar_map = {a: bm for a in data
                       if (bm := _bar_map_from_row(data[a], ts)) is not None}
            if bar_map:
                model.process_bar(ts, bar_map)
            if progress and i > 0 and i % 250 == 0:
                console.log(f"  {i}/{len(timestamps)} bars…")

    if wf_splits > 1:
        chunk = len(all_ts) // wf_splits
        rows  = []
        for split in range(wf_splits):
            s        = split * chunk
            e        = s + chunk if split < wf_splits - 1 else len(all_ts)
            chunk_ts = all_ts[s:e]
            warmup   = all_ts[max(0, s - MAX_HISTORY):s]
            wf_model = ROIBarbellModel()
            if warmup:
                _feed(wf_model, warmup)
            _reset_model_counters(wf_model)
            _feed(wf_model, chunk_ts)
            wf_model.telemetry.flush(); wf_model.trades.flush()
            p   = wf_model.performance
            roi = safe_div(p["total_pnl"], INITIAL_CAPITAL) * 100
            # Use daily MTM series for accurate Sharpe / Calmar (v13.5 fix)
            daily_arr  = np.array(wf_model._daily_equity)
            daily_rets = np.diff(daily_arr) / np.maximum(daily_arr[:-1], 1.0)
            chunk_days = max((chunk_ts[-1] - chunk_ts[0]).days, 1)
            chunk_years = chunk_days / 365.25
            rows.append({
                "label":   f"Split {split+1}/{wf_splits} ({chunk_ts[0].date()}→{chunk_ts[-1].date()})",
                "trades":  p["exits"], "wins": p["wins"],
                "total_r": p["total_r"], "pnl": p["total_pnl"],
                "roi": roi, "max_dd": wf_model.max_dd,
                "sharpe": sharpe_ratio(daily_rets),
                "sortino": sortino_ratio(daily_rets),
                "calmar": annualised_calmar(roi / 100, wf_model.max_dd, chunk_years),
            })
        wft = Table(title="Walk-Forward Results")
        for col in ["Period","Trades","Wins","Total R","PnL","ROI","MaxDD","Sharpe","Sortino","Calmar"]:
            wft.add_column(col, justify="right" if col != "Period" else "left")
        for r in rows:
            wft.add_row(r["label"], str(r["trades"]), str(r["wins"]),
                        f"{r['total_r']:+.2f}", f"${r['pnl']:+,.0f}",
                        f"{r['roi']:+.1f}%", f"{r['max_dd']*100:.1f}%",
                        f"{r['sharpe']:.2f}", f"{r['sortino']:.2f}", f"{r['calmar']:.2f}")
        console.print(wft)
        return

    model = ROIBarbellModel()
    _feed(model, all_ts, progress=True)
    model.telemetry.flush(); model.trades.flush()
    _print_results(model)

    # Persist ML training samples so the live feed can load them on startup.
    model.save_state(state_file)
    console.log(
        f"[cyan]Backtest complete - {len(model._ml_expectancy._y)} ML samples "
        f"saved to {state_file}[/cyan]"
    )

    if run_stress:
        console.rule("[bold magenta]Stress Report[/bold magenta]")
        run_trade_stress_report(model._all_trades_r)

    if run_mc:
        console.rule("[bold cyan]Monte Carlo - Futures[/bold cyan]")
        run_monte_carlo(model._futures_trades_r, n_sims=mc_sims, seed=mc_seed)


# =========================================================
# LIVE POLLING
# =========================================================

async def fetch_latest_ohlc(asset: str) -> Optional[Tuple[pd.Timestamp, dict]]:
    """Fetch the most-recently *closed* daily bar for *asset*.

    Delegates to ``DataProvider.get_latest_bar`` which maintains an
    append-only parquet cache per asset.  The network is only hit when the
    cached bar is older than yesterday UTC, reducing per-poll-cycle HTTP
    requests from 16 to 0 on most cycles.
    """
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, _data_provider.get_latest_bar, asset)
    except Exception as exc:
        console.log(f"[yellow]Live fetch error {asset}: {exc}[/yellow]")
        return None
    return result


async def preload_live_history(model: MultiAssetTradingModel):
    """Preload OHLC history for all assets using a single batched fetch."""
    now_utc = pd.Timestamp.now("UTC")
    end     = now_utc
    start   = end - pd.Timedelta(days=MAX_HISTORY + 30)
    start_s = start.strftime("%Y-%m-%d")
    end_s   = end.strftime("%Y-%m-%d")

    loop = asyncio.get_event_loop()
    # Run the (partially blocking) batch fetch in a thread executor so we
    # don't block the async event loop; DataProvider handles async Binance
    # internally.
    try:
        raw = await loop.run_in_executor(
            None, _data_provider.get_history_batch,
            ALL_ASSETS, start_s, end_s, DATA_INTERVAL,
        )
    except Exception as exc:
        console.log(f"[yellow]Preload batch error: {exc}[/yellow]")
        raw = {}

    for asset, df in raw.items():
        try:
            if df.empty:
                continue
            df = df[~df.index.duplicated(keep="last")]
            have_ohlc = all(c in df.columns for c in ["Open","High","Low","Close"])
            df_slice = df.iloc[-MAX_HISTORY:]
            for i in range(len(df_slice)):
                row = df_slice.iloc[i]
                vol = float(row["Volume"]) if "Volume" in row.index else 0.0
                bar = (OHLCBar(float(row["Open"]), float(row["High"]),
                               float(row["Low"]),  float(row["Close"]), vol)
                       if have_ohlc else
                       OHLCBar(*([float(row["Close"])] * 4)))
                model.ohlc_history[asset].append(bar)
            # Use the last *closed* bar for the displayed price (mirrors
            # get_latest_bar which discards any still-forming intraday bar).
            today_utc = pd.Timestamp.now("UTC").normalize()
            df_closed = df[df.index < today_utc]
            if df_closed.empty:
                df_closed = df
            model.latest_price[asset] = float(df_closed["Close"].iat[-1])
            model.refresh_asset_snapshot(asset)
        except Exception as exc:
            console.log(f"[yellow]Preload error {asset}: {exc}[/yellow]")

    model.btc_trend = model.get_btc_trend()


async def run_live_polling(
    poll_seconds: int = 900,
    state_file: str = _MODEL_STATE_FILE,
    broker: Optional[AlpacaBroker] = None,
):
    """Main live-trading loop.

    Changes vs. original:
    * ``live_mode=True`` so LLM / macro gate activate.
    * State loaded from disk on startup; saved after every processed bar.
    * Broker orders submitted on every entry/exit when *broker* is provided.
    * Account equity synced from broker before each bar to keep sizing accurate.
    * Positions reconciled against broker on startup.
    * All 16 asset fetches run in parallel via asyncio.gather + run_in_executor.
    * Incomplete (still-forming) daily bars are automatically skipped.
    """
    model = ROIBarbellModel(live_mode=True)

    # Restore persisted state (positions, equity, ML data) if available
    model.load_state(state_file)

    # Preload price history for indicators (runs in parallel)
    await preload_live_history(model)

    # Attach broker and reconcile positions
    if broker is not None:
        model._broker = broker
        # Sync equity from real account balance
        live_equity = broker.get_account_equity()
        if live_equity > 0:
            console.log(f"[cyan]Broker equity synced: ${live_equity:,.0f}[/cyan]")
            model.equity      = live_equity
            model.peak_equity = max(model.peak_equity, live_equity)
        broker.reconcile_positions(model)

    last_processed_date: Optional[str] = None

    with Live(model.update_dashboard(), refresh_per_second=2, console=console) as live:
        while True:
            loop_start = time.time()

            # Sync account equity once per poll cycle when broker is available
            if broker is not None:
                live_equity = broker.get_account_equity()
                if live_equity > 0:
                    model.equity      = live_equity
                    model.peak_equity = max(model.peak_equity, live_equity)

            # Fetch latest bars for all assets in parallel
            results = await asyncio.gather(
                *(fetch_latest_ohlc(a) for a in ALL_ASSETS),
                return_exceptions=True,
            )
            latest_bars: Dict[str, Tuple[pd.Timestamp, dict]] = {}
            for asset, res in zip(ALL_ASSETS, results):
                if isinstance(res, Exception):
                    console.log(f"[yellow]Live fetch error {asset}: {res}[/yellow]")
                elif res is not None:
                    latest_bars[asset] = res

            if latest_bars:
                newest_ts   = max(ts for ts, _ in latest_bars.values())
                newest_date = newest_ts.strftime("%Y-%m-%d")
                if newest_date != last_processed_date:
                    bar_map = {
                        asset: bar
                        for asset, (ts, bar) in latest_bars.items()
                        if ts.strftime("%Y-%m-%d") == newest_date
                    }
                    model.process_bar(newest_ts, bar_map)
                    model.telemetry.flush()
                    model.trades.flush()
                    last_processed_date = newest_date
                    # Persist state after every processed bar
                    model.save_state(state_file)

            live.update(model.update_dashboard())
            await asyncio.sleep(max(5.0, poll_seconds - (time.time() - loop_start)))


# =========================================================
# OPTUNA HYPERPARAMETER OPTIMISATION
# =========================================================

def _run_optuna(start: str, end: str, n_trials: int = 50,
                metric: str = "sharpe"):
    """Bayesian hyperparameter search via Optuna.

    Searches over a curated subset of ROIBarbellModel hyperparameters,
    running a full backtest for each trial and maximising *metric*.

    Usage::

        python Trading_Model_v11_4_roi_barbell.txt --optimize \\
               --opt-trials 100 --opt-metric sharpe \\
               --start 2021-01-01 --end 2024-12-31

    The best parameters are printed at the end. Evaluation uses a
    deterministic single-pass backtest (no Monte-Carlo, no stress report)
    so each trial completes in seconds.

    Requires: ``pip install optuna``
    """
    if optuna is None:
        console.log("[red]optuna not installed[/red]")
        return

    data = load_backtest_data(start, end)
    if not data:
        console.log("[red]No data for optimisation window[/red]")
        return
    all_ts = sorted(set().union(*(df.index for df in data.values())))

    def _objective(trial: "optuna.Trial") -> float:
        # ── Searchable parameters ─────────────────────────────────────────
        params = {
            "CRYPTO_BUDGET":                trial.suggest_float("CRYPTO_BUDGET",      0.45, 0.70, step=0.05),
            "EQUITY_BUDGET":                trial.suggest_float("EQUITY_BUDGET",       0.15, 0.30, step=0.05),
            "FUTURE_BUDGET":                1.0,   # will be re-derived below
            "CRYPTO_BREAKOUT_TRAIL_ACTIVATE": trial.suggest_float("trail_activate",  1.40, 2.60, step=0.10),
            "CRYPTO_BREAKOUT_TRAIL_MULT":   trial.suggest_float("trail_mult",          2.50, 4.00, step=0.25),
            "CRYPTO_PULLBACK_TRAIL_ACTIVATE": trial.suggest_float("pullback_trail_act", 0.70, 1.30, step=0.10),
            "CRYPTO_PYRAMID_TRIGGER_R":     trial.suggest_float("pyramid_trigger",    0.80, 1.80, step=0.10),
            "CRYPTO_BREAKOUT_TIME_BARS":    trial.suggest_int("breakout_time_bars",    10,   20),
            "CRYPTO_PULLBACK_TIME_BARS":    trial.suggest_int("pullback_time_bars",    6,    14),
            "BREAKOUT_PARTIAL_PROFIT_R":    trial.suggest_float("partial_profit_r",   1.00, 2.00, step=0.25),
        }
        # Ensure budgets sum to 1.0
        future_budget = round(1.0 - params["CRYPTO_BUDGET"] - params["EQUITY_BUDGET"], 2)
        if future_budget < 0.08:
            return float("-inf")
        params["FUTURE_BUDGET"] = future_budget

        # Apply parameters to a fresh model instance
        model = ROIBarbellModel()
        for attr, val in params.items():
            if hasattr(model, attr):
                setattr(model, attr, val)

        for ts in all_ts:
            bar_map = {a: bm for a in data
                       if (bm := _bar_map_from_row(data[a], ts)) is not None}
            if bar_map:
                model.process_bar(ts, bar_map)

        p = model.performance
        exits = p.get("exits", 0)
        if exits < 30:
            return float("-inf")

        if metric == "calmar":
            start_ts = all_ts[0]; end_ts = all_ts[-1]
            years = max(0.1, (end_ts - start_ts).days / 365.25)
            cagr = ((model.equity / INITIAL_CAPITAL) ** (1.0 / years)) - 1.0
            return float(cagr / max(0.001, model.max_dd))
        elif metric == "total_r":
            return float(safe_div(p.get("total_r", 0.0), max(1, exits)))
        elif metric == "sortino":
            daily_arr = np.array(model._daily_equity)
            daily_rets = np.diff(daily_arr) / np.maximum(daily_arr[:-1], 1.0)
            score = sortino_ratio(daily_rets)
            return float(score if np.isfinite(score) else 1e9)
        else:   # sharpe
            returns = np.diff(model._daily_equity)
            if len(returns) < 2 or np.std(returns) == 0:
                return float("-inf")
            return float(np.mean(returns) / np.std(returns) * np.sqrt(252))

    study = optuna.create_study(direction="maximize",
                                sampler=optuna.samplers.TPESampler(seed=42))
    console.log(f"[cyan]Optuna search: {n_trials} trials, metric={metric}[/cyan]")
    study.optimize(_objective, n_trials=n_trials, show_progress_bar=True)

    best = study.best_trial
    console.rule("[bold green]Best Parameters[/bold green]")
    console.print(f"[green]Best {metric}:[/green] {best.value:.4f}")
    for k, v in best.params.items():
        console.print(f"  {k} = {v}")
    # Derive implied future budget
    cb = best.params.get("CRYPTO_BUDGET", 0.60)
    eb = best.params.get("EQUITY_BUDGET", 0.22)
    console.print(f"  FUTURE_BUDGET = {round(1.0 - cb - eb, 2)} (derived)")


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Asset Trading Model v14.1")
    parser.add_argument("--live",             action="store_true")
    parser.add_argument("--start",            default="2021-01-01")
    parser.add_argument("--end",              default=pd.Timestamp.now("UTC").strftime("%Y-%m-%d"))
    parser.add_argument("--poll-seconds",     type=int, default=900)
    parser.add_argument("--wf-splits",        type=int, default=0)
    parser.add_argument("--no-mc",            action="store_true")
    parser.add_argument("--mc-seed",          type=int, default=42)
    parser.add_argument("--mc-sims",          type=int, default=MC_SIMULATIONS)
    parser.add_argument("--no-stress-report", action="store_true")
    # ── Live trading ────────────────────────────────────────────────────────
    parser.add_argument("--state-file",       default=_MODEL_STATE_FILE,
                        help="Path to JSON state file for live mode persistence.")
    parser.add_argument("--alpaca-paper",     action="store_true",
                        help="Enable Alpaca paper-trading execution "
                             "(reads ALPACA_API_KEY / ALPACA_API_SECRET; "
                             "uses https://paper-api.alpaca.markets by default).")
    parser.add_argument("--alpaca-live",      action="store_true",
                        help="Enable Alpaca LIVE-trading execution "
                             "(reads ALPACA_API_KEY / ALPACA_API_SECRET / "
                             "ALPACA_BASE_URL; USE WITH CAUTION).")
    # ── Optuna hyperparameter optimisation ─────────────────────────────────
    parser.add_argument("--optimize",         action="store_true",
                        help="Run Optuna hyperparameter search (requires optuna).")
    parser.add_argument("--opt-trials",       type=int, default=50,
                        help="Number of Optuna trials (default 50).")
    parser.add_argument("--opt-metric",       default="sharpe",
                        choices=["sharpe", "sortino", "calmar", "total_r"],
                        help="Metric to maximise (default: sharpe).")
    args = parser.parse_args()

    if args.live:
        # Build broker if Alpaca credentials are present and a mode flag is given
        _broker: Optional[AlpacaBroker] = None
        if args.alpaca_paper or args.alpaca_live:
            _key    = _ALPACA_API_KEY    or os.environ.get("ALPACA_API_KEY",    "")
            _secret = _ALPACA_API_SECRET or os.environ.get("ALPACA_API_SECRET", "")
            if not _key or not _secret:
                console.log(
                    "[red]Alpaca broker requested but ALPACA_API_KEY / "
                    "ALPACA_API_SECRET are not set - running signal-only mode[/red]"
                )
            else:
                if args.alpaca_live:
                    _base = os.environ.get("ALPACA_BASE_URL", "https://api.alpaca.markets")
                    console.log(
                        "[bold red]⚠️  LIVE TRADING MODE ACTIVE - real orders will be sent![/bold red]"
                    )
                else:
                    _base = os.environ.get("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
                    console.log("[yellow]Paper-trading mode active (Alpaca)[/yellow]")
                _broker = AlpacaBroker(_key, _secret, _base)
        asyncio.run(
            run_live_polling(
                poll_seconds=args.poll_seconds,
                state_file=args.state_file,
                broker=_broker,
            )
        )
    elif args.optimize:
        if optuna is None:
            console.log("[red]optuna is not installed - run: pip install optuna[/red]")
        else:
            _run_optuna(
                start=args.start, end=args.end,
                n_trials=args.opt_trials, metric=args.opt_metric,
            )
    else:
        _backtest_kwargs = {
            "wf_splits": args.wf_splits,
            "run_mc": not args.no_mc,
            "mc_seed": args.mc_seed,
            "mc_sims": args.mc_sims,
            "run_stress": not args.no_stress_report,
            "state_file": args.state_file,
        }
        _sig = inspect.signature(run_backtest)
        _params = list(_sig.parameters.values())
        _supported = set(_sig.parameters)
        _date_kwargs = {}
        _has_start = "start" in _supported
        _has_start_date = "start_date" in _supported
        _has_end = "end" in _supported
        _has_end_date = "end_date" in _supported
        if _has_start and _has_start_date:
            console.log("[yellow]run_backtest supports both start/start_date; using start[/yellow]")
        if _has_end and _has_end_date:
            console.log("[yellow]run_backtest supports both end/end_date; using end[/yellow]")

        if _has_start:
            _date_kwargs["start"] = args.start
        elif _has_start_date:
            _date_kwargs["start_date"] = args.start
        if _has_end:
            _date_kwargs["end"] = args.end
        elif _has_end_date:
            _date_kwargs["end_date"] = args.end

        _positional_only = [p for p in _params if p.kind is inspect.Parameter.POSITIONAL_ONLY]
        _call_args = []
        if len(_positional_only) >= 1:
            _call_args.append(args.start)
        if len(_positional_only) >= 2:
            _call_args.append(args.end)

        _merged_kwargs = {**_backtest_kwargs, **_date_kwargs}
        _consumed_positional_names = {p.name for p in _positional_only[:len(_call_args)]}
        _filtered_kwargs = {
            k: v for k, v in _merged_kwargs.items()
            if k in _supported and k not in _consumed_positional_names
        }
        for _date_name in ("start", "start_date", "end", "end_date"):
            if _date_name in _consumed_positional_names:
                _filtered_kwargs.pop(_date_name, None)
        _dropped = sorted(k for k in _merged_kwargs if k not in _supported)
        if _dropped or _consumed_positional_names:
            _ignored_items = _dropped + sorted(_consumed_positional_names)
            console.log(
                "[yellow]Ignoring unsupported run_backtest kwargs: "
                f"{', '.join(_ignored_items)}[/yellow]"
            )
        run_backtest(*_call_args, **_filtered_kwargs)
