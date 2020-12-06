import math
import music21


def mxml_read(filepath):
    m21_score_dirty = music21.converter.parse(filepath)
    m21_score = sanitize_score(m21_score_dirty)
    notes_list, id_to_harmony, id_to_m21_identifiers = read_score(m21_score)
    return notes_list, id_to_harmony, id_to_m21_identifiers, m21_score


def read_score(score):
    """
    Read a musicxml file and output a list of dictionnaries containing:
        - notes: the notes occuring in the different parts of the score sorted by offset time.
        - harmonies: the (possibly several) harmonic analysis/interpretation of the chord formed by the notes
    Thus, returned notes_list has the following structure

    notes_list = [{
                    notes: [note],
                    harmonies: [harmony]}
                ]

    where note is a dictionnary containing the following informations

    note = {
        'id': unique identifier associated to each note in the score,
        'offset': time offset in quarter notes quantized using the precision variable,
        'duration': duration of the note in quarter length,
        'tie_previous_id': indicate if the note is tied to a previous note. If no set to None, if yes, set to the 'id' of the previous note,
        'pitch': pitch,
        'velocity': velocity,
        'instrument': instrument,
        # Metas informations
        'color': None,
        'text': None,
    }

    and harmony is a dictionnary

    harmony = {
        'id': unique identifier,
        'offset': ,
        'kind': ,
        'root': ,
        'bass': ,
        'colour': 
    }
    """
    # Parameters
    precision = 0.01

    # Variables
    id_to_m21_identifiers = {}
    notes_dict = {}
    chord_symbols = []
    tied_notes = {}
    id = None

    for part_index, part in enumerate(score.parts):
        part_identifier = part.id
        part_flat = part.flat
        elements_iterator = part_flat.notes
        instrument = part.partName
        for element_index, element in enumerate(elements_iterator):
            element_identifier = element.id
            # Need to quantize at some point...
            offset = element.offset
            duration = element.duration.quarterLength
            offset_quantized = math.floor(offset / precision) * precision

            # Element can be a chord symbol in lead sheets
            if 'ChordSymbol' in element.classes:
                # Create the chord identifier
                id = f'{part_index}_{element_index}'
                # Existing color?
                color = element.style.color
                # m21_identifier
                m21_identifier = {
                    'part_identifier': part_identifier,
                    'element_identifier': element_identifier,
                }

                id_to_m21_identifiers[id] = m21_identifier

                this_chord_symbol = {
                    'id': id,
                    'offset': offset_quantized,
                    'figure': element.figure,
                    'kind': element.chordKind,
                    'chord_notes': element.pitchNames if element else [],
                    'root': element.root().nameWithOctave if element else None,
                    'bass': element.bass().nameWithOctave if element else None,
                    'color': color,
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
                octave, note_name, pitch, velocity = get_pitch_velocity(m21_note)

                # Create the note identifier
                id = f'{part_index}_{element_index}_{chord_index}'
                id_to_m21_identifiers[id] = m21_identifier
                # Existing color?
                color = element.style.color
                # Existing text/lyrics?
                text = element.lyrics
                if len(text) == 0:
                    text = None

                this_note = {
                    'id': id,
                    'offset': offset_quantized,
                    'duration': duration,
                    'tie_previous_id': None,
                    'pitch': pitch,
                    'velocity': velocity,
                    'instrument': instrument,
                    'octave': octave,
                    'note': note_name,
                    # Metas informations
                    'color': color,
                    'text': text,
                    'harmony': [],
                }

                # check for ties
                if m21_note.tie:
                    if m21_note.tie.type == 'start':
                        tied_notes[pitch] = id
                    else:
                        if pitch not in tied_notes:
                            raise Exception(
                                'Trying to tie a note which \
                                    does not have a starting tie')

                        # Get the id of the previous note
                        previous_note_id = tied_notes[pitch]
                        this_note['tie_previous_id'] = previous_note_id
                        # Replace the id in tied_notes with id of the current note
                        tied_notes[pitch] = id
                        # If it was the last note in the tie, remove from the list of tied notes
                        if m21_note.tie.type == 'stop':
                            tied_notes.pop(pitch, None)

                # Write in dict of notes
                if this_note['offset'] in notes_dict.keys():
                    notes_dict[this_note['offset']].append(
                        this_note)
                else:
                    notes_dict[this_note['offset']] = [this_note]

    # Sort chord symbols by offset times
    if len(chord_symbols) > 0:
        chord_symbols = sorted(chord_symbols, key=lambda x: x['offset'])

    # Convert dict to list sorted by offset time
    offset_quantized_list = sorted(notes_dict.keys())
    notes_list = []
    harmonies_dict = {}
    for time in offset_quantized_list:
        while((len(chord_symbols) > 1) and (time >= chord_symbols[1]['offset'])):
            chord_symbols.pop(0)

        # Sort by decreasing pitch
        notes_dict_t = notes_dict[time]
        notes_to_write = sorted(notes_dict_t, key=lambda x: -x['pitch'])
        if (len(chord_symbols) > 0):
            this_harmo = chord_symbols[0]
            # harmo_dict = {
            #     # 'figure': this_harmo['figure'],
            #     # 'kind': this_harmo['kind'],
            #     # 'root': this_harmo['root'],
            #     # 'bass': this_harmo['bass'],
            #     'id': this_harmo['id']
            # }
            harmo_id = chord_symbols[0]['id']
            for e in notes_to_write:
                e['harmony'].append(harmo_id)
                e['chord_notes']=chord_symbols[0]['chord_notes']
            if this_harmo['id'] not in harmonies_dict:
                harmonies_dict[this_harmo['id']] = this_harmo
        notes_list.append(notes_to_write)
    return notes_list, harmonies_dict, id_to_m21_identifiers


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
    return note.nameWithOctave, note.name, pitch, velocity

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
