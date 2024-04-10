# track-chair-review-tables
Produce summary tables of the different track reviews for use by the track chairs with decision making

## Getting Data

The Pretalx API is unreliable, so still need to do this somewhat manually

### Proposals

_Proposals -> Export -> CSV/JSON Exports_

#### Export Settings

* Export format: CSV format
* Data delimiter: Newline

#### Dataset

* Target Group: Submitted

#### Data fields

* Proposal title
* Session type
* Track

Save to `data/` dir as `sessions.csv`.

### Review

_Review -> Export reviews -> CSV/JSON Exports_

#### Dataset

* Proposal: All proposals

#### Data fields

* Select All

#### Export Settings

* Export format: CSV format

Save to `data/` dir as `reviews.csv`.

## Running

This project uses [`pixi`](https://pixi.sh/) to control the application.
If you don't have `pixi` installed yet, follow the 1-liner [install command](https://pixi.sh/latest/#installation) for the Rust binary for your operating system.

Then to both install the the full environment from the multi platform lock file (`pixi.lock`) and run the script to generate the output files run

```
pixi run summary
```

## Development

To rebuild the lock file at any point simply

```
rm pixi.lock && pixi install
```

and to get a virtual environment shell, run

```
pixi shell
```
