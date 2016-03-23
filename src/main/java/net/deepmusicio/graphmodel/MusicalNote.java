package net.deepmusicio.graphmodel;

import javax.sound.midi.MidiMessage;
import javax.sound.midi.ShortMessage;

/**
 * Created by Adisor on 3/20/2016.
 */

// Immutable - except for duration
public class MusicalNote {

    // pitch can be 0-127
    private final int pitch;

    // velocity can be up to 255
    private final int velocity;

    // how long the note is played
    private double duration;

    public MusicalNote(ShortMessage shortMidiMessage) {
        this(shortMidiMessage.getData1(), shortMidiMessage.getData2(), 0);
    }

    public MusicalNote(ShortMessage shortMidiMessage, double duration) {
        this(shortMidiMessage.getData1(), shortMidiMessage.getData2(), duration);
    }

    public MusicalNote(int pitch, int velocity, double duration) {
        this.pitch = pitch;
        this.velocity = velocity;
        this.duration = duration;
    }

    public void setDuration(double duration){
        this.duration = duration;
    }

    public int getPitch() {
        return pitch;
    }

    public int getVelocity() {
        return velocity;
    }

    public double getDuration() {
        return duration;
    }
}
