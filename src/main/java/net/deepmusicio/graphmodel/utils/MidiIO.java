package net.deepmusicio.graphmodel.utils;

import com.sun.media.sound.MidiUtils;
import net.deepmusicio.graphmodel.MusicalNote;
import net.deepmusicio.graphmodel.SoundEvent;

import javax.sound.midi.*;
import java.io.*;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

/**
 * Created by Adisor on 3/19/2016.
 *
 * Used http://stackoverflow.com/questions/3850688/reading-midi-files-in-java
 * Multiple types of midi files: https://forum.noteworthycomposer.com/?topic=4157.0
 *
 * TODO: KEEP TRACK OF TEMPO CHANGES
 * TODO: SOME CHORDS HAVE SLIGHT DIFFERENCES IN TIMES BETWEEN NOTES
 * TODO: CAN USE CHANGES IN TEMPO FOR MODEL PREDICTION
 * TODO: PICK METAEVENTS FOR THE FINAL OUTPUT
 * TODO: COMPUTE DURATION IF TEMPO IS MPQ
 * TODO: Log midi file details : tracks, events, pitches, etc.
 * TODO: CONSIDER CHANGING CHANNELS OF TRACKS
 */

public class MidiIO {

    private static final int DEFAULT_TYPE = 1;
    private Sequencer sequencer;
    private List<SoundEvent> soundEvents;
    private MidiFileFormat midiFileFormat;

    public MidiIO(String midiFile) {
        openSequencer();
        setSequence(midiFile);
        loadSoundEvents();
    }

    private void openSequencer() {
        try {
            sequencer = MidiSystem.getSequencer();
            sequencer.open();
        } catch (MidiUnavailableException e) {
            e.printStackTrace();
            sequencer.close();
        }
    }

    private void setSequence(String midiFile) {
        InputStream inputStream = openResourceStream(midiFile);
        try {
            midiFileFormat = MidiSystem.getMidiFileFormat(inputStream);
            sequencer.setSequence(inputStream);
        } catch (IOException | InvalidMidiDataException e) {
            e.printStackTrace();
        } finally {
            closeResourceIfNotNull(inputStream);
        }
    }

    private InputStream openResourceStream(String resourceFile) {
        URL midiFileUrl = getClass().getClassLoader().getResource(resourceFile);
        return openFileStream(midiFileUrl);
    }

    private InputStream openFileStream(URL url) {
        InputStream inputStream = null;
        if (url != null)
            try {
                File file = new File(url.getFile());
                inputStream = new BufferedInputStream(new FileInputStream(file));
            } catch (FileNotFoundException e) {
                e.printStackTrace();
                closeResource(inputStream);
            }
        return inputStream;
    }

    public static boolean closeResourceIfNotNull(Closeable resource) {
        return resource != null && closeResource(resource);
    }

    public static boolean closeResource(Closeable resource) {
        try {
            resource.close();
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
        return true;
    }

    private void loadSoundEvents() {
        soundEvents = new ArrayList<>(); // can use the size of the track for initialization - speeds up
        Sequence sequence = sequencer.getSequence();
        for (Track track : sequence.getTracks())
            processTrack(track);
    }

    private void processTrack(Track track){
        for (int i = 0; i < track.size(); i++) {
            MidiEvent midiEvent = track.get(i);
            processEvent(midiEvent);
        }
    }

    private void processEvent(MidiEvent midiEvent){
        MidiMessage midiMessage = midiEvent.getMessage();
        double duration = getDuration(midiEvent);
        if (midiMessage instanceof ShortMessage) {

            ShortMessage shortMessage = (ShortMessage) midiMessage;
            int command = shortMessage.getCommand();
            if(command == ShortMessage.NOTE_OFF);
            MusicalNote musicalNote = new MusicalNote(shortMessage, duration);
            SoundEvent soundEvent = new SoundEvent();
            soundEvent.setNote(musicalNote);
            soundEvents.add(soundEvent);
        }
    }

    public boolean saveToFile(Sequence sequence, int type, File file){
        try {
            MidiSystem.write(sequence, type, file);
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
        return true;
    }

    private double getDuration(MidiEvent midiEvent){
        long tick = midiEvent.getTick();
        double tickSize = getMidiEventTickSize(midiEvent);
        return tick * tickSize;
    }

    private double getMidiEventTickSize(MidiEvent midiEvent) {
        double resolution = sequencer.getSequence().getResolution();
        double tempo = getMidiEventTempoBPM(midiEvent);
        double ticksPerSecond = resolution * (tempo / 60.0);
        return 1.0 / ticksPerSecond;
    }

    private double getMidiEventTempoBPM(MidiEvent midiEvent) {
        int tempoMPQ = MidiUtils.getTempoMPQ(midiEvent.getMessage());
        return MidiUtils.convertTempo(tempoMPQ);
    }

    public static void main(String[] args) {
        String midiFile = "music/Eminem/thewayiam.mid";
        MidiIO midiIO = new MidiIO(midiFile);
//        midiIO.prototypeMethod1();
    }
}
