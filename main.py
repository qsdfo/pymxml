from pymxml.write import mxml_write
from pymxml.read import mxml_read
import random


if __name__ == '__main__':
    # filepath = 'xmlsamples/ActorPreludeSample.musicxml'
    filepath = 'xmlsamples/MozartPianoSonata.mxl'
    notes_list, m21_score = mxml_read(filepath)

    #########################
    # Randomly adding colours for testing
    for notes in notes_list:
        for note in notes:
            colour = random.choice(['red', 'blue', 'green'])
            note['colour'] = colour
    #########################

    modified_score = mxml_write(m21_score, notes_list)
    modified_score.write(fp='out_test_color.mxml', fmt='musicxml')

    # score_flat = score.flat
    # for element in score_flat.elements:
    #     if (hasattr(element, 'isNote') and element.isNote)\
    #         or (hasattr(element, 'isChord') and element.isChord):
    #         identifier = element.id
    #         score_flat.getElementById(element.id).style.color = 'red'

    # score = music21.converter.parse(filepath)
    # for part in score.parts:
    #     part_flat = part.flat        
    #     elements_iterator = part_flat.notes
    #     instrument = part.partName
    #     for element in elements_iterator:
    #         if element.isChord:
    #             m21_notes = element._notes
    #             identifier = element.id
    #             for chord_index, m21_note in enumerate(m21_notes):
    #                 part_flat.getElementById(identifier)[chord_index].style.color = 'red'
    #         else:
    #             m21_notes = element
    #             identifier = element.id
    #             part_flat.getElementById(identifier).style.color = 'red'
    # score.write(fp='out_test_color.mxml', fmt='musicxml')
