import music21
from pymxml.write import mxml_write
from pymxml.read import mxml_read


if __name__ == '__main__':
    # filepath = 'xmlsamples/ActorPreludeSample.musicxml'
    filepath = 'xmlsamples/MozartPianoSonata.mxl'
    # notes_list, id_to_m21 = mxml_read(filepath)

    # mxml_write(id_to_m21=id_to_m21, id_to_metadata=None)
    # Test to modify the colour of a score

    score = music21.converter.parse(filepath)
    score.write(fp='out_test.mxml', fmt='musicxml')
    score_flat = score.flat
    for element in score_flat.elements:
        if (hasattr(element, 'isNote') and element.isNote)\
            or (hasattr(element, 'isChord') and element.isChord):
            id = element.id
            score_flat.getElementById(element.id).style.color = 'red'
    # for part in score_soundingPitch.parts:
    #     elements_iterator = part.flat.notes
    #     for element in elements_iterator:
    #         part.getElementById(element.id).style.color = 'red'
    score.write(fp='out_test_color.mxml', fmt='musicxml')
