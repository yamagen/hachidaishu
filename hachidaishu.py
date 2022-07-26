#!/usr/bin/env python

from dataclasses import dataclass, field, fields, astuple, asdict
from typing import List
from enum import Enum
from itertools import groupby
from collections import Counter

from dictionaryconverter import (
    unidic2ud_map,
    chasenid2pos,
    chasenid2pos_en,
    ipadic2unidic,
)

Anthology = Enum(
    "Anthology",
    "Kokinshu Gosenshu Shuishu Goshuishu Kin’yoshu Shikashu Senzaishu Shinkokinshu",
)


@dataclass
class Token:
    token_type: str
    bg_id: str
    chasen_id: str = field(repr=False)
    ipa_pos: str = field(init=False)
    ipa_en_pos: str = field(init=False)
    unidic_pos: str = field(init=False)
    ud_pos: str = field(init=False)
    surface: str
    lemma: str
    lemma_reading: str
    kanji: str
    kanji_reading: str

    def __post_init__(self):
        self.ipa_pos = chasenid2pos[self.chasen_id]
        self.ipa_en_pos = chasenid2pos_en[self.chasen_id]
        self.unidic_pos = ipadic2unidic[self.ipa_pos]
        self.ud_pos = None

    def __repr__(self):
        return f"{self.surface}/{self.unidic_pos}/{self.ud_pos}/{self.lemma}"

    def __iter__(self):
        return iter(astuple(self))

    def to_json(self):
        return asdict(self)


@dataclass
class Decomposition:
    tokens: List[Token]
    decomposition_type: str

    def __iter__(self):
        return iter(astuple(self.tokens))

    def __getitem__(self, index: int) -> Token:
        return self.tokens[index]

    def __iter__(self):
        return iter(astuple(self))


@dataclass
class HachidaishuRecord:
    anthology: Anthology
    poem: int
    serial: int
    segments: List[Decomposition]

    def __iter__(self):
        return iter(astuple(self)[:3] + astuple(self.token()))

    def keys(self):
        return [f.name for f in fields(self)][:3] + [
            f.name for f in fields(self.token())
        ]

    def to_json(self):
        return {
            "anthology": self.anthology.name,
            "poem": self.poem,
        } | self.token().to_json()

    def token(self):
        """Return the canonical decomposition (always one token), ignoring any alternative variants."""
        return self.segments[0][0]

    def decompositions(self):
        """Return a list containing the alternative decompositions of segment record."""
        return self.segments


@dataclass
class HachidaishuDB:
    db: List[HachidaishuRecord] = field(repr=False)

    def __init__(self, filename="hachidai.db"):
        self.db = self._retokenize(self._read_db(filename))

    def __getitem__(self, index):
        return self.db[index]

    def __iter__(self):
        for record in self.db:
            yield record

    def columns(self):
        return self.db[0].keys()

    def _retokenize(self, db):
        records = []
        serial = None
        token_type = None
        for entry in db:
            entry_type = entry.segments[
                0
            ].decomposition_type  # intially, only one decomposition per record
            if (
                serial == entry.serial
            ):  # tokens with same serial are decomposition variants to be added to existing decomposition segment
                prev_decomp = records[-1].segments
                # decomposition variants are grouped by their type (A-E) and can represent groups of tokens themselves
                if (
                    entry_type == token_type
                ):  # add to existing segment in previous token
                    prev_decomp[-1].tokens.extend(entry.segments[0].tokens)
                else:  # add to new segment in previous token
                    prev_decomp.extend(entry.segments)
            else:  # new record
                records.append(entry)

            serial = entry.serial
            token_type = entry_type

        # Map UniDic POS to Universal Dependencies
        for i, e in enumerate(records):
            for decomposition in e.segments:
                for j, token in enumerate(decomposition.tokens):
                    if token.ud_pos:  # UD POS already set, skip to next.
                        continue
                    # Get next token:
                    if j + 1 < len(
                        decomposition.tokens
                    ):  # Next token is within decomposition.
                        e_next = decomposition.tokens[j + 1]
                    else:  # Next token is outside decomposition in next record, and
                        if (
                            i + 1 < len(records) and e.poem == records[i + 1].poem
                        ):  # there is a next token in the same poem.
                            # Here we choose the first token from the possible compositions of the next token to compare against.
                            # TODO This should be against all first tokens of all decomposition in next record!
                            e_next = records[i + 1].segments[0].tokens[0]
                        else:  # there is no next token.
                            e_next = None
                    new_pos, next_new_pos = unidic2ud_map(
                        token.surface,
                        token.unidic_pos,
                        e_next.unidic_pos if e_next else None,
                    )
                    token.ud_pos = new_pos
                    if e_next and next_new_pos:
                        records[i + 1].segments[0].tokens[0].ud_pos = next_new_pos

        return records

    def _read_db(self, filename="hachidai.db"):
        with open(filename) as f:
            for row in f.readlines():
                fields = row.rstrip().split(" ")
                (
                    id,
                    token_type,
                    bg_id,
                    chasen_id,
                    surface,
                    lemma,
                    lemma_reading,
                    kanji,
                    kanji_reading,
                ) = fields
                anthology, poem, serial = id.split(":")
                decomposition_type = token_type[0]
                token = Token(
                    token_type,
                    bg_id,
                    chasen_id,
                    surface,
                    lemma,
                    lemma_reading,
                    kanji,
                    kanji_reading,
                )
                # token is represented as a list of tokens within possible decompositon list
                yield HachidaishuRecord(
                    Anthology(int(anthology)),
                    int(poem),
                    int(serial),
                    [Decomposition([token], decomposition_type)],
                )

    def query(self, anthology=None, poem=None, serial=None):
        for record in self:
            if anthology and record.anthology != Anthology(anthology):
                continue
            if poem and record.poem != poem:
                continue
            if serial and record.serial != serial:
                continue
            yield record

    def tokens(self, mode="default", anthology=None, poem=None, serial=None):
        for record in self.query(anthology, poem, serial):
            if mode == "default":
                yield record.token()
            elif mode == "decomposition":
                for token_seq in record.decompositions():
                    for token in token_seq:
                        yield token

    def text(self, delimiter=" ", anthology=None, poem=None, serial=None):
        by_poem = groupby(
            self.query(anthology=anthology, poem=poem, serial=serial),
            key=lambda r: (r.anthology, r.poem),
        )
        return "\n".join(
            delimiter.join(record.token().surface for record in poem)
            for poem_info, poem in by_poem
        )


if __name__ == "__main__":
    db = HachidaishuDB()
    for e in db:
        for ts in e.segments:
            for t in ts.tokens:
                assert t.ud_pos is not None

    print("Validation complete. Printing the top 20 and bottom 20 tokens.")
    c = Counter((t.surface, t.ud_pos) for t in db.tokens())
    for token, freq in c.most_common(20):
        print(f"{token}: {freq}")
    print()
    for token, freq in c.most_common()[:-21:-1]:
        print(f"{token}: {freq}")

    print("Printing space-delimited corpus.")
    print(db.text())
