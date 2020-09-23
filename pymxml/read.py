import music21


def mxml_read(filepath):
    subdivision = 64
    m21_score = music21.converter.parse(filepath)
    notes_list = read_score(m21_score, subdivision)
    return notes_list, m21_score


def read_score(score, subdivision):
    # Transpose the score at sounding pitch. Simplify when transposing
    # instruments are in the score
    # try:
    #     score_soundingPitch = score.toSoundingPitch()
    # except:
    #     score_soundingPitch = score

    # Output
    notes_dict = {}
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
            offset_quantized = int(round(offset) * subdivision) // subdivision

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
                    'id': id
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

                # Write in list of notes
                if write:
                    if this_note['offset_quantized'] in notes_dict.keys():
                        notes_dict[this_note['offset_quantized']].append(
                            this_note)
                    else:
                        notes_dict[this_note['offset_quantized']] = [this_note]
                id = id + 1

    # Transform to the correct format
    offset_quantized_list = sorted(notes_dict.keys())
    notes_list = []
    for time in offset_quantized_list:
        notes_list.append(notes_dict[time])
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
