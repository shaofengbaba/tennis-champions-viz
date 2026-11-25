# Three Generations of Tennis Champions
Source: uploaded tennis-atp-data-main.zip, mirror https://github.com/farhadGithub/tennis-atp-data ; Jeff Sackmann, CC BY-NC-SA 4.0. Outputs derived from that source retain the same license. Non-commercial use; credit original author.

Scope: seven specified players, men's singles, records through 2024 only. Original 1968–2024 archive remains unchanged; keep it for all-player prediction. This is not a complete record of every professional-level match (e.g. lower-level events may be absent). Tournament date is event start date, not actual match date. IDs are used for selection. No missing numeric values are imputed. Walkovers excluded from played-match wins/rates; retirements and defaults counted as recorded results, but serve rates use completed matches only. Finals winners count as titles, including recorded walkover finals. Entries represent recorded main-draw appearances, not qualification or withdrawals before any recorded match. Mean age and rank in annual files are match-weighted, not year-end rankings. Age is source tournament age, floored for age aggregation. Peak = largest sum of titles over three calendar years; tied windows retained; active careers censored at 2024. Rows without any recorded tour match have null metrics in matrix; active seasons without Slam entry have zero titles and null Slam win rate. Rates are fractions 0–1. For prediction, do not train on seven-player-only data or use future information.

Files:
- star_matches.csv: unique original matches involving any of seven, with status, date, year, match_id, played, slam, title flags.
- star_slam_matches.csv: Grand Slam subset of star_matches.
- player_matches.csv: one row per selected player per recorded match; a match between two selected players appears twice intentionally.
- player_year.csv: observed player-years; all-event statistics and separate Slam metrics.
- player_year_matrix.csv: complete seven-player x 1986–2024 grid with observation and Slam participation status.
- player_age.csv, slam_player_age.csv: statistics by integer age, all events and Slams respectively.
- slam_entries.csv: one record per observed player-tournament, round reached and title.
- slam_surface.csv: Slam surface performance and title per observed entry.
- rivalry_matches.csv, rivalry_summary.csv: unique direct matches and head-to-head counts by scope, including zero-match pairs in summary; exclude walkovers in summary.
- all_slam_finals.csv: all recorded Slam finals in source, historical context; not independently checked against official champion lists.
- player_summary.csv: career totals, first and last observed title age, peak windows.
- missingness.csv: field-level missingness in unique selected match records.
- audit.txt: execution summary.
- prepare_data.py: reproducible preprocessing; run `python prepare_data.py /path/to/tennis-atp-data-main.zip`.

No predictive model has been fitted. Some historical technical statistics are missing, so use coverage counts when comparing rates. No independent validation against official ATP statistics has been performed.

## V2: linked filtering and missing values
Run `python prepare_data.py path/to/tennis-atp-data-main.zip` and then `python extend_data.py` in this directory to regenerate. Requires pandas and numpy. Source: https://github.com/farhadGithub/tennis-atp-data/tree/main/data/raw (Jeff Sackmann, CC BY-NC-SA 4.0).

- `player_year_matrix.csv`: `cell_state` = no_record / no_slam_entry / zero_titles / positive_titles. Metric-specific `_state` columns distinguish unavailable values from measured zeros. Blank CSV numeric values are null, not zero. The archive establishes observed participation only, not verified absence from the sport.
- `player_year_surface.csv`: group by player, year, surface, scope (all or slam). Never combine both scopes. `all` includes Slam matches. `slam_entries` and `slam_titles` are Slam-specific even for all scope. Carpet is retained for all-scope history.
- `player_year_tournament.csv`: Grand Slam only, joint year/tournament/surface keys. US Open spelling normalized. One row per observed entry. For a selected Slam use this table, not surface-only totals. For filters with no group, left join to matrix: no recorded season vs no observed entry in selected subset. Do not treat null rates as zero.
- Across years, sum wins and played_matches before dividing; sum slam_titles and slam_entries before dividing. For serve rates sum numerator and denominator, and for rank use rank_sum/rank_n. Never average precomputed rates without weights. No denominator means null. Technical counts of zero with zero valid matches are not evidence of zero aces.
- Career curves keep full cumulative totals and highlight selected years; use player_matches / slam_entries for exact age/time details. Age is archived tournament-start age, rounded in source. A 2024 cutoff is not a retirement indicator.
- Rivalry filters use rivalry_matches.csv, played=True, year/surface/slam/tourney_name. No direct recorded meeting is an absent edge, not missing performance.
- Historical benchmark is descriptive; prediction not trained. Seven purposively chosen champions are not a representative sample.
