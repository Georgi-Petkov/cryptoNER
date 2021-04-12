<!-- SPACY PROJECT DOCS START -->

# 🪐 spaCy Project: CryptoNER

A Named Entity Recognition model for cryptocurrencies. The model is trained on comments and posts collected from the [r/CryptoCurrency](https://www.reddit.com/r/CryptoCurrency/) subreddit. The data is annotated using [Label Studio](https://labelstud.io/) and the output encoded as a `.json` file which is then further processed to obtain Spacy's binary training data.

## 📋 project.yml

The [`project.yml`](project.yml) file defines the data assets required by the
project, as well as the available commands and workflows. For details, see the
[spaCy projects documentation](https://spacy.io/usage/projects).

### ⏯ Commands

The following commands are defined by the project. They
can be executed using [`spacy project run [command_name]`](https://spacy.io/api/cli#project-run).
Commands are only re-run if their inputs have changed.

| Command | Description |
| --- | --- |
| **`preprocess`** | Unzip, convert and split Label Studio annotated data into `train.spacy`, `test.spacy` and `dev.spacy` |
| **`debug`** | Debug spaCy’s config file and binary training data |
| **`train`** | Train the model |
| **`evaluate`** | Evaluate the best model on `test.spacy` and generate a displacy visualization |
| **`clean`** | Remove all files and folders created while running the previous commands |

### ⏭ Workflows

The following workflows are defined by the project. They
can be executed using [`spacy project run [workflow_name]`](https://spacy.io/api/cli#project-run)
and will run the specified commands in order. Commands are only re-run if their
inputs have changed.

| Workflow | Steps |
| --- | --- |
| `all` | `preprocess` &rarr; `debug` &rarr; `train` &rarr; `evaluate` |

## 🗜️ Label Studio utils

The `labelStudio_utils.zip` archive stores data and scripts required to reproduce the annotation step carried out with Label Studio:
- `raw_reddit_data.zip` collects the raw Reddit data to be annotated;
- `create_LabelStudio_tasks.py` is the script used to clean the raw data and turn it into Label Studio tasks;
- `model.py` is a ["dummy model"](https://labelstud.io/tutorials/dummy_model.html#Create-dummy-model-script) returning a label for each recognised entity in a given task. Labels are the result of a naive rule-based matching;
- `crypto_patterns.jsonl` stores the patterns used for the naive rule-based matching performed by `model.py`.
- `CryptoCurrency_tasks.json` stores a set of tasks ready to be imported in Label Studio for annotation.
<!-- SPACY PROJECT DOCS END -->