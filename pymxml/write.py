import music21 as music21

def mxml_write(id_to_m21, id_to_metadata):
    """
    :param durations:
    :param tensor_score: one-hot encoding with dimensions (time, instrument)
    :return:
    """
    #  Batch is used as time in the score
    parts = {}

    for id, m21 in id_to_m21.items():
        # This will contain colour and textual information added by the analysis
        if id_to_metadata is not None:
            metadata = id_to_metadata[id]
            raise Exception('Not implemented yet')
        part_name = m21.part    
        if part_name not in streams():
            this_part = music21.stream.Part(id=part_name)
            parts[part_name] = this_part
            instrument_name = m21.instrument
            music21_instrument = music21.instrument.fromString(instrument_name)
            parts[part_name].insert(0, music21_instrument)


    for instrument_name, elems in score_dict.items():
        this_part = music21.stream.Part(id=instrument_name)
        #  re is for removing underscores in instrument names which raise errors in music21
        if instrument_name == "Cymbal":
            music21_instrument = music21.instrument.Cymbals()
        elif instrument_name == "Woodwind":
            music21_instrument = music21.instrument.fromString("Clarinet")
        elif instrument_name == "String":
            music21_instrument = music21.instrument.fromString("Violoncello")
        elif instrument_name == "Brass":
            music21_instrument = music21.instrument.fromString("Horn")
        else:
            music21_instrument = music21.instrument.fromString(re.sub('_', ' ', instrument_name))
        this_part.insert(0, music21_instrument)

        if elems == []:
            f = music21.note.Rest()
            f.quarterLength = total_duration_ql
            this_part.insert(0, f)
        else:
            #  Sort by offset time (not sure it's very useful, more for debugging purposes)
            elems = sorted(elems, key=lambda e: e[1])
            for elem in elems:
                pitch, offset, duration = elem
                try:
                    f = music21.note.Note(pitch)
                except:
                    print('yo')
                f.volume.velocity = 60.
                f.quarterLength = duration / subdivision
                this_part.insert((offset / subdivision), f)

        if format == 'xml':
            this_part = this_part.chordify()
        this_part.atSoundingPitch = self.transpose_to_sounding_pitch
        stream.append(this_part)

    return stream
