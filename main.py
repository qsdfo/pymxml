from pymxml.write import mxml_write
from pymxml.read import mxml_read
import random


if __name__ == '__main__':
    filepath = 'xmlsamples/ActorPreludeSample.musicxml'
    # filepath = 'xmlsamples/MozartPianoSonata.mxl'
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

    # # DEBUG: 139971019057568
    # for part in m21_score.parts:
    #     part_identifier = part.id
    #     if part_identifier == '1 2':
    #         print('yolo')
    #     part_flat = part.flat
    #     elements_iterator = part_flat.notes
    #     instrument = part.partName
    #     for element in elements_iterator:
    #         element_identifier = element.id
    #         # Need to quantize at some point...
    # # DEBUG:

    modified_score = mxml_write(m21_score, notes_list_coloured)
    modified_score.write(fp='out_test_color.mxml', fmt='musicxml')
