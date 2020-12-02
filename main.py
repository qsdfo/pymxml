from pymxml.write import mxml_write
from pymxml.read import mxml_read
import random


if __name__ == '__main__':
    filepath = 'data/leadsheet_slurs.xml'
    notes_list, m21_score = mxml_read(filepath)

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
    for notes_and_harmonies in notes_list:
        notes = notes_and_harmonies['notes']
        harmonies = notes_and_harmonies['harmonies']

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

        # Color harmony
        harmonies_colored = []
        for harmony in harmonies:
            if harmony['color'] is None:
                color = random.choice(['red', 'blue', 'green'])
            else:
                color = harmony['color']
            harmony_colored = harmony
            harmony_colored['color'] = color
            harmonies_colored.append(harmony_colored)

        counter += 1
        notes_list_colored.append(
            dict(notes=notes_colored, harmonies=harmonies_colored))
    #########################

    modified_score = mxml_write(m21_score, notes_list_colored)
    modified_score.write(fp='out.mxml', fmt='musicxml')

    # import music21
    # s1 = music21.stream.Stream()
    # s1.append(music21.note.Note('C#4', type='half', lyric='death'))
    # s1.append(music21.note.Note('D5', type='quarter'))
    # s1.insert(0, music21.harmony.ChordSymbol(kind='minor', kindStr='m', root='C'))
    # s1.write(fp='testounet.mxml', fmt='musicxml')
