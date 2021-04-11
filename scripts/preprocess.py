from zipfile import ZipFile
from pathlib import Path
from typing import List, Dict
from tabulate import tabulate
from spacy.tokens import DocBin, Doc
from spacy.training import offsets_to_biluo_tags, biluo_tags_to_spans
import random, typer, json, spacy



def unzip(zip_file: Path):
    """Reads the content of a zipped archive containing a .json file
    with the completed Label Studio's annotations.

    Args:
        zip_file: path to zip archive storing a .json file collecting
        Label Studio's completed annotations.

    Returns:
        A list of completed tasks. Each task is encoded as a dictionary
        and represents an annotated Reddit post or comment.

    Raises:
        FileNotFoundError: if the given zip archive path is wrong.
        KeyError: if the .json file stored in the zip archive is
            not named ``result.json``.
    """
    with ZipFile(zip_file, "r") as zip:
        completed_tasks = json.loads(zip.read("result.json"))

    return completed_tasks



def create_spacy_docs(completed_tasks: List[Dict]):
    """Converts a list of completed Label Studio's tasks into a list
    of Spacy Doc objects.

    Args:
        completed_tasks: a list of completed Label Studio's tasks. Each
        task is encoded as a dictionary and represents an annotated Reddit
        post or comment.

    Returns:
        A list of Spacy Doc objects.
    """
    nlp = spacy.blank("en")
    docs = []
    tot_ents = 0
    misaligned = 0

    for task in completed_tasks:
        completions = task["completions"]

        # discard skipped tasks and tasks with multiple completions
        if len(completions) == 1:
            completion = completions[0]
            if "was_cancelled" in completion: continue

            raw_text = task["data"]["reddit"]
            annotated_entities = []

            for result in completion["result"]:
                ent = result["value"]
                # store entity start\end-char index and label as tuple
                entity = (ent["start"], ent["end"], ent["labels"][0])
                annotated_entities.append(entity)

            doc = nlp(raw_text)
            # biluo tags marking doc entities and non-entities
            tags = offsets_to_biluo_tags(doc, annotated_entities)
            # sequence of spans corresponding to doc entities
            entities = biluo_tags_to_spans(doc, tags)
            doc.ents = entities
            docs.append(doc)
            tot_ents += len(annotated_entities)
            misaligned += (len(annotated_entities) - len(doc.ents))

    # print a summary of the conversion result
    print(tabulate({"TOT. ENTITIES": [tot_ents], "TOT. DOCS": [len(docs)],
        "TOT. MISALIGNED ENTITIES": [misaligned]},
        headers="keys", tablefmt="fancy_grid"), sep="\n")

    return docs, tot_ents



def train_test_dev_split(docs: List[Doc], tot_ents: int, out_dir: Path,
    test_size: float, dev_size: float):
    """Splits a list of Spacy Doc objects into three random partitions:
    `train`, `test`, `dev` according to the given sizes (e.g. 0.2 is 20%).

    Each partition is stored as a serialized DocBin .spacy file that can
    be used as input format for specifying a training corpus or for spaCy’s
    CLI train command (https://spacy.io/api/data-formats#training).

    Args:
        docs: a list of Spacy Doc objects encoding Reddit comments and posts.
        tot_ents: total number of entities in docs.
        out_dir: path to output directory storing the three .spacy files.
        test_size: a float representing the amount of data for the test set.
        dev_size: a float representing the amount of data for the dev set.

    Returns:
        None

    Raises:
        ValueError: if there are any empty partitions.
    """
    train_docs, dev_docs, test_docs = [], [], []

    # number of entities per partition
    train_count, dev_count, test_count = 0, 0, 0

    # current entities/tot_ents ratio per partition
    cur_train_ratio, cur_dev_ratio, cur_test_ratio = 0, 0, 0

    random.seed(42)
    random.shuffle(docs)

    for doc in docs:
        num_entities = len(doc.ents)

        if cur_dev_ratio < dev_size:
            dev_docs.append(doc)
            dev_count += num_entities
            cur_dev_ratio = dev_count / tot_ents
        elif cur_test_ratio < test_size:
            test_docs.append(doc)
            test_count += num_entities
            cur_test_ratio = test_count / tot_ents
        else:
            train_docs.append(doc)
            train_count += num_entities
            cur_train_ratio = train_count / tot_ents

    # raise an exception if there are any empty partitions
    if any(len(partition) == 0 for partition in [train_docs, test_docs, dev_docs]):
        raise ValueError("""One or more partitions are empty! """
    f"""train: {len(train_docs)}, test: {len(test_docs)}, dev: {len(dev_docs)}""")

    # print a summary of the data in each partition
    summary = [["train", train_count, len(train_docs), cur_train_ratio*100],
        ["test", test_count, len(test_docs), cur_test_ratio*100],
        ["dev", dev_count, len(dev_docs), cur_dev_ratio*100]]

    print(tabulate(summary, headers=["PARTITION", "ENTS PER PARTITION", "DOCS PER PARTITION", "%"],
        tablefmt="fancy_grid"), sep="\n")

    # create out_dir if not already there
    out_dir.mkdir(exist_ok=True)

    # save partitions as serialized DocBin files
    DocBin(docs=train_docs).to_disk(out_dir / "train.spacy")
    DocBin(docs=dev_docs).to_disk(out_dir / "dev.spacy")
    DocBin(docs=test_docs).to_disk(out_dir / "test.spacy")



def main(zip_file: Path, out_dir: Path, test_size: float, dev_size: float):
    try:
        tasks = unzip(zip_file)
        docs, tot_ents = create_spacy_docs(tasks)
        train_test_dev_split(docs, tot_ents, out_dir, test_size, dev_size)
    except KeyError as ke:
        print(str(ke))
    except ValueError as ve:
        print(str(ve))
    except FileNotFoundError as fe:
        print(str(fe))



if __name__ == "__main__":
    typer.run(main)
