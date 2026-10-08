# Live signals (not built yet)

Reserved for the live signal feed. Planned record shape, matching the strategy data files so the page can reuse the same code:

```json
{
  "strategy": "strategy-slug",
  "timestamp": "2027-01-04T15:00:00Z",
  "publish_after": "2027-01-04T15:00:00Z",
  "holdings": [
    {"ticker": "XXXX", "weight": 0.05, "compliant": true}
  ]
}
```

`publish_after` is the delay control: the site shows a record only once this time has passed. Set it equal to `timestamp` for real-time display.
