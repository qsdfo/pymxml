import music21 as music21


def mxml_write(score, notes_list):
    """
    :param durations:
    :param tensor_score: one-hot encoding with dimensions (time, instrument)
    :return:
    """
    # First parse notes_list index by part_id and notes_id
    id_to_meta = {}
    for notes in notes_list:
        for note in notes:
            colour = note['colour']
            text = note['text']
            m21_identifiers = note['m21_identifiers']
            for m21_identifier in m21_identifiers:
                part_identifier = m21_identifier['part_identifier']
                element_identifier = m21_identifier['element_identifier']
                chord_index = m21_identifier['chord_index']
                if part_identifier not in id_to_meta:
                    id_to_meta[part_identifier] = {}
                id_to_meta[part_identifier][(
                    element_identifier, chord_index)] = {
                        'colour': colour,
                        'text': text
                }

    # Modify score
    for part_id, meta_dict in id_to_meta.items():
        this_part = score.getElementById(part_id)
        this_part_flat = this_part.flat
        for m21_identifier, metas in meta_dict.items():
            element_identifier, chord_index = m21_identifier
            this_element = this_part_flat.getElementById(element_identifier)
            if chord_index == -1 or chord_index == 0:
                this_element.lyric = metas['text']
            if chord_index != -1:
                this_element = this_element[chord_index]
            this_element.style.color = metas['colour']
    return score


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
