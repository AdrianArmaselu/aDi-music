package net.deepmusicio.graphmodel.utils;

import com.sun.media.sound.MidiUtils;
import net.deepmusicio.graphmodel.MusicalNote;
import net.deepmusicio.graphmodel.SoundEvent;

import javax.sound.midi.*;
import java.io.*;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Created by Adisor on 3/19/2016.
 * <p/>
 * Used http://stackoverflow.com/questions/3850688/reading-midi-files-in-java
 * Multiple types of midi files: https://forum.noteworthycomposer.com/?topic=4157.0
 * Official Java Midi API: https://docs.oracle.com/javase/tutorial/sound/MIDI-seq-intro.html
 * <p/>
 * TODO: SOME CHORDS HAVE SLIGHT DIFFERENCES IN TIMES BETWEEN NOTES
 * TODO: CAN USE CHANGES IN TEMPO FOR MODEL PREDICTION
 * TODO: PICK METAEVENTS FOR THE FINAL OUTPUT
 * TODO: Log midi file details : tracks, events, pitches, etc.
 * TODO: CONSIDER CHANGING CHANNELS OF TRACKS
 * TODO: NOT SURE IF A PITCH CAN BE REPEATED TWICE, HOW DO YOU DETERMINE DURATION IF THE MESSAGE TO TURN IT OFF IS NOT THERE
 *
 * Notes:
 * Tick Size depends on current tempo
 */

public class MidiIO {

    private static final int DEFAULT_TYPE = 1;
    private Sequencer sequencer;

    private MidiFileFormat midiFileFormat;

    public MidiIO(String midiFile) {
        openSequencer();
        setSequence(midiFile);
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

    public boolean saveToFile(Sequence sequence, int type, File file) {
        try {
            MidiSystem.write(sequence, type, file);
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
        return true;
    }

    public static void main(String[] args) {
        String midiFile = "music/Eminem/thewayiam.mid";
        MidiIO midiIO = new MidiIO(midiFile);
    }

    class SoundEventsExtractor {

        // the key is the pitch
        private Map<Integer, MidiEvent> playingEvents;
        private List<SoundEvent> soundEventsSequence;
        private Sequence sequence;

        // always in BPM
        private double currentBPMTempo;

        // in microseconds or milliseconds, idk
        private double currentTickSize;

        SoundEventsExtractor(Sequence sequence) {
            this.sequence = sequence;
            playingEvents = new HashMap<>();
            soundEventsSequence = new ArrayList<>(); // can use the size of the track for initialization - speeds up
        }

        private void extractSoundEvents() {
            for (Track track : sequence.getTracks())
                processTrack(track);
        }

        private void processTrack(Track track) {
            long previousTick = 0;
            for (int i = 0; i < track.size(); i++) {
                MidiEvent midiEvent = track.get(i);
                processEvent(midiEvent, previousTick);
                previousTick = midiEvent.getTick();
            }
        }

        private void processEvent(MidiEvent midiEvent, long previousTick) {
            MidiMessage midiMessage = midiEvent.getMessage();
            if(MidiUtils.isMetaTempo(midiMessage)) { // is it a change in tempo?
                updateTempo(midiMessage);
                updateTickSize();
            }
            if (midiMessage instanceof ShortMessage) {

                ShortMessage shortMessage = (ShortMessage) midiMessage;

                int pitch = shortMessage.getData1();
                SoundEvent soundEvent;
                if(isNotePlayStopped(shortMessage)){
                    MidiEvent playingEvent = playingEvents.get(pitch);
                    ShortMessage playingMessage = (ShortMessage) playingEvent.getMessage();
                    MusicalNote musicalNote = new MusicalNote(playingMessage);
                    double duration = computePreviousEventDuration(playingEvent, previousTick);
                    musicalNote.setDuration(duration);
                    playingEvents.remove(pitch);
                    // stuck on considering chords

                }else{
                    MusicalNote musicalNote = new MusicalNote(shortMessage);
                    boolean isNotePartOfAChord = duration == 0;
                    if (isNotePartOfAChord) {
                        soundEvent = getLastSoundEvent();
                        soundEvent.addNote(musicalNote);
                    } else {
                        soundEvent = new SoundEvent();
                        soundEvent.addNote(musicalNote);
                        soundEventsSequence.add(soundEvent);
                    }
                    playingEvents.put(pitch, midiEvent);
                }
            }
        }

        private void updateTempo(MidiMessage midiMessage){
            float mpqTempo = MidiUtils.getTempoMPQ(midiMessage);
            currentBPMTempo = MidiUtils.convertTempo(mpqTempo);
        }

        private void updateTickSize(){
            double resolution = sequencer.getSequence().getResolution();
            double ticksPerSecond = resolution * (currentBPMTempo / 60.0);
            currentTickSize =  1.0 / ticksPerSecond;
        }

        private double computePreviousEventDuration(MidiEvent currentMidiEvent, long previousTick){ // this is computed wrongly - should compute next note's tick - this one
            long deltaTick = currentMidiEvent.getTick() - previousTick;
            return deltaTick * currentTickSize;
        }

        private boolean isNotePlayStopped(ShortMessage shortMessage){
            int command = shortMessage.getCommand();
            int velocity = shortMessage.getData2();
            return command == ShortMessage.NOTE_OFF || command == ShortMessage.NOTE_ON && velocity == 0;
        }

        private SoundEvent getLastSoundEvent() {
            return soundEventsSequence.get(soundEventsSequence.size() - 1);
        }
    }
}
