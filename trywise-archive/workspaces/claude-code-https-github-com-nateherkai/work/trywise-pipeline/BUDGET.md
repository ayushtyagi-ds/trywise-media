# Budget planning (not a spending limit)

`budget_estimate.py` calculates estimated monthly CAD spend from amounts you enter; it does not fetch exchange rates, inspect subscriptions or enforce provider limits. Include any Gemini subscription if it counts against CAD 50, every service, estimated taxes, FX conversion, variable usage and a reserve. Actual bills may exceed the estimate. Don't enable paid billing merely because this tool says the estimate fits.

Example **hypothetical values only**, not a quote:

```
{"ceiling_cad":"50", "cad_per_usd":"1.40", "tax_fraction":"0.05", "reserve_cad":"5", "services":[{"name":"Example service", "currency":"USD", "monthly":"29"}]}
```

Save your own values in a private JSON file and run `python3 budget_estimate.py /path/to/config.json`. It applies the supplied tax fraction to all converted services as a conservative assumption; actual taxes and exchange rates vary. Set provider-side spending controls where available, but confirm whether they enforce a hard limit and whether fees/taxes are covered. This tool cannot guarantee that combined bills remain within CAD 50.
