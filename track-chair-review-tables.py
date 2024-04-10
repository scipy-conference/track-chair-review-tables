# ---
# jupyter:
#   jupytext:
#     notebook_metadata_filter: all,-jupytext.text_representation.jupytext_version
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.12.2
# ---

# %% [markdown]
# # Generate Review Tables for Track Chairs

# %%
from pathlib import Path
import pandas as pd

# %% [markdown]
# First ensure that all the directories exist that are needed for reading and writing

# %%
cwd = Path().cwd()

output_dir = cwd / "output"
output_dir.mkdir(exist_ok=True)

data_dir = cwd / "data"

# %% [markdown]
# The Proposals table is the only table exported from Pretlax (as of 2024) that provides information on the proposal track _and_ the unique "Proposal ID". So first get all the track names

# %%
proposals = pd.read_csv( data_dir / "sessions.csv")
talks = proposals[proposals["Session type"] == "Talk"]

track_names = talks["Track"].unique().tolist()

# %% [markdown]
# and then load up _all_ the reviews and search on the "Proposal ID" to match the talk to the reviews for it for each track. Once the table has been constructed save it as a CSV under `/output` which can then be individually copied and pasted into the relevant Google Sheet.

# %%
reviews = pd.read_csv( data_dir / "reviews.csv")

# reorder columns to match example
column_names = reviews.columns.tolist()
column_names = column_names[9:11] + column_names[0:9] + column_names[11:]

# %%
for track_name in track_names:
    print(f"Creating review table for track: {track_name}")

    track_review = pd.DataFrame(columns=reviews.keys())
    
    track_talk_selection = talks["Track"] == track_name
    track_proposal_id = talks[track_talk_selection]["ID"].tolist()
    
    for proposal_id in track_proposal_id:
        proposal_selection = reviews["Proposal ID"] == proposal_id
        track_review = pd.concat([track_review, reviews[proposal_selection]])
    
    # reorder columns for export
    track_review = track_review[column_names]
    
    # TODO: Clean this up as a regex
    file_name = "review_" + track_name.split(",")[0].split("/")[0].split(":")[0].lower().replace(" ", "_") + ".csv"
    track_review.to_csv(output_dir / file_name, index=False)
