from pymxml.write import mxml_write
from pymxml.read import mxml_read
import random
import jsonplus as json
import json as js
import sys

if __name__ == '__main__':
    filepath = 'xmlsamples/Hark_The_Herald.mxl'
    #filepath = sys.argv[1]
    notes_list, id_to_harmony, _, _ = mxml_read(filepath)
    with open('song_to_analyze.json', 'w+') as f:
        f.write(json.dumps(notes_list))
        f.close()
    #########################
    # Messy example
    # Randomly adding colors for testing
    # notes_list_colored = []
    # counter = 0
    # for notes in notes_list:
    #     notes_colored = []
    #     for note in notes:
    #         color = random.choice(['red', 'blue', 'green'])
    #         # write_text_bool = random.choice([True, False])
    #         # write_harmo_bool = random.choice([True, False])
    #         write_text_bool = False
    #         write_harmo_bool = True
    #         note_colored = note
    #         note_colored['color'] = color
    #         if write_text_bool:
    #             note_colored['text'] = str(counter)
    #         if write_harmo_bool:
    #             note_colored['harmony'] = {
    #                 'function': 'V'
    #                 }
    #         notes_colored.append(note_colored)
    #         counter += 1
    #     notes_list_colored.append(notes_colored)
    #########################

    #########################
    # Messy example
    # Randomly adding colors for testing
    notes_list_colored = []
    counter = 0
    for notes in notes_list:
        # Color notes
        notes_colored = []
        for ind_note, note in enumerate(notes):
            if note['color'] is None:
                color = random.choice(['red', 'blue', 'green'])
            else:
                color = note['color']
            note_colored = note
            note_colored['color'] = color
            # Write text?
            if ind_note == 0:
                write_text_bool = random.choice([True, False])
                if write_text_bool:
                    note_colored['text'] = str(counter)
            notes_colored.append(note_colored)

        counter += 1
        notes_list_colored.append(notes_colored)
    #########################

    # Color harmony
    for k, v in id_to_harmony.items():
        if v['color'] is None:
            v['color'] = random.choice(['red', 'blue', 'green'])

    # Add a chord for testing
    id_to_harmony['nouveau_chord'] = {
        'id': 'nouveau_chord',
        'm21_identifier': None,
        'offset': 0,
        'figure': 'Fmaj7',
        'kind': None,
        'root': None,
        'bass': None,
        'color': 'yellow',
    }

    modified_score = mxml_write(filepath, notes_list_colored, id_to_harmony)
    modified_score.write(fp='out.mxml', fmt='musicxml')

    # import music21
    # s1 = music21.stream.Stream()
    # s1.append(music21.note.Note('C#4', type='half', lyric='death'))
    # s1.append(music21.note.Note('D5', type='quarter'))
    # s1.insert(0, music21.harmony.ChordSymbol(kind='minor', kindStr='m', root='C'))
    # s1.write(fp='testounet.mxml', fmt='musicxml')
