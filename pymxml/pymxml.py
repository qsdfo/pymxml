import music21 as music21


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
    notes = {}
    elements = {}
    id = 0
    for part in score_soundingPitch.parts:
        elements_iterator = part.flat.notes
        instrument = part.partName
        for element in elements_iterator:
            # Need to quantize at some point...
            offset = element.offset
            duration = element.duration.quarterLength
            offset_quantized = int(round(offset) * subdivision)
            if element.isChord:
                for note in element._notes:
                    pitch, velocity = get_note(note)
                    add_note(notes, pitch, velocity, offset, offset_quantized, duration, instrument, id)
                    elements[id] = note
                    id = id + 1
            else:
                pitch, velocity = get_note(element)
                add_note(notes, pitch, velocity, offset, offset_quantized, duration, instrument, id)
                elements[id] = element
                id = id + 1
    # Transform to the correct format
    offset_quantized_list = sorted(notes.keys())
    notes_list = []
    for time in offset_quantized_list:
        notes_list.append(notes[time])
    return notes_list, elements


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


def get_note(note):
    velocity = note.volume.velocity
    if velocity is None:
        velocity = 128
    pitch = note_to_midiPitch(note)
    if note.tie and not(note.tie.type == 'start'):
        raise Exception()
    return pitch, velocity

def add_note(notes, pitch, velocity, offset, offset_quantized, duration, instrument, id):
    this_note = {
                    'offset': offset,
                    'duration': duration,
                    'pitch': pitch,
                    'velocity': velocity,
                    'instrument': instrument,
                    'id': id
                }
    if offset_quantized in notes.keys():
        notes[offset_quantized].append(this_note) 
    else:
        notes[offset_quantized] = [this_note]
    return notes