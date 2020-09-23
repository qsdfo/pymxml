import music21 as music21

def mxml_write(score, id_to_m21, id_to_metadata):
    """
    :param durations:
    :param tensor_score: one-hot encoding with dimensions (time, instrument)
    :return:
    """
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
