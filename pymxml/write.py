import music21 as music21


def mxml_write(score, notes_list):
    """
    :param durations:
    :param tensor_score: one-hot encoding with dimensions (time, instrument)
    :return:
    """
    new_score = music21.stream.Stream()
    parts = {}
    for notes_and_harmonies in notes_list:
        notes = notes_and_harmonies['notes']
        for note_index, note in enumerate(notes):
            # Get corresponding part
            m21_identifier = note['m21_identifier']
            part_id = m21_identifier['part_identifier']
            if part_id not in parts:
                this_part = score.getElementById(part_id)
                # Remove existing harmony
                this_part_flat = this_part.flat
                # this_part_flat = [e for e in this_part.flat if ('ChordSymbol' not in e.classes) \
                #     or 'Harmony' not in e.classes]
            else:
                this_part_flat = parts[part_id]

            # Get element in the part
            element_identifier = m21_identifier['element_identifier']
            this_element = this_part_flat.getElementById(element_identifier)
            chord_index = m21_identifier['chord_index']

            # FIXME: associate the harmony to the first part of the score (now it's only to the highest pitch in chord, which might change part....)
            if note_index == 0:
                harmonies = notes_and_harmonies['harmonies']
                assert len(
                    harmonies) < 3, "can't have more than two harmony elements at a time"
                for ind_harmo, harmony in enumerate(harmonies):
                    # To deal with chords written in the original score (and not extracted through analysis):
                    # the correct spelling of the chord for music21 would be stored in the figure attribute
                    if harmony['figure'] is not None:
                        m21_harmo = music21.harmony.ChordSymbol(
                            figure=harmony['figure'], color=harmony['color'])
                    else:
                        m21_harmo = music21.harmony.ChordSymbol(
                            root=harmony['root'], bass=harmony['bass'], kind=harmony['kind'], color=harmony['color'])
                    if harmony['color'] is not None:
                        m21_harmo.style.color = harmony['color']
                    if ind_harmo == 1:
                        m21_harmo.style.relativeY = 100
                    this_part_flat.insert(this_element.offset, m21_harmo)

            # Add colored text
            if note['text'] is not None:
                if chord_index != -1:
                    lyric_identifier = f'{element_identifier}_{chord_index}'
                else:
                    lyric_identifier = f'{element_identifier}'

                # FIXME: if two or more voices are written, lyrics might be placed at the same position (-1 for melodies)
                this_element.addLyric(
                    note['text'], lyricNumber=chord_index, lyricIdentifier=lyric_identifier)

                if note['color'] is not None:
                    for this_lyric in this_element.lyrics:
                        if this_lyric.identifier == lyric_identifier:
                            this_lyric.style.color = note['color']

            # Color note
            if chord_index != -1:
                this_element = this_element[chord_index]
            if note['color'] is not None:
                this_element.style.color = note['color']

            # Store the modified part
            parts[part_id] = this_part_flat

    for flat_part in parts.values():
        new_score.append(flat_part)

    # # First parse notes_list index by part_id and notes_id
    # id_to_meta = {}
    # for notes in notes_list:
    #     for note in notes:
    #         color = note['color']
    #         text = note['text']
    #         harmony = note['harmony']
    #         m21_identifier = note['m21_identifier']
    #         for m21_identifier in m21_identifiers:
    #             part_identifier = m21_identifier['part_identifier']
    #             element_identifier = m21_identifier['element_identifier']
    #             chord_index = m21_identifier['chord_index']
    #             if part_identifier not in id_to_meta:
    #                 id_to_meta[part_identifier] = {}
    #             id_to_meta[part_identifier][(
    #                 element_identifier, chord_index)] = {
    #                     'color': color,
    #                     'text': text,
    #                     'harmony': harmony
    #             }

    # # First pass to color existing lyrics
    # for part_id, meta_dict in id_to_meta.items():
    #     this_part = score.getElementById(part_id)
    #     this_part_flat = this_part.flat
    #     for m21_identifier, metas in meta_dict.items():
    #         element_identifier, chord_index = m21_identifier
    #         this_element = this_part_flat.getElementById(element_identifier)
    #         if metas['color'] is not None:
    #             for this_lyric in this_element.lyrics:
    #                 this_lyric.style.color = metas['color']

    # new_score = music21.stream.Stream()
    # # Modify score
    # for part_id, meta_dict in id_to_meta.items():
    #     this_part = score.getElementById(part_id)
    #     this_part_flat = this_part.flat
    #     for m21_identifier, metas in meta_dict.items():
    #         # Get element in the part
    #         element_identifier, chord_index = m21_identifier
    #         this_element = this_part_flat.getElementById(element_identifier)

    #         # Add colored text
    #         if metas['text'] is not None:
    #             if chord_index != -1:
    #                 lyric_identifier = f'{element_identifier}_{chord_index}'
    #             else:
    #                 lyric_identifier = f'{element_identifier}'

    #             # FIXME: if two or more voices are written, lyrics might be placed at the same position (-1 for melodies)
    #             this_element.addLyric(
    #                 metas['text'], lyricNumber=chord_index, lyricIdentifier=lyric_identifier)

    #             if metas['color'] is not None:
    #                 for this_lyric in this_element.lyrics:
    #                     if this_lyric.identifier == lyric_identifier:
    #                         this_lyric.style.color = metas['color']

    #         # Add colored roman numeral analysis
    #         if len(metas['harmony']) > 0:
    #             assert len(
    #                 metas['harmony']) < 3, "can't have more than two harmony elements for a single note"
    #             offset = this_element.offset
    #             for ind_harmo, harmony in enumerate(metas['harmony']):
    #                 this_harmo = music21.harmony.ChordSymbol(**harmony)
    #                 if metas['color'] is not None:
    #                     this_harmo.style.color = metas['color']
    #                 if ind_harmo == 1:
    #                     this_harmo.style.relativeY = 100
    #                 this_part_flat.insert(offset, this_harmo)

    #         # Color note
    #         if chord_index != -1:
    #             this_element = this_element[chord_index]
    #         if metas['color'] is not None:
    #             this_element.style.color = metas['color']
    #     new_score.append(this_part_flat)
    return new_score


def change_color(filepath):
    """
    For testing and exemple of how to keep track of an id in m21 score format
    """
    score = music21.converter.parse(filepath)
    for part in score.parts:
        part_flat = part.flat
        elements_iterator = part_flat.notes
        instrument = part.partName
        for element in elements_iterator:
            if element.isChord:
                m21_notes = element._notes
                identifier = element.id
                for chord_index, m21_note in enumerate(m21_notes):
                    part_flat.getElementById(identifier)[
                        chord_index].style.color = 'red'
            else:
                m21_notes = element
                identifier = element.id
                part_flat.getElementById(identifier).style.color = 'red'
    score.write(fp='out_test_color.mxml', fmt='musicxml')
