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
proposals = pd.read_csv(data_dir / "sessions.csv")
submissions = proposals[proposals["Session type"] != "Tutorial"]

track_names = submissions["Track"].unique().tolist()

# %% [markdown]
# and then load up _all_ the reviews and search on the "Proposal ID" to match the submission to the reviews for it for each track. Once the table has been constructed save it as a CSV under `/output` which can then be individually copied and pasted into the relevant Google Sheet.

# %% [markdown]
# The Google Sheet template also expects the columns to be in the following order:
#
# * Proposal ID
# * Proposal title
# * Session type
# * Score
# * Text
# * Score in 'Overall evaluation.'
# * Score in 'Is the proposal interesting to a broad range of people in the SciPy community?'
# * Score in 'Is the proposal Clear?'
# * Score in 'Is the proposal complete?'
# * Score in 'How relevant and immediately useful is the topic?'
# * Score in 'I have read the SciPy Conference Code of Conduct and reviewer guidelines sent to me in my confirmation email'
# * Score in 'If there is a full paper submitted for this abstract, I would like to be a reviewer on it.'
# * created
# * updated
# * Reviewer name
# * Reviewer email
#
# which is not the default order from the export from Pretalx, so rearrange the column names for the final output to match this.

# %%
reviews = pd.read_csv(data_dir / "reviews.csv")

# reorder columns to match example
column_names = reviews.columns.tolist()
column_names = (
    column_names[9:11]
    + ["Session type", "Track"]
    + column_names[0:9]
    + column_names[11:]
)

# %%
# for track_name in track_names:
# c.f. https://github.com/scipy-conference/track-chair-review-tables/issues/2
_tmp_track_names = track_names.copy()
_tmp_track_names.remove("General")
for track_name in _tmp_track_names:
    print(f"Creating review table for track: {track_name}")

    track_review = pd.DataFrame(columns=reviews.keys())

    track_submission_selection = submissions["Track"] == track_name
    track_proposal_ids = submissions[track_submission_selection]["ID"].tolist()

    for proposal_id in track_proposal_ids:
        proposal_selection = reviews["Proposal ID"] == proposal_id
        track_review = pd.concat([track_review, reviews[proposal_selection]])

    # Build a list to append as a column to the final dataframe
    session_types = []
    for proposal_id in track_proposal_ids:
        # First find out the type of submission of the proposal_id
        proposal_id_seclection = submissions["ID"] == proposal_id
        session_type = submissions[proposal_id_seclection]["Session type"].values[0]
        # The reviews for any proposal ID are grouped sequentially, so can
        # add the same number of session types as there are reviews
        track_review_proposal_id_counts = track_review["Proposal ID"].value_counts()
        n_reviews = track_review["Proposal ID"].value_counts()[proposal_id]
        # need to _not_ append but instead _add_ as joining lists
        session_types += [session_type] * n_reviews

    track_review["Session type"] = session_types
    track_review["Track"] = track_name

    # reorder columns for export
    track_review = track_review[column_names]

    # TODO: Clean this up as a regex
    file_name = (
        "review_"
        + track_name.split(",")[0].split("/")[0].split(":")[0].lower().replace(" ", "_")
        + ".csv"
    )
    track_review.to_csv(output_dir / file_name, index=False)

# %% [markdown]
# ## Reviews Summary

# %% [markdown]
# Now create a dashboard panel kind of table for the track chair reviewers to get a quick summary of all the reviews using the tables that were just generated.

# %%
# for review_file in output_dir.glob("review_*.csv"):
column_names = [
    "Proposal ID",
    "Proposal title",
    "Session type",
    "Track",
    "Average score",
    "Status",
    "Number of reviewers",
]

# for review_file in output_dir.glob("review_human_networks.csv"):
for review_file in output_dir.glob("review_*.csv"):
    data = {
        "Proposal ID": [],
        "Proposal title": [],
        "Session type": [],
        "Average score": [],
        "Number of reviewers": [],
    }
    review = pd.read_csv(review_file)

    proposal_ids = review["Proposal ID"].unique()
    for proposal_id in proposal_ids:
        proposal_id_selection = review["Proposal ID"] == proposal_id
        proposal_dataframe = review[proposal_id_selection]

        # Need to get all the scored review questions
        # here being lazy and doing so by column index
        scores = proposal_dataframe.iloc[:, 6:11]
        average_score = scores.sum(axis=1).mean()  # sum across the row and then average

        data["Proposal ID"].append(proposal_id)
        data["Proposal title"].append(proposal_dataframe["Proposal title"].tolist()[0])
        data["Session type"].append(proposal_dataframe["Session type"].tolist()[0])
        data["Average score"].append(average_score)
        data["Number of reviewers"].append(
            len(proposal_dataframe["Reviewer email"].unique())
        )

    review_summary = pd.DataFrame.from_dict(data=data)
    # safe to use zero index as know this exists for entire dataframe
    review_summary["Track"] = review["Track"][0]
    review_summary["Status"] = "Submitted"

    # reorder columns for export
    review_summary = review_summary[column_names]
    # order by average score, but sort by "Session type" first to put talks at top
    review_summary = review_summary.sort_values(
        by=["Session type", "Average score"], ascending=False
    )

    file_name = review_file.name.replace("review", "review-summary")
    review_summary.to_csv(output_dir / file_name, index=False)
