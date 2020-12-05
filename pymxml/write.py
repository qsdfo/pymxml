from pymxml.read import mxml_read
import music21 as music21


def mxml_write(filepath, notes_list, id_to_harmony):
    """
    :param durations:
    :param tensor_score: one-hot encoding with dimensions (time, instrument)
    :return:
    """
    # Rebuild the m21_identifiers
    _, _, id_to_m21_identifiers, score = mxml_read(filepath)

    new_score = music21.stream.Stream()
    parts = {}

    for notes in notes_list:
        for note in notes:
            # Get corresponding part
            m21_identifier = id_to_m21_identifiers[note['id']]
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

    # Get a list of harmonies sorted by offset time
    harmonies = sorted([e for e in id_to_harmony.values()], key=lambda x: x['offset'])
    previous_offset = None
    # Write/modify harmony
    for harmony in harmonies:
        if previous_offset == harmony['offset']:
            write_on_top = True
        else:
            write_on_top = False
        previous_offset = harmony['offset']

        # If chords was written on the original score before the analysis, it will have an identifier
        harmony_id = harmony['id']
        if harmony_id in id_to_m21_identifiers.keys():
            m21_identifier = id_to_m21_identifiers[harmony_id]
            part_id = m21_identifier['part_identifier']
            if part_id not in parts:
                raise Exception('trying to write a chord in a part with no notes')
            else:
                this_part_flat = parts[part_id]
            # Get element in the part
            element_identifier = m21_identifier['element_identifier']
            this_element = this_part_flat.getElementById(element_identifier)
            # Color note
            if harmony['color'] is not None:
                this_element.style.color = harmony['color']
            if write_on_top:
                this_element.style.relativeY = 100
        else:
            if harmony['figure'] is not None:
                m21_harmo = music21.harmony.ChordSymbol(
                    figure=harmony['figure'], color=harmony['color'])
            else:
                m21_harmo = music21.harmony.ChordSymbol(
                    root=harmony['root'], bass=harmony['bass'], kind=harmony['kind'], color=harmony['color'])
            if harmony['color'] is not None:
                m21_harmo.style.color = harmony['color']
            if write_on_top:
                m21_harmo.style.relativeY = 100
            # FIXME: define the part used for writing harmony, not a random one like this
            this_part_flat = parts[list(parts.keys())[0]]
            this_part_flat.insert(harmony['offset'], m21_harmo)

    for flat_part in parts.values():
        new_score.append(flat_part)
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
