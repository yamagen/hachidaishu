#!/usr/bin/env python

import re
from collections import Counter
from dataclasses import asdict, astuple, dataclass, field, fields
from enum import Enum
from itertools import groupby
from typing import List

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
    ud_pos: str | None = field(init=False)
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
        records: list[HachidaishuRecord] = []
        serial = None
        token_type = None
        for entry in db:
            entry_type = entry.segments[
                0
            ].decomposition_type  # initially, only one decomposition per record
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

        current_poem = None
        variant_indices: list[tuple[int, int]] = []

        for i, record in enumerate(records):
            if record.poem != current_poem:
                # As possible future work, we could add a check for the number of variant indices
                # and do type-based processing based on that.
                # if len(variant_indices) == 0:
                #     ...
                # elif len(variant_indices) not in [2, 3]:
                #     ...
                if len(variant_indices) in [2, 3]:
                    self._process_variants(records, variant_indices)
                current_poem = record.poem
                variant_indices = []

            for j, token in enumerate(record.segments[0].tokens):
                if token.surface.startswith("＊") or token.surface.startswith("イ"):
                    variant_indices.append((i, j))

        # logger.info(f"records: {len(records)}")
        return records

    def _process_variants(self, records, variant_indices):
        for k in range(len(variant_indices) - 3, -1, -3):
            begin_original, begin_variant, end_variant = variant_indices[k : k + 3]

            variant_count = end_variant[0] - begin_variant[0] - 1

            original_start_index = begin_original[0] + 1
            variant_tokens = records[
                begin_variant[0] + 1 : begin_variant[0] + 1 + variant_count
            ]

            for original_record, variant_record in zip(
                records[original_start_index : original_start_index + variant_count],
                variant_tokens,
            ):
                if original_record.segments and variant_record.segments:
                    for original_segment, variant_segment in zip(
                        original_record.segments, variant_record.segments
                    ):
                        if (
                            original_segment.decomposition_type
                            == variant_segment.decomposition_type
                        ):
                            original_segment.tokens.extend(
                                token
                                for token in variant_segment.tokens
                                if token not in original_segment.tokens
                            )

            # Remove the ＊ and variant tokens at the end
            del records[begin_variant[0] : begin_variant[0] + 2 + variant_count]
            del records[begin_original[0]]

        records[:] = [
            record
            for record in records
            if all(segment.tokens for segment in record.segments)
        ]

    def __process_variants(self, records, variant_indices):
        # FIXME ＊ inidicates:
        # 1. when appearing the first time, the starting position of tokens that have a variant (up to the end of the chunk)
        # 2. when appearing the second time in a poem, it is followed by the variant (to be replace with the variant)
        # For our purposes, we will combine the variants into the same decomposition segment (?? or ignore them).

        # poem_id = records[variant_indices[0][0]].poem
        # anthology = records[variant_indices[0][0]].anthology

        for k in range(len(variant_indices) - 3, -1, -3):
            begin_original, begin_variant, end_variant = variant_indices[k : k + 3]

            # If we want to use the number index (this needs more debugging):
            # number_record_idx = begin_variant[0]
            # try:
            #     number_string = unicodedata.normalize(
            #         "NFKC",
            #         records[number_record_idx].segments[0].tokens[0].surface,
            #     )
            #     parsed_variant_count = int(number_string[1])
            # except (IndexError, ValueError):
            #     parsed_variant_count = None

            variant_count = end_variant[0] - begin_variant[0] - 1
            # if parsed_variant_count and parsed_variant_count != variant_count:
            #     logger.debug(
            #         f"Parsed variant count: {parsed_variant_count} != Counted variant count: {variant_count}"
            #     )

            _original_start_index = begin_original[0] + 1
            # logger.info(
            #     f"Original: {records[original_start_index:original_start_index+variant_count]}"
            # )
            # logger.info(f"Variants: {records[begin_variant[0] + 1]}")
            variant_tokens = records[
                begin_variant[0] + 1 : begin_variant[0] + 1 + variant_count
            ]
            # logger.info(
            #     f"Variant tokens: {variant_tokens} to be added to original {records[original_start_index:original_start_index+variant_count]}"
            # )

            # Move variant tokens next to the original tokens by looking at their decomposition_type
            # logger.warning(
            #     f"Processing variants for poem {poem_id} record: {' | '.join(str(records[idx].segments) for idx in range(begin_original[0], begin_original[0] + variant_count))}"
            # )
            for original_record, variant_record in zip(
                records[begin_original[0] + 1 : begin_original[0] + 1 + variant_count],
                variant_tokens,
            ):
                if original_record.segments and variant_record.segments:
                    for original_segment, variant_segment in zip(
                        original_record.segments, variant_record.segments
                    ):
                        if (
                            original_segment.decomposition_type
                            == variant_segment.decomposition_type
                        ):
                            for variant_token in variant_segment.tokens:
                                if variant_token not in original_segment.tokens:
                                    original_segment.tokens.append(variant_token)
                    # logger.info(
                    #     f"Processed variants for poem {poem_id} record: {original_tokens} -> {segment.tokens}"
                    # )
            # logger.info(
            #     f"Before poem: {' '.join([r.token().surface for r in records if r.poem == poem_id and r.anthology == anthology])}"
            # )

            # Remove the merged segments and remaining ＊ tokens from records
            del records[begin_variant[0] : begin_variant[0] + 2 + variant_count]
            # Remove the first ＊ token
            del records[begin_original[0]]

            # logger.info(
            #     f"Mid poem: {' '.join([r.token().surface for r in records if r.poem == poem_id and r.anthology == anthology])}"
            # )

            records[:] = [
                record
                for record in records
                if any(segment.tokens for segment in record.segments)
            ]

            # logger.warning(
            #     f"Processed and removed variants and ＊ tokens for poem {poem_id} record: {records[begin_original[0]].segments}"
            # )
            # logger.error(
            #     [
            #         r.segments
            #         for r in records
            #         if r.poem == poem_id and r.anthology == anthology
            #     ]
            # )
            # logger.info(
            #     f"Cleaned poem: {' '.join([r.token().surface for r in records if r.poem == poem_id and r.anthology == anthology])}"
            # )

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
                    re.sub(r"[〈〉]", "", surface),
                    lemma,
                    lemma_reading,
                    kanji,
                    kanji_reading,
                )
                # token is represented as a list of tokens within possible decomposition list
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

    def text(
        self,
        delimiter=" ",
        anthology=None,
        poem=None,
        serial=None,
        embed_metadata=False,
    ):
        by_poem = groupby(
            self.query(anthology=anthology, poem=poem, serial=serial),
            key=lambda r: (r.anthology, r.poem),
        )
        return "\n".join(
            f"{' '.join(str(info) for info in _poem_info) + ' ' if embed_metadata else ''}{delimiter.join(record.token().surface for record in poem)}"
            for _poem_info, poem in by_poem
        )


if __name__ == "__main__":
    db = HachidaishuDB()
    for e in db:
        for ts in e.segments:
            for t in ts.tokens:
                assert t.ud_pos is not None
    for poem in db.text(embed_metadata=True).split("\n"):
        assert len(poem.split()) > 3, poem
    for meta, poem in groupby(db.query(), key=lambda r: (r.anthology, r.poem)):
        tokens = [r.token() for r in poem]
        assert len(tokens) > 5, meta

    print("Validation complete. Printing the top 20 and bottom 20 tokens.")
    c = Counter((t.surface, t.ud_pos) for t in db.tokens())
    for token, freq in c.most_common(20):
        print(f"{token}: {freq}")
    print()
    for token, freq in c.most_common()[:-21:-1]:
        print(f"{token}: {freq}")

    print("Printing space-delimited corpus.")
    print(db.text())
