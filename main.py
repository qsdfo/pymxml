from pymxml.write import mxml_write
from pymxml.read import mxml_read
import random


if __name__ == '__main__':
    # filepath = 'xmlsamples/ActorPreludeSample.musicxml'
    filepath = 'xmlsamples/MozartPianoSonata.mxl'
    notes_list, m21_score = mxml_read(filepath)

    #########################
    # Randomly adding colours for testing
    notes_list_coloured = []
    for notes in notes_list:
        notes_coloured = []
        for note in notes:
            colour = random.choice(['red', 'blue', 'green'])
            note_coloured = note
            note_coloured['colour'] = colour
            notes_coloured.append(note_coloured)
        notes_list_coloured.append(notes_coloured)
    #########################

    modified_score = mxml_write(m21_score, notes_list_coloured)
    modified_score.write(fp='out_test_color.mxml', fmt='musicxml')