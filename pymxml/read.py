import music21


def mxml_read(filepath):
    subdivision = 64
    score = music21.converter.parse(filepath)
    notes_list, mxml_elements = read_score(score, subdivision)
    return notes_list, mxml_elements


def read_score(score, subdivision):
    # Transpose the score at sounding pitch. Simplify when transposing instruments are in the score
    try:
        score_soundingPitch = score.toSoundingPitch()
    except:
        score_soundingPitch = score

    # Output
    notes_dict = {}
    id_to_m21 = {}
    tied_notes = {}
    id = 0
    for part in score_soundingPitch.parts:
        elements_iterator = part.flat.notes
        instrument = part.partName
        for element in elements_iterator:
            # Need to quantize at some point...
            offset = element.offset
            duration = element.duration.quarterLength
            offset_quantized = int(round(offset) * subdivision) // subdivision

            if element.isChord:
                m21_notes = element._notes
            else:
                m21_notes = [element]

            for m21_note in m21_notes:
                pitch, velocity = get_pitch_velocity(m21_note)
                this_note = {
                    'offset': offset,
                    'offset_quantized': offset_quantized,
                    'duration': duration,
                    'pitch': pitch,
                    'velocity': velocity,
                    'instrument': instrument,
                    'mxml_ids': [id],
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
                            tied_notes[pitch]['mxml_ids'].append(id)
                        else:
                            raise Exception('Trying to tie a note which does not have a starting tie')
                        if m21_note.tie.type == 'stop':
                            this_note = tied_notes[pitch]
                            tied_notes.pop(pitch, None)
                            write = True
                    
                # Write in list of notes
                if write:
                    if this_note['offset_quantized'] in notes_dict.keys():
                        notes_dict[this_note['offset_quantized']].append(this_note)
                    else:
                        notes_dict[this_note['offset_quantized']] = [this_note]
                id_to_m21[id] = m21_note
                id = id + 1

    # Transform to the correct format
    offset_quantized_list = sorted(notes_dict.keys())
    notes_list = []
    for time in offset_quantized_list:
        notes_list.append(notes_dict[time])
    return notes_list, id_to_m21


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