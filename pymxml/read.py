import math
import music21


def mxml_read(filepath):
    precision = 0.01
    m21_score_dirty = music21.converter.parse(filepath)
    m21_score = sanitize_score(m21_score_dirty)
    notes_list = read_score(m21_score, precision)
    return notes_list, m21_score


def read_score(score, precision):
    # Transpose the score at sounding pitch. Simplify when transposing
    # instruments are in the score
    # try:
    #     score_soundingPitch = score.toSoundingPitch()
    # except:
    #     score_soundingPitch = score

    # Output
    notes_dict = {}
    chord_symbols = []
    tied_notes = {}
    id = 0

    for part in score.parts:
        part_identifier = part.id
        part_flat = part.flat
        elements_iterator = part_flat.notes
        instrument = part.partName
        for element in elements_iterator:
            element_identifier = element.id
            # Need to quantize at some point...
            offset = element.offset
            duration = element.duration.quarterLength
            offset_quantized = math.floor(offset / precision) * precision

            # Element can be a chord symbol in lead sheets
            if 'ChordSymbol' in element.classes:
                this_chord_symbol = {
                    'offset': offset_quantized,
                    'figure': element.figure,
                    'kind': element.chordKind,
                    'root': element.root(),
                    'bass': element.bass(),
                }
                chord_symbols.append(this_chord_symbol)
                continue

            is_chord = False
            if element.isChord:
                m21_notes = element._notes
                is_chord = True
            else:
                m21_notes = [element]

            for chord_index, m21_note in enumerate(m21_notes):
                if is_chord:
                    m21_identifier = {
                        'part_identifier': part_identifier,
                        'element_identifier': element_identifier,
                        'chord_index': chord_index
                    }
                else:
                    m21_identifier = {
                        'part_identifier': part_identifier,
                        'element_identifier': element_identifier,
                        'chord_index': -1
                    }
                pitch, velocity = get_pitch_velocity(m21_note)
                this_note = {
                    'offset': offset,
                    'offset_quantized': offset_quantized,
                    'duration': duration,
                    'pitch': pitch,
                    'velocity': velocity,
                    'instrument': instrument,
                    'm21_identifiers': [m21_identifier],
                    'id': id,
                    # Metas informations
                    'color': None,
                    'text': None,
                    'harmony': []
                }

                # check for ties
                write = True
                if m21_note.tie:
                    write = False
                    if m21_note.tie.type == 'start':
                        tied_notes[pitch] = this_note
                    else:
                        # find the tied notes and append duration
                        if pitch in tied_notes:
                            tied_notes[pitch]['duration'] += duration
                            tied_notes[pitch]['m21_identifiers'].append(
                                m21_identifier)
                        else:
                            raise Exception(
                                'Trying to tie a note which \
                                    does not have a starting tie')
                        if m21_note.tie.type == 'stop':
                            this_note = tied_notes[pitch]
                            tied_notes.pop(pitch, None)
                            write = True

                # Write in dict of notes
                if write:
                    if this_note['offset_quantized'] in notes_dict.keys():
                        notes_dict[this_note['offset_quantized']].append(
                            this_note)
                    else:
                        notes_dict[this_note['offset_quantized']] = [this_note]
                id = id + 1

    # Sort chord symbols by offset times
    if len(chord_symbols) > 0:
        chord_symbols = sorted(chord_symbols, key=lambda x: x['offset'])

    # Convert dict to list sorted by offset time
    offset_quantized_list = sorted(notes_dict.keys())
    notes_list = []
    for time in offset_quantized_list:
        while((len(chord_symbols) > 1) and (time >= chord_symbols[1]['offset'])):
            chord_symbols.pop(0)

        # Sort by decreasing pitch
        notes_dict_t = notes_dict[time]
        notes_to_write = sorted(notes_dict_t, key=lambda x: -x['pitch'])
        if (len(chord_symbols) > 0):
            harmo_dict = {
                # 'figure': chord_symbols[0]['figure'],
                'kind': chord_symbols[0]['kind'],
                'root': chord_symbols[0]['root'],
                'bass': chord_symbols[0]['bass']
            }
            for e in notes_to_write:
                e['harmony'].append(harmo_dict)
        notes_list.append(notes_to_write)
    return notes_list


def note_to_midiPitch(note):
    """
    music21 note to number
    :param note:
    :return:
    """
    # +1 on octave is needed to obtain midi pitch
    octave = (note.octave + 1)
    pc = note.pitch.pitchClass
    return octave * 12 + pc


def get_pitch_velocity(note):
    velocity = note.volume.velocity
    if velocity is None:
        velocity = 128
    pitch = note_to_midiPitch(note)
    return pitch, velocity

def sanitize_score(score):
    """
    Simply prevents two parts to have the same id
    """
    part_ids = []
    for part in score.parts:
        part_identifier = part.id
        if part_identifier in part_ids:
            new_part_identifier = part_identifier + '_'
            part.id = new_part_identifier
        else:
            new_part_identifier = part_identifier
        part_ids.append(new_part_identifier)
    return score
