# Kaladin Decision: Case-sensitive matching for short portfolio tickers

- Recorded: 2026-05-25T15:28:43-07:00
- Requested by: Giakas

## Decision

Match one- and two-character portfolio tickers with case-sensitive boundary regexes, while matching longer tickers with case-insensitive compiled boundary regexes.

## Rationale

Single-character symbols like `A` become noisy if matched case-insensitively because normal prose contains many standalone lowercase words such as `a`. Splitting the regex strategy keeps short ticker hits precise without giving up flexible matching for longer symbols that are more distinctive in article headlines and bodies.

## Consequences

- The pre-filter avoids obvious false positives for short symbols while still returning `matched_tickers` for real uppercase mentions.
- Longer symbols such as `AAPL` still match reliably across headline and body text even when source formatting varies.
