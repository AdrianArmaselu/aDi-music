package net.deepmusicio.graphmodel;

import java.util.ArrayList;
import java.util.List;

/**
 * Created by Adisor on 3/20/2016.
 */

//Can either be e note or a chord (set of notes)

public class SoundEvent {

    private List<MusicalNote> notes;

    public SoundEvent() {
        notes = new ArrayList<>();
    }

    public void addChordNote(MusicalNote note) {
        notes.add(note);
    }

    public void setNote(MusicalNote note) {
        if (notes.isEmpty()) notes.add(note);
        else notes.set(0, note);
    }

}
